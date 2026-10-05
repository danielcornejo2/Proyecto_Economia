"""
Extracción de series desde la Base de Datos Estadísticos (BDE) del Banco Central de Chile
usando el servicio web SieteRestWS.
 
Uso (desde la carpeta raíz del proyecto):
    python extraccion/extraer_bcch.py                 # descarga todas las series de SERIES
    python extraccion/extraer_bcch.py --buscar "IPC"  # busca códigos de series mensuales
 
Las credenciales se leen desde el archivo .env (ver .env.example), que NO se sube a GitHub.
"""
 
import argparse
import os
import sys
import time
from pathlib import Path
 
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
# TPM y dólar observado (mensuales) ya están verificados.
# Completen el resto con los códigos que encuentren usando --buscar.
SERIES = {
    "tpm": "F022.TPM.TIN.D001.NO.Z.M",          # Tasa de política monetaria, promedio mensual
    "dolar_observado": "F073.TCO.PRE.Z.M",      # Tipo de cambio dólar observado, promedio mensual
    # "ipc": "COMPLETAR",
    # "imacec": "COMPLETAR",
    # "desempleo": "COMPLETAR",
    # ...
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
            print(f"  intento {intento}/{reintentos} falló: {e}")
            if intento == reintentos:
                raise
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
    parser.add_argument("--buscar", help="texto a buscar en el catálogo de series mensuales")
    args = parser.parse_args()
 
    usuario, clave = cargar_credenciales()
 
    if args.buscar:
        buscar_series(args.buscar, usuario, clave)
        return
 
    CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    errores = []
    for nombre, codigo in SERIES.items():
        print(f"Descargando {nombre} ({codigo})...")
        try:
            df = descargar_serie(codigo, usuario, clave)
            df["serie"] = nombre
            df["codigo"] = codigo
            df.to_csv(CARPETA_SALIDA / f"{nombre}.csv", index=False)
            print(f"  OK: {len(df)} observaciones, {df['valor'].isna().sum()} faltantes, "
                  f"desde {df['fecha'].min():%Y-%m} hasta {df['fecha'].max():%Y-%m}")
        except Exception as e:
            print(f"  ERROR en {nombre}: {e}")
            errores.append(nombre)
 
    if errores:
        print(f"\nTerminado con errores en: {', '.join(errores)}")
        sys.exit(1)
    print("\nTodas las series se descargaron correctamente.")
 
 
if __name__ == "__main__":
    main()