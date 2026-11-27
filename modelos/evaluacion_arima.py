"""
evaluacion_arima.py
-------------------
evaluación fuera de muestra del ARIMA contra la caminata aleatoria.

Pregunta: ¿el ARIMA pronostica la TPM mejor que el benchmark ingenuo
"la TPM futura es igual a la última observada" (caminata aleatoria)?

Diseño (sin sesgo de anticipación):
  - Período de evaluación: enero de 2025 a septiembre de 2026, el mismo que usa
    la regla de Taylor (Persona 2), para que todos los modelos se comparen igual.
  - Ventana expansiva: para pronosticar un mes, el modelo se re-estima SOLO con los
    datos disponibles hasta el momento del pronóstico. Nunca ve el dato que pronostica.
  - El orden (p, d, q) se elige UNA vez con el período de entrenamiento
    (hasta 2024-12) y se mantiene fijo: elegirlo mirando el período de evaluación
    sería hacer trampa.
  - Horizontes de 1, 6 y 12 meses: pronosticar el mes siguiente es fácil (la TPM
    cambia poco); la pregunta del proyecto es a 6-24 meses.

Se comparan dos versiones del ARIMA:
  - d = 1: modela el CAMBIO de la TPM (lo que eligió arima_tpm.py por AIC).
  - d = 0: modela el NIVEL, como sugiere el test ADF (p = 0,008).
Así la decisión de diferenciar queda respaldada con evidencia fuera de muestra.

Métricas (en puntos porcentuales de TPM):
  - MAE: error absoluto promedio.
  - RMSE: raíz del error cuadrático medio; castiga más los errores grandes.
  - R² OOS vs caminata aleatoria = 1 - ECM_modelo / ECM_caminata.
    Positivo: el modelo le gana al benchmark. Negativo: no le gana.

Uso (desde la raíz del proyecto):
    python modelos/evaluacion_arima.py
Resultados:
    hito_3/resultados/evaluacion_arima_metricas.csv
    hito_3/resultados/evaluacion_arima_detalle.csv
    hito_3/graficos/evaluacion_arima.png
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from modelos.arima_tpm import FIN_ENTRENAMIENTO, cargar_tpm, elegir_orden  # noqa: E402

INICIO_EVALUACION = "2025-01-01"
FIN_EVALUACION = "2026-09-01"
HORIZONTES = [1, 6, 12]


def pronosticos_fuera_de_muestra(tpm: pd.Series, ordenes: dict, horizonte: int) -> pd.DataFrame:
    """
    Para cada mes objetivo del período de evaluación, se pronostica con los datos
    disponibles 'horizonte' meses antes. Devuelve una fila por mes objetivo con el
    valor observado y el pronóstico de cada modelo.
    """
    objetivos = tpm.loc[INICIO_EVALUACION:FIN_EVALUACION].index
    filas = []
    for objetivo in objetivos:
        # Último mes con dato al momento de pronosticar (el "origen" del pronóstico)
        origen = objetivo - pd.DateOffset(months=horizonte)
        historia = tpm.loc[:origen]                # solo pasado: no mira el futuro

        fila = {"mes_objetivo": objetivo, "horizonte": horizonte,
                "origen": origen, "observado": tpm.loc[objetivo],
                "Caminata aleatoria": historia.iloc[-1]}
        for nombre, orden in ordenes.items():
            ajuste = ARIMA(historia, order=orden).fit()
            fila[nombre] = float(np.asarray(ajuste.forecast(steps=horizonte))[-1])
        filas.append(fila)
    return pd.DataFrame(filas)


def metricas(detalle: pd.DataFrame, modelos: list[str]) -> pd.DataFrame:
    """MAE, RMSE y R² OOS frente a la caminata aleatoria, por horizonte y modelo."""
    filas = []
    for horizonte, grupo in detalle.groupby("horizonte"):
        ecm_caminata = ((grupo["observado"] - grupo["Caminata aleatoria"]) ** 2).mean()
        for modelo in modelos:
            error = grupo["observado"] - grupo[modelo]
            ecm = (error ** 2).mean()
            filas.append({
                "horizonte_meses": horizonte,
                "modelo": modelo,
                "MAE": error.abs().mean(),
                "RMSE": np.sqrt(ecm),
                # Si la caminata tiene error cero (TPM sin cambios), el R² no se puede calcular
                "R2_OOS_vs_caminata": np.nan if ecm_caminata == 0 else 1 - ecm / ecm_caminata,
                "meses_evaluados": len(grupo),
            })
    return pd.DataFrame(filas)


def graficar(tpm: pd.Series, detalle: pd.DataFrame, modelos: list[str], ruta: Path) -> None:
    """Un panel por horizonte: TPM efectiva vs pronósticos de cada modelo."""
    fig, ejes = plt.subplots(1, len(HORIZONTES), figsize=(15, 4.2), sharey=True)
    contexto = tpm.loc[pd.Timestamp(INICIO_EVALUACION) - pd.DateOffset(months=12):FIN_EVALUACION]
    estilos = {"Caminata aleatoria": ("--", "#7f7f7f")}
    colores = ["#1f77b4", "#d62728", "#2ca02c"]

    for eje, horizonte in zip(ejes, HORIZONTES):
        grupo = detalle[detalle["horizonte"] == horizonte].set_index("mes_objetivo")
        eje.plot(contexto.index, contexto, color="black", lw=2, label="TPM efectiva")
        for i, modelo in enumerate(modelos):
            linea, color = estilos.get(modelo, ("-", colores[i % len(colores)]))
            eje.plot(grupo.index, grupo[modelo], linea, color=color, lw=1.5, label=modelo)
        eje.axvline(pd.Timestamp(INICIO_EVALUACION), color="grey", lw=0.8, ls=":")
        eje.set_title(f"Pronóstico a {horizonte} mes{'es' if horizonte > 1 else ''}")
        eje.tick_params(axis="x", rotation=45)
    ejes[0].set_ylabel("TPM (% anual)")
    ejes[0].legend(fontsize=8)
    fig.suptitle("Evaluación fuera de muestra de la TPM, ene-2025 a sep-2026 "
                 "(ventana expansiva). Fuente: BCCh, base del proyecto.", fontsize=10)
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    tpm = cargar_tpm()
    entrenamiento = tpm.loc[:FIN_ENTRENAMIENTO]

    # Órdenes elegidos UNA vez, solo con el entrenamiento
    orden_d1, _ = elegir_orden(entrenamiento, d=1)
    orden_d0, _ = elegir_orden(entrenamiento, d=0)
    ordenes = {f"ARIMA{orden_d1}": orden_d1, f"ARIMA{orden_d0}": orden_d0}
    modelos = ["Caminata aleatoria"] + list(ordenes)
    print("Modelos elegidos con datos hasta", FIN_ENTRENAMIENTO[:7], "->", ", ".join(ordenes))
    print("Evaluando (re-estima el modelo para cada mes; demora alrededor de un minuto)...\n")

    detalle = pd.concat([pronosticos_fuera_de_muestra(tpm, ordenes, h) for h in HORIZONTES],
                        ignore_index=True)
    tabla = metricas(detalle, modelos)

    carpeta_res = RAIZ / "hito_3" / "resultados"
    carpeta_graf = RAIZ / "hito_3" / "graficos"
    carpeta_res.mkdir(parents=True, exist_ok=True)
    carpeta_graf.mkdir(parents=True, exist_ok=True)
    tabla.round(4).to_csv(carpeta_res / "evaluacion_arima_metricas.csv", index=False)
    detalle.round(4).to_csv(carpeta_res / "evaluacion_arima_detalle.csv", index=False)
    graficar(tpm, detalle, modelos, carpeta_graf / "evaluacion_arima.png")

    print("Errores fuera de muestra (puntos porcentuales de TPM):\n")
    print(tabla.round(3).to_string(index=False))
    print("\nLectura: R² OOS > 0 significa que el modelo le gana a la caminata aleatoria.")
    print("Archivos guardados en hito_3/resultados y hito_3/graficos")