"""
Extracción de series desde la Base de Datos Estadísticos (BDE) del Banco Central de Chile
usando el servicio web SieteRestWS.

Uso (desde la carpeta raíz del proyecto):
    python extraccion/E_BCCH.py                                    # descarga todas las series de SERIES
    python extraccion/E_BCCH.py --buscar "IPC"                     # busca códigos de series mensuales
    python extraccion/E_BCCH.py --buscar "operadores" --frecuencia DAILY   # busca en otra frecuencia

Todas las series se guardan en frecuencia MENSUAL: las series diarias o quincenales se
convierten a promedio mensual, para que todas queden comparables entre sí.

Las credenciales se leen desde el archivo .env (ver .env.example), que NO se sube a GitHub.
"""

import argparse
import os
import sys
import time
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
URL_API = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"
FECHA_INICIO = "2000-01-01"          # al menos 10 años de historia, según la pauta
CARPETA_SALIDA = Path("data/raw")

# Series a descargar: {nombre_corto: código BDE}
# Las series con código None están pendientes: el script las omite (sin marcar error)
# hasta que se complete su código. Para encontrarlo, usar el texto sugerido con --buscar.
SERIES = {
    # 1. Tasa de política monetaria, promedio mensual
    "tpm": "F022.TPM.TIN.D001.NO.Z.M",
    # 2. IPC general, variación mensual (%)
    "ipc": "F074.IPC.VAR.Z.Z.C.M",
    # 3. IPC SAE (sin alimentos ni energía), variación mensual (%), base 2023
    #    Verificar que cubra desde 2000; si parte en 2023, buscar la serie empalmada: --buscar "SAE"
    "ipc_sae": "F074.IPCSAE.VAR.Z.2023.C.M",
    # 4. Imacec, índice original, referencia 2018
    "imacec": "F032.IMC.IND.Z.Z.EP18.Z.Z.0.M",
    # 5. Tipo de cambio dólar observado, promedio mensual
    "dolar_observado": "F073.TCO.PRE.HIST.M",
    # 6. Expectativa de inflación a 12 meses, Encuesta de Expectativas Económicas (EEE), mediana
    "expectativa_ipc_eee": "F089.IPC.V12.14.M",
    # 7. Expectativa de inflación, Encuesta de Operadores Financieros (EOF)
    #    PENDIENTE: --buscar "operadores" --frecuencia DAILY  (la EOF es quincenal)
    "expectativa_ipc_eof": None,
    # 8a. Tasa BCP 10 años (bonos en pesos), mercado secundario. Serie diaria → promedio mensual
    "tasa_bcp_10": "F022.BCP.TIN.AN10.NO.Z.D",
    # 8b. Tasa BCU 10 años (bonos en UF), mercado secundario. Serie diaria → promedio mensual
    "tasa_bcu_10": "F022.BUF.TIS.AN10.UF.Z.D",
    # 8c. Tasa de los PDBC (pagarés descontables del Banco Central)
    #     PENDIENTE: --buscar "PDBC"  o  --buscar "descontables"
    "tasa_pdbc": None,
    # 9. Tasa de desocupación nacional (%), INE
    "desempleo": "F049.DES.TAS.INE9.10.M",
    # 10. Índice nominal de remuneraciones, INE
    #     PENDIENTE: --buscar "remuneraciones"
    "remuneraciones": None,
}


# ---------------------------------------------------------------------------
# Funciones
# ---------------------------------------------------------------------------
def cargar_credenciales():
    """Lee usuario y clave desde .env y avisa si faltan."""
    load_dotenv()
    usuario = os.getenv("BCCH_USER")
    clave = os.getenv("BCCH_PASS")
    if not usuario or not clave:
        sys.exit("ERROR: faltan BCCH_USER o BCCH_PASS en el archivo .env (ver .env.example).")
    return usuario, clave


class SinConexion(Exception):
    """No se pudo llegar al servidor del Banco Central (internet, VPN o red bloqueada)."""


def ocultar_credenciales(texto, params):
    """Reemplaza usuario y clave por *** para que nunca aparezcan en pantalla."""
    for campo in ("user", "pass"):
        valor = params.get(campo)
        if valor:
            for forma in (valor, quote_plus(valor)):
                texto = texto.replace(forma, "***")
    return texto


def llamar_api(params, reintentos=3):
    """Hace la consulta a la API con reintentos ante fallas de red."""
    for intento in range(1, reintentos + 1):
        try:
            r = requests.get(URL_API, params=params, timeout=60)
            r.raise_for_status()
            datos = r.json()
            # La API responde Codigo = 0 cuando la consulta fue exitosa
            if datos.get("Codigo") != 0:
                raise ValueError(f"API respondió: {datos.get('Descripcion')}")
            return datos
        except (requests.RequestException, ValueError) as e:
            mensaje = ocultar_credenciales(str(e), params)
            print(f"  intento {intento}/{reintentos} falló: {mensaje}")
            if intento == reintentos:
                # Sin conexión: no tiene sentido seguir con las demás series
                if isinstance(e, requests.ConnectionError):
                    raise SinConexion(mensaje) from None
                raise ValueError(mensaje) from None
            time.sleep(2 * intento)


def descargar_serie(codigo, usuario, clave, desde=FECHA_INICIO):
    """Descarga una serie y la devuelve como DataFrame con columnas fecha, valor."""
    params = {
        "user": usuario,
        "pass": clave,
        "function": "GetSeries",
        "timeseries": codigo,
        "firstdate": desde,
    }
    datos = llamar_api(params)
    obs = datos["Series"]["Obs"]
    df = pd.DataFrame(obs)
    if df.empty:
        return pd.DataFrame(columns=["fecha", "valor"])

    df["fecha"] = pd.to_datetime(df["indexDateString"], format="%d-%m-%Y")
    # Valores faltantes vienen como "NaN" con statusCode distinto de "OK"
    df["valor"] = pd.to_numeric(df["value"], errors="coerce")
    df.loc[df["statusCode"] != "OK", "valor"] = pd.NA
    return df[["fecha", "valor"]]


def a_mensual(df):
    """
    Convierte la serie a frecuencia mensual (promedio de cada mes), con fecha el día 1.
    Las series que ya son mensuales no cambian; las diarias o quincenales quedan como
    promedio mensual. Un mes sin ningún dato válido queda como faltante.
    """
    if df.empty:
        return df
    mensual = (
        df.set_index("fecha")["valor"]
        .astype(float)
        .resample("MS")
        .mean()
        .reset_index()
    )
    return mensual[["fecha", "valor"]]


def buscar_series(texto, usuario, clave, frecuencia="MONTHLY"):
    """Muestra las series del catálogo cuyo título contiene el texto buscado."""
    params = {"user": usuario, "pass": clave, "function": "SearchSeries", "frequency": frecuencia}
    catalogo = pd.DataFrame(llamar_api(params)["SeriesInfos"])
    filtro = catalogo["spanishTitle"].str.contains(texto, case=False, na=False)
    resultado = catalogo.loc[filtro, ["seriesId", "spanishTitle", "firstObservation", "lastObservation"]]
    pd.set_option("display.max_colwidth", 90)
    print(resultado.to_string(index=False) if not resultado.empty else "Sin resultados.")


def main():
    parser = argparse.ArgumentParser(description="Extrae series de la BDE del Banco Central.")
    parser.add_argument("--buscar", help="texto a buscar en el catálogo de series")
    parser.add_argument(
        "--frecuencia",
        default="MONTHLY",
        choices=["DAILY", "MONTHLY", "QUARTERLY", "ANNUAL"],
        help="frecuencia del catálogo en que se busca (por defecto MONTHLY)",
    )
    args = parser.parse_args()

    usuario, clave = cargar_credenciales()

    if args.buscar:
        buscar_series(args.buscar, usuario, clave, args.frecuencia)
        return

    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    errores = []
    pendientes = []
    for nombre, codigo in SERIES.items():
        if codigo is None:
            print(f"Omitiendo {nombre}: código pendiente (ver comentario en SERIES).")
            pendientes.append(nombre)
            continue

        print(f"Descargando {nombre} ({codigo})...")
        try:
            df = a_mensual(descargar_serie(codigo, usuario, clave))
            df["serie"] = nombre
            df["codigo"] = codigo
            df.to_csv(CARPETA_SALIDA / f"{nombre}.csv", index=False)
            print(f"  OK: {len(df)} meses, {df['valor'].isna().sum()} faltantes, "
                  f"desde {df['fecha'].min():%Y-%m} hasta {df['fecha'].max():%Y-%m}")
        except SinConexion:
            sys.exit("\nERROR: no hay conexión con si3.bcentral.cl. Revisa tu internet "
                     "(o desactiva la VPN) e intenta de nuevo. No se descargó nada más.")
        except Exception as e:
            print(f"  ERROR en {nombre}: {e}")
            errores.append(nombre)

    if pendientes:
        print(f"\nSeries pendientes de código: {', '.join(pendientes)}")
    if errores:
        print(f"\nTerminado con errores en: {', '.join(errores)}")
        sys.exit(1)
    print("\nTodas las series con código se descargaron correctamente.")


if __name__ == "__main__":
    main()