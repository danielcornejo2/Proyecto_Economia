"""
ejecutar_todo.py
----------------
Corre el proyecto completo de punta a punta con un solo comando:

    python ejecutar_todo.py

Orden:
  1. carga.py                   descarga las series (BCCh y FRED) y crea data/base.db
  2. Relaciones                 correlaciones y rezagos de la TPM
  3. ARIMA                      selección del modelo y evaluación fuera de muestra
  4. Regla de Taylor            estimación, evaluación, horizontes y proyección
  5. Gráficos de Taylor
  6. Comparación de modelos     tabla única Taylor vs ARIMA vs caminata aleatoria

Cada script se corre como módulo (python -m modelos.xxx) desde la raíz del
proyecto, así los "from modelos... import ..." funcionan siempre.
Si un paso falla, se detiene y muestra cuál fue: los pasos siguientes dependen
de los anteriores.

Opción: python ejecutar_todo.py --sin-descarga
    Omite carga.py y usa la base ya existente (útil si no hay internet o
    si la base ya está creada).
"""

import subprocess
import sys
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent

PASOS = [
    ("Descarga de datos y creación de la base", ["carga.py"]),
    ("Correlaciones y rezagos",                  ["-m", "modelos.correlaciones_tpm"]),
    ("Selección del ARIMA",                      ["-m", "modelos.arima_tpm"]),
    ("Evaluación fuera de muestra del ARIMA",    ["-m", "modelos.evaluacion_arima"]),
    ("Regla de Taylor: evaluación",              ["-m", "modelos.evaluacion_taylor"]),
    ("Regla de Taylor: validación temporal",     ["-m", "modelos.validacion_temporal"]),
    ("Regla de Taylor: horizontes 6-12-24",      ["-m", "modelos.evaluacion_horizontes"]),
    ("Regla de Taylor: significancia (HAC)",     ["-m", "modelos.significancia_taylor"]),
    ("Regla de Taylor: proyección a 24 meses",   ["-m", "modelos.proyeccion_taylor"]),
    ("Gráfico de comparación de Taylor",         ["-m", "modelos.grafico_taylor"]),
    ("Gráfico de proyección de Taylor",          ["-m", "modelos.grafico_proyeccion_taylor"]),
    ("Comparación de modelos",                   ["-m", "modelos.comparacion_modelos"]),
    ("Proyección con escenarios y carga a la base", ["-m", "modelos.proyeccion_escenarios"]),
]


def main():
    pasos = PASOS[1:] if "--sin-descarga" in sys.argv else PASOS
    if not (RAIZ / "data" / "base.db").exists() and pasos is not PASOS:
        sys.exit("No existe data/base.db: corre primero sin --sin-descarga.")

    inicio = time.time()
    for numero, (nombre, argumentos) in enumerate(pasos, start=1):
        print(f"\n{'=' * 70}\n[{numero}/{len(pasos)}] {nombre}\n{'=' * 70}")
        resultado = subprocess.run([sys.executable, *argumentos], cwd=RAIZ)
        if resultado.returncode != 0:
            sys.exit(f"\n[ERROR] Falló el paso {numero}: {nombre}. Revisa el mensaje de arriba.")

    minutos = (time.time() - inicio) / 60
    print(f"\n[OK] Proyecto completo ejecutado en {minutos:.1f} minutos. "
          "Resultados en hito_3/resultados y gráficos en hito_3/graficos.")


if __name__ == "__main__":
    main()