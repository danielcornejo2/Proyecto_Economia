
import argparse
import logging
import sys
from pathlib import Path

import pandas as pd

sys.dont_write_bytecode = True
RAIZ = Path(__file__).resolve().parent
sys.path.append(str(RAIZ / "extraccion"))
sys.path.append(str(RAIZ / "bd"))

import E_BCCH
import E_FRED
import crear_base

FECHA_CORTE = "2026-09-30"   # fecha de corte del proyecto (anotada en el README)


def descargar_fuente(modulo, descargar, hasta):
    """
    Descarga todas las series de una fuente (E_BCCH o E_FRED), descarta los datos
    posteriores a la fecha de corte y guarda un CSV por serie en data/raw/.
    Devuelve la lista de series que fallaron.
    """
    modulo.CARPETA_SALIDA.mkdir(parents=True, exist_ok=True)
    errores = []

    for nombre, codigo in modulo.SERIES.items():
        try:
            df = descargar(codigo)
            df = df[df["fecha"] <= hasta]      # se descartan los datos posteriores al corte
            df = modulo.a_mensual(df)          # series diarias -> promedio mensual
            if df.empty:
                raise ValueError("la API no devolvió datos hasta la fecha de corte")

            df["serie"] = nombre
            df["codigo"] = codigo
            df.to_csv(modulo.CARPETA_SALIDA / f"{nombre}.csv", index=False)
            print(f"  [OK] {nombre}: {len(df)} meses, {df['valor'].isna().sum()} sin dato, "
                  f"desde {df['fecha'].min():%Y-%m} hasta {df['fecha'].max():%Y-%m}")

        except (E_BCCH.SinConexion, E_FRED.SinConexion):
            sys.exit("\n[ERROR] No hay conexión a internet con la API. Revisa tu red (o la VPN) "
                     "e intenta de nuevo.")
        except Exception as e:
            print(f"  [ERROR] {nombre}: {e}")
            errores.append(nombre)

    return errores


def main():
    parser = argparse.ArgumentParser(description="Descarga las series y crea la base de datos.")
    parser.add_argument("--hasta", default=FECHA_CORTE,
                        help=f"fecha de corte AAAA-MM-DD (por defecto {FECHA_CORTE})")
    args = parser.parse_args()

    try:
        hasta = pd.to_datetime(args.hasta, format="%Y-%m-%d")
    except ValueError:
        sys.exit(f"[ERROR] La fecha de corte '{args.hasta}' debe tener el formato AAAA-MM-DD.")
    print(f"Fecha de corte: {hasta:%Y-%m-%d}")

    # 1) Banco Central de Chile
    print("\n1) Descargando series del Banco Central de Chile...")
    usuario, clave = E_BCCH.cargar_credenciales()
    errores = descargar_fuente(E_BCCH, lambda codigo: E_BCCH.descargar_serie(codigo, usuario, clave), hasta)

    # 2) FRED
    print("\n2) Descargando series de FRED...")
    api_key = E_FRED.cargar_api_key()
    errores += descargar_fuente(E_FRED, lambda codigo: E_FRED.descargar_serie(codigo, api_key), hasta)

    # Si falló alguna serie, no se crea la base: quedaría con CSV de una descarga anterior
    if errores:
        sys.exit(f"\n[ERROR] Fallaron estas series: {', '.join(errores)}. No se creó la base.")

    # 3) Base de datos
    print("\n3) Creando la base de datos...")
    logging.basicConfig(level=logging.INFO, format="  %(message)s", stream=sys.stdout)
    problemas = crear_base.construir_base(crear_base.CARPETA_DATOS, crear_base.RUTA_BASE)
    crear_base.mostrar_resumen(crear_base.RUTA_BASE)

    if problemas:
        print("\nProblemas encontrados:")
        for problema in problemas:
            print(f"  [ERROR] {problema}")
        sys.exit(1)

    print(f"\n[OK] Carga completa: {len(E_BCCH.SERIES) + len(E_FRED.SERIES)} series "
          f"con fecha de corte {hasta:%Y-%m-%d} en {crear_base.RUTA_BASE.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()