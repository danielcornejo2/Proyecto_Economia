"""
Extracción de series desde FRED (Federal Reserve Economic Data, Reserva Federal de St. Louis)
usando su API oficial.

Uso (desde la carpeta raíz del proyecto):
    python extraccion/E_FRED.py                       # descarga todas las series de SERIES
    python extraccion/E_FRED.py --buscar "copper"     # busca códigos de series (en inglés)

Todas las series se guardan en frecuencia MENSUAL: las series diarias se convierten a
promedio mensual, igual que en E_BCCH.py, para que todas queden comparables entre sí.
Los CSV quedan en data/raw/fred/ (los del Banco Central van aparte, en data/raw/bcch/).

La API key se lee desde el archivo .env (variable FRED_API_KEY, ver .env.example),
que NO se sube a GitHub. Se obtiene gratis en https://fred.stlouisfed.org/docs/api/api_key.html
"""

import argparse
import os
import re
import sys
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
URL_API = "https://api.stlouisfed.org/fred"
FECHA_INICIO = "2000-01-01"          # mismo inicio que las series del Banco Central
RAIZ = Path(__file__).resolve().parent.parent      # carpeta raíz del proyecto
CARPETA_SALIDA = RAIZ / "data" / "raw" / "fred"    # cada fuente tiene su propia carpeta

# Series a descargar: {nombre_corto: código FRED}
# Los nombres deben ser distintos a los de E_BCCH.py, porque el notebook junta ambas fuentes.
# Las series con código None se omiten (sin marcar error) hasta que se complete su código.
SERIES = {
    # 11. Precio internacional del cobre (FMI), dólares por tonelada métrica, mensual
    "precio_cobre": "PCOPPUSDM",
    # 12. Tasa de fondos federales (Fed Funds Rate), promedio mensual (%)
    "fed_funds": "FEDFUNDS",
    # 13a. IPC de EE.UU. (todos los consumidores urbanos), índice 1982-84=100, desestacionalizado
    "ipc_eeuu": "CPIAUCSL",
    # 13b. Índice de producción industrial de EE.UU., índice 2017=100, desestacionalizado
    "produccion_industrial_eeuu": "INDPRO",
}


def cargar_api_key():
    """Lee la API key de FRED desde .env y avisa si falta o no tiene el formato correcto."""
    load_dotenv(RAIZ / ".env")
    api_key = (os.getenv("FRED_API_KEY") or "").strip()
    if not api_key:
        sys.exit("ERROR: falta FRED_API_KEY en el archivo .env (ver .env.example). "
                 "Se obtiene gratis en https://fred.stlouisfed.org/docs/api/api_key.html")
    # Las API keys de FRED tienen exactamente 32 caracteres en minúscula (letras y números)
    if not re.fullmatch(r"[a-z0-9]{32}", api_key):
        sys.exit("ERROR: FRED_API_KEY en .env no tiene el formato de una API key de FRED "
                 "(32 letras minúsculas y números). Revisa que la copiaste completa, sin "
                 "comillas ni espacios.")
    return api_key


class SinConexion(Exception):
    """No se pudo llegar al servidor de FRED (internet, VPN o red bloqueada)."""


class ErrorDefinitivo(Exception):
    """Error que no se arregla reintentando: API key inválida o serie inexistente."""


def ocultar_credenciales(texto, params):
    """Reemplaza la API key por *** para que nunca aparezca en pantalla."""
    valor = params.get("api_key")
    if valor:
        texto = texto.replace(valor, "***")
    return texto


def mensaje_de_error(respuesta):
    """FRED explica cada error en el campo "error_message" de su respuesta."""
    try:
        detalle = respuesta.json().get("error_message", "")
    except ValueError:
        detalle = ""
    return f"API respondió ({respuesta.status_code}): {detalle or respuesta.reason}"


def llamar_api(endpoint, params, reintentos=3):
    """Hace la consulta a la API con reintentos ante fallas de red."""
    params = {**params, "file_type": "json"}
    for intento in range(1, reintentos + 1):
        try:
            r = requests.get(f"{URL_API}/{endpoint}", params=params, timeout=60)
            # 400 y 404 (key inválida, serie inexistente) no se arreglan reintentando
            if r.status_code in (400, 404):
                raise ErrorDefinitivo(ocultar_credenciales(mensaje_de_error(r), params))
            if r.status_code != 200:
                raise ValueError(mensaje_de_error(r))
            return r.json()
        except (requests.RequestException, ValueError) as e:
            mensaje = ocultar_credenciales(str(e), params)
            print(f"  intento {intento}/{reintentos} falló: {mensaje}")
            if intento == reintentos:
                # Sin conexión: no tiene sentido seguir con las demás series
                if isinstance(e, requests.ConnectionError):
                    raise SinConexion(mensaje) from None
                raise ValueError(mensaje) from None
            # Si FRED pide bajar el ritmo (error 429), se espera más antes de reintentar
            time.sleep(20 if "(429)" in mensaje else 2 * intento)


def descargar_serie(codigo, api_key, desde=FECHA_INICIO):
    """Descarga una serie y la devuelve como DataFrame con columnas fecha, valor."""
    params = {
        "api_key": api_key,
        "series_id": codigo,
        "observation_start": desde,
    }
    datos = llamar_api("series/observations", params)
    df = pd.DataFrame(datos.get("observations", []))
    if df.empty:
        return pd.DataFrame(columns=["fecha", "valor"])

    df["fecha"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    # FRED marca los valores faltantes con un punto ".": se convierten en faltantes
    df["valor"] = pd.to_numeric(df["value"], errors="coerce")
    return df[["fecha", "valor"]]


def a_mensual(df):
    """
    Convierte la serie a frecuencia mensual (promedio de cada mes), con fecha el día 1.
    Las series que ya son mensuales no cambian; las diarias quedan como promedio mensual.
    Un mes sin ningún dato válido queda como faltante.
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


def buscar_series(texto, api_key):
    """Muestra las series de FRED que coinciden con el texto buscado (en inglés)."""
    params = {
        "api_key": api_key,
        "search_text": texto,
        "order_by": "popularity",
        "sort_order": "desc",
        "limit": 20,
    }
    catalogo = pd.DataFrame(llamar_api("series/search", params).get("seriess", []))
    if catalogo.empty:
        print("Sin resultados.")
        return
    columnas = ["id", "title", "frequency_short", "units_short", "observation_start", "observation_end"]
    pd.set_option("display.max_colwidth", 70)
    print(catalogo[columnas].to_string(index=False))


def main():
    parser = argparse.ArgumentParser(description="Extrae series de FRED (Reserva Federal de St. Louis).")
    parser.add_argument("--buscar", help="texto a buscar en el catálogo de FRED (en inglés)")
    args = parser.parse_args()

    api_key = cargar_api_key()

    if args.buscar:
        buscar_series(args.buscar, api_key)
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
            df = a_mensual(descargar_serie(codigo, api_key))
            if df.empty:
                raise ValueError("la API no devolvió observaciones")
            df["serie"] = nombre
            df["codigo"] = codigo
            df.to_csv(CARPETA_SALIDA / f"{nombre}.csv", index=False)
            print(f"  OK: {len(df)} meses, {df['valor'].isna().sum()} faltantes, "
                  f"desde {df['fecha'].min():%Y-%m} hasta {df['fecha'].max():%Y-%m}")
        except SinConexion:
            sys.exit("\nERROR: no hay conexión con api.stlouisfed.org. Revisa tu internet "
                     "(o desactiva la VPN) e intenta de nuevo. No se descargó nada más.")
        except Exception as e:
            print(f"  ERROR en {nombre}: {e}")
            errores.append(nombre)
            # Si la API key no es válida, fallarán todas las series: se avisa y se detiene
            if "api_key" in str(e):
                sys.exit("\nERROR: FRED rechazó la API key. Revisa FRED_API_KEY en tu archivo .env.")

    if pendientes:
        print(f"\nSeries pendientes de código: {', '.join(pendientes)}")
    if errores:
        print(f"\nTerminado con errores en: {', '.join(errores)}")
        sys.exit(1)
    print("\nTodas las series con código se descargaron correctamente.")


if __name__ == "__main__":
    main()
