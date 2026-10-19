
import argparse
import os
import sys
import time
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import requests
from dotenv import load_dotenv


# Configuración

URL_API = "https://si3.bcentral.cl/SieteRestWS/SieteRestWS.ashx"
FECHA_INICIO = "2000-01-01"          # al menos 10 años de historia, según la pauta
RAIZ = Path(__file__).resolve().parent.parent      # carpeta raíz del proyecto
CARPETA_SALIDA = RAIZ / "data" / "raw" / "bcch"    # cada fuente tiene su propia carpeta


SERIES = {
    # 1. Tasa de política monetaria, promedio mensual
    #    Variable objetivo del proyecto.
    "tpm": "F022.TPM.TIN.D001.NO.Z.M",
    # 2. IPC general, variación mensual (%)
    #    Por qué: si la inflación se aleja de la meta de 3 %, el BCCh ajusta la TPM
    #    en la misma dirección (signo +). Se publica con rezago: usar rezagada.
    "ipc": "F074.IPC.VAR.Z.Z.C.M",
    # 3. IPC SAE (sin alimentos ni energía), variación mensual (%), serie empalmada
    #    por el INE (base 2023 = 100). Disponible desde 2010-01.
    #    Por qué: inflación subyacente; muestra si las presiones de precios son
    #    persistentes (signo +).
    "ipc_sae": "F074.IPCSAE.VAR.Z.EP23.Z.M",
    # 4. Imacec, índice original, referencia 2018
    #    Por qué: con el filtro HP se obtiene la brecha de actividad de la regla de
    #    Taylor; actividad sobre su potencial presiona la inflación (signo +).
    "imacec": "F032.IMC.IND.Z.Z.EP18.Z.Z.0.M",
    # 5. Tipo de cambio dólar observado, promedio mensual
    #    Por qué: canal cambiario; una depreciación del peso encarece los bienes
    #    importados y sube la inflación (signo +).
    "dolar_observado": "F073.TCO.PRE.HIST.M",
    # 6. Expectativa de inflación a 12 meses, Encuesta de Expectativas Económicas (EEE), mediana
    #    Por qué: la regla de Taylor responde a la inflación esperada; expectativas
    #    sobre 3 % anticipan alzas de la TPM (signo +).
    "expectativa_ipc_eee": "F089.IPC.V12.14.M",
    # 7a. Tasa de interés de mercado secundario, bonos en pesos a 10 años (BCP/BTP).
    #     Serie diaria → promedio mensual. Reemplaza a la tasa de licitación BCP,
    #     que se dejó de publicar en 2013.
    #     Por qué: refleja las expectativas del mercado sobre tasas e inflación
    #     futuras (canal de tasas de mercado).
    "tasa_bcp_10": "F022.BCLP.TIS.AN10.NO.Z.D",
    # 7b. Tasa BCU 10 años (bonos en UF), mercado secundario. Serie diaria → promedio mensual
    #     Por qué: tasa real de largo plazo; muestra cómo se transmite la TPM a las
    #     tasas de crédito.
    "tasa_bcu_10": "F022.BUF.TIS.AN10.UF.Z.D",
    # 7c. Tasa de depósitos en bolsa a 90 días, en pesos, mercado secundario.
    #     Serie diaria → promedio mensual. Disponible desde 2007-02.
    #     Reemplaza a la tasa de los PDBC: sus tasas a 30 y 90 días se dejaron de
    #     licitar y la de 14 días solo existe desde 2024.
    #     Por qué: tasa de corto plazo del mercado monetario; incorpora lo que se
    #     espera de la TPM en los próximos meses (signo +, adelanta).
    "tasa_depositos_90d": "F022.TDB.TIS.D090.NO.Z.D",
    # 8. Tasa de desocupación nacional (%), INE
    #    Por qué: mide la holgura del mercado laboral; más desempleo implica menos
    #    presión salarial e inflacionaria (signo −).
    "desempleo": "F049.DES.TAS.INE9.10.M",
}


def cargar_credenciales():
    """Lee usuario y clave desde .env y avisa si faltan."""
    load_dotenv(RAIZ / ".env")
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

def leer_fecha_corte(texto):
    """
    Convierte la fecha de corte escrita como 'AAAA-MM-DD' en una fecha de pandas.
    Si no se indicó fecha, devuelve None (se descarga hasta el último dato).
    Si el formato es incorrecto, detiene el script con un mensaje claro.
    """
    if texto is None:
        return None
    try:
        return pd.to_datetime(texto, format="%Y-%m-%d")
    except ValueError:
        sys.exit(f"ERROR: la fecha de corte '{texto}' no tiene el formato AAAA-MM-DD "
                 "(ejemplo: 2026-09-30).")

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
    parser.add_argument(
        "--hasta",
        help="fecha de corte AAAA-MM-DD: se descartan los datos posteriores a esa fecha",
    )
    args = parser.parse_args()
    hasta = leer_fecha_corte(args.hasta)

    usuario, clave = cargar_credenciales()

    if args.buscar:
        buscar_series(args.buscar, usuario, clave, args.frecuencia)
        return

    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    if hasta is not None:
        print(f"Fecha de corte: {hasta:%Y-%m-%d} (se descartan los datos posteriores).")
    else:
        print("Sin fecha de corte: se descarga hasta el último dato disponible.")
    errores = []
    pendientes = []
    for nombre, codigo in SERIES.items():
        if codigo is None:
            print(f"Omitiendo {nombre}: código pendiente (ver comentario en SERIES).")
            pendientes.append(nombre)
            continue

        print(f"Descargando {nombre} ({codigo})...")
        try:
            df = descargar_serie(codigo, usuario, clave)
            if hasta is not None:
                df = df[df["fecha"] <= hasta]   
            df = a_mensual(df)
            if df.empty:
                raise ValueError("no hay datos hasta la fecha de corte")
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