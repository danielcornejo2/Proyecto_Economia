"""
comparacion_modelos.py
----------------------
tabla única que compara los tres modelos de la TPM en el MISMO diseño:
regla de Taylor, ARIMA y caminata aleatoria (benchmark).

Diseño (el mismo de modelos/evaluacion_horizontes.py, para que las cifras calcen):
  - Cortes: septiembre de cada año entre 2016 y 2024.
  - En cada corte, cada modelo se estima SOLO con los datos hasta ese mes y
    pronostica la TPM a 6, 12 y 24 meses.
  - Regla de Taylor: misma especificación y misma forma de proyectar que
    evaluacion_horizontes.py (las explicativas se mantienen en su valor del corte
    y la TPM proyectada alimenta el rezago del mes siguiente).
  - ARIMA: el orden se elige con datos hasta el PRIMER corte (2016-09) y se
    mantiene fijo; en cada corte se re-estiman los coeficientes.
  - Caminata aleatoria: la TPM futura es igual a la TPM del corte.

Métricas (puntos porcentuales de TPM): MAE, RMSE y R² OOS frente a la caminata
aleatoria (positivo = le gana al benchmark).

Limitación: son 9 cortes por horizonte (pocos datos), y a 24 meses el último corte
con dato observado es 2024-09. Los resultados orientan, no son concluyentes.

Uso (desde la raíz del proyecto):
    python -m modelos.comparacion_modelos
Resultados:
    salidas/resultados/comparacion_modelos_resumen.csv
    salidas/resultados/comparacion_modelos_detalle.csv
    salidas/graficos/comparacion_modelos_rmse.png
"""

from __future__ import annotations

import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from modelos.arima_tpm import elegir_orden  # noqa: E402
from modelos.datos_modelo import armar_panel  # noqa: E402
from modelos.regla_taylor import estimar_regla_taylor  # noqa: E402

warnings.filterwarnings("ignore")

CORTES = [pd.Timestamp(f"{anio}-09-01") for anio in range(2016, 2025)]
HORIZONTES = [6, 12, 24]
VARIABLES_FIJAS = ["brecha_inflacion_esp", "brecha_actividad", "fed_funds"]
MODELOS = ["Caminata aleatoria", "Regla de Taylor", "ARIMA"]


def pronostico_taylor(panel: pd.DataFrame, corte: pd.Timestamp, pasos: int) -> list[float]:
    """Trayectoria de la regla de Taylor estimada hasta el corte (igual que evaluacion_horizontes.py)."""
    coef, _ = estimar_regla_taylor(panel, corte.strftime("%Y-%m-%d"))
    ultimo = panel.loc[corte]
    fijo = float(coef["constante"]) + sum(float(coef[v] * ultimo[v]) for v in VARIABLES_FIJAS)
    tpm, trayectoria = float(ultimo["tpm"]), []
    for _ in range(pasos):
        tpm = fijo + float(coef["tpm_lag1"]) * tpm
        trayectoria.append(tpm)
    return trayectoria


def pronostico_arima(tpm: pd.Series, corte: pd.Timestamp, orden: tuple, pasos: int) -> list[float]:
    """Trayectoria del ARIMA re-estimado con la TPM hasta el corte."""
    ajuste = ARIMA(tpm.loc[:corte], order=orden).fit()
    return [float(x) for x in np.asarray(ajuste.forecast(steps=pasos))]


def evaluar(panel: pd.DataFrame) -> tuple[pd.DataFrame, tuple]:
    tpm = panel["tpm"].asfreq("MS")
    orden, _ = elegir_orden(tpm.loc[:CORTES[0]])      # solo datos hasta el primer corte
    filas = []
    for corte in CORTES:
        if corte not in panel.index:
            continue
        pasos = max(HORIZONTES)
        taylor = pronostico_taylor(panel, corte, pasos)
        arima = pronostico_arima(tpm, corte, orden, pasos)
        for h in HORIZONTES:
            objetivo = corte + pd.DateOffset(months=h)
            if objetivo not in tpm.index or pd.isna(tpm.loc[objetivo]):
                continue
            filas.append({"corte": corte.strftime("%Y-%m"), "horizonte": h,
                          "mes_objetivo": objetivo.strftime("%Y-%m"),
                          "tpm_real": tpm.loc[objetivo],
                          "Caminata aleatoria": tpm.loc[corte],
                          "Regla de Taylor": taylor[h - 1],
                          "ARIMA": arima[h - 1]})
    return pd.DataFrame(filas), orden


def resumir(detalle: pd.DataFrame) -> pd.DataFrame:
    filas = []
    for h, grupo in detalle.groupby("horizonte"):
        ecm_ca = ((grupo["tpm_real"] - grupo["Caminata aleatoria"]) ** 2).mean()
        for modelo in MODELOS:
            error = grupo["tpm_real"] - grupo[modelo]
            ecm = (error ** 2).mean()
            filas.append({"horizonte_meses": h, "modelo": modelo, "cortes": len(grupo),
                          "MAE": error.abs().mean(), "RMSE": np.sqrt(ecm),
                          "R2_OOS_vs_caminata": 1 - ecm / ecm_ca if ecm_ca > 0 else np.nan})
    return pd.DataFrame(filas)


def graficar(resumen: pd.DataFrame, orden: tuple, ruta: Path) -> None:
    tabla = resumen.pivot(index="horizonte_meses", columns="modelo", values="RMSE")[MODELOS]
    colores = {"Caminata aleatoria": "#7f7f7f", "Regla de Taylor": "#d62728", "ARIMA": "#1f77b4"}
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ancho = 0.26
    for i, modelo in enumerate(MODELOS):
        x = np.arange(len(tabla)) + (i - 1) * ancho
        barras = ax.bar(x, tabla[modelo], ancho, color=colores[modelo],
                        label=modelo if modelo != "ARIMA" else f"ARIMA{orden}")
        ax.bar_label(barras, fmt="%.2f", fontsize=8)
    ax.set_xticks(range(len(tabla)), [f"{h} meses" for h in tabla.index])
    ax.set_ylabel("RMSE (puntos porcentuales de TPM)")
    ax.set_title("Error de pronóstico de la TPM por horizonte (menor es mejor)\n"
                 "Cortes sep-2016 a sep-2024. Fuente: BCCh y FRED, base del proyecto.", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    panel = armar_panel()
    detalle, orden = evaluar(panel)
    resumen = resumir(detalle)

    carpeta_res = RAIZ / "salidas" / "resultados"
    carpeta_graf = RAIZ / "salidas" / "graficos"
    carpeta_res.mkdir(parents=True, exist_ok=True)
    carpeta_graf.mkdir(parents=True, exist_ok=True)
    resumen.round(4).to_csv(carpeta_res / "comparacion_modelos_resumen.csv", index=False)
    detalle.round(4).to_csv(carpeta_res / "comparacion_modelos_detalle.csv", index=False)
    graficar(resumen, orden, carpeta_graf / "comparacion_modelos_rmse.png")

    print(f"ARIMA usado: ARIMA{orden} (orden elegido con datos hasta {CORTES[0]:%Y-%m})\n")
    print("Comparación fuera de muestra (puntos porcentuales de TPM):\n")
    print(resumen.round(3).to_string(index=False))
    print("\nR² OOS > 0: el modelo le gana a la caminata aleatoria.")
    print("Archivos guardados en salidas/resultados y salidas/graficos")