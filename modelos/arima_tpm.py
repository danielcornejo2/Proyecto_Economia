"""
arima_tpm.py
------------
 modelo ARIMA para la TPM.

Idea: pronosticar la TPM usando SOLO su propia historia (sin otras variables).
Sirve de punto de comparación para la regla de Taylor de la Persona 2:
si Taylor no le gana a un ARIMA, las variables macro no están aportando.

Pasos:
    1. Evaluar la estacionariedad mediante ADF y KPSS en nivel y primera
     diferencia. El ADF contrasta raíz unitaria; KPSS contrasta
     estacionariedad. Se adopta d = 1 para modelar los cambios de la TPM,
     dada su elevada persistencia, aunque el ADF también rechaza raíz
     unitaria en nivel. Se compara d = 0 como análisis de robustez.
  2. Elegir p y q: se prueban todas las combinaciones de 0 a 3 y se elige la de
     menor AIC, usando SOLO el período de entrenamiento (hasta FIN_ENTRENAMIENTO).
  3. Estimar el ARIMA elegido y revisar los residuos (test de Ljung-Box).

¿Por qué ARIMA y no SARIMA? La TPM la fija el Consejo del BCCh en reuniones a lo
largo del año; no tiene un patrón que se repita cada 12 meses (como el Imacec en
febrero). Por eso no se agrega componente estacional. El script lo verifica
mirando la autocorrelación en el rezago 12 de la TPM diferenciada.

El período de entrenamiento es el mismo que usa la regla de Taylor
(hasta diciembre de 2024), para que ambos modelos se comparen en igualdad.

Uso (desde la raíz del proyecto):
    python modelos/arima_tpm.py
"""

from __future__ import annotations

import itertools
import sys
import warnings
from pathlib import Path

import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import acf, adfuller, kpss

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from modelos.datos_modelo import leer_consultas  # noqa: E402

FIN_ENTRENAMIENTO = "2024-12-01"   # igual que la regla de Taylor
MAXIMO_P_Q = 3                     # se prueban p y q entre 0 y 3

# Avisos de convergencia de statsmodels: no son errores, solo ensucian la pantalla
warnings.filterwarnings("ignore")


def cargar_tpm() -> pd.Series:
    """TPM mensual (% anual) desde la base, con frecuencia mensual."""
    niveles, _ = leer_consultas()
    tpm = niveles["tpm"].dropna()
    tpm.index = pd.DatetimeIndex(tpm.index, freq="MS")
    return tpm.rename("tpm")


def test_estacionariedad(serie: pd.Series) -> pd.DataFrame:
    """Contrasta estacionariedad mediante ADF y KPSS."""
    filas = {}

    datos_prueba = {
        "Nivel": serie,
        "Primera diferencia": serie.diff().dropna(),
    }

    for nombre, datos in datos_prueba.items():
        estadistico_adf, p_adf, *_ = adfuller(datos, autolag="AIC")
        estadistico_kpss, p_kpss, *_ = kpss(
            datos, regression="c", nlags="auto"
        )

        filas[nombre] = {
            "ADF": estadistico_adf,
            "p_ADF": p_adf,
            "KPSS": estadistico_kpss,
            "p_KPSS": p_kpss,
        }

    return pd.DataFrame(filas).T

def elegir_orden(serie: pd.Series, d: int = 1, maximo: int = MAXIMO_P_Q) -> tuple[tuple, pd.DataFrame]:
    """Prueba ARIMA(p, d, q) para p, q en 0..maximo y devuelve el de menor AIC."""
    resultados = []
    for p, q in itertools.product(range(maximo + 1), repeat=2):
        try:
            ajuste = ARIMA(serie, order=(p, d, q)).fit()
            resultados.append({"p": p, "d": d, "q": q, "AIC": ajuste.aic, "BIC": ajuste.bic})
        except Exception:      # algunas combinaciones no convergen: se omiten
            continue
    tabla = pd.DataFrame(resultados).sort_values("AIC").reset_index(drop=True)
    mejor = tabla.iloc[0]
    return (int(mejor.p), int(mejor.d), int(mejor.q)), tabla


def estimar_arima(serie: pd.Series, orden: tuple):
    """Estima el ARIMA con el orden indicado y devuelve el resultado de statsmodels."""
    return ARIMA(serie, order=orden).fit()


if __name__ == "__main__":
    tpm = cargar_tpm()
    entrenamiento = tpm.loc[:FIN_ENTRENAMIENTO]
    print(f"TPM mensual: {tpm.index.min():%Y-%m} a {tpm.index.max():%Y-%m} ({len(tpm)} meses)")
    print(f"Entrenamiento: hasta {FIN_ENTRENAMIENTO[:7]} ({len(entrenamiento)} meses)\n")

    # 1. Estacionariedad
    print("1) Pruebas de estacionariedad (ADF y KPSS)")
    print(test_estacionariedad(entrenamiento).round(3).to_string(), "\n")
    print("ADF: p < 0.05 rechaza raíz unitaria.")
    print("KPSS: p < 0.05 rechaza estacionariedad.")
    print("Se compara d=0 como robustez; d=1 no se deduce del ADF.\n")

    # ¿Hace falta componente estacional? Autocorrelación en el rezago 12
    ac12 = acf(entrenamiento.diff().dropna(), nlags=12)[12]
    print(f"   Autocorrelación de la TPM diferenciada en el rezago 12: {ac12:.2f} "
          f"({'baja: no se necesita SARIMA' if abs(ac12) < 0.2 else 'revisar SARIMA'})\n")

    # 2. Selección del orden
    orden, tabla_aic = elegir_orden(entrenamiento)
    print("2) Las 5 mejores combinaciones según AIC (menor es mejor)")
    print(tabla_aic.head().round(1).to_string(index=False), "\n")
    print(f"   Modelo elegido: ARIMA{orden}\n")

    # 3. Estimación y diagnóstico
    ajuste = estimar_arima(entrenamiento, orden)
    print("3) Coeficientes estimados")
    print(ajuste.summary().tables[1], "\n")

    ljung = acorr_ljungbox(ajuste.resid.iloc[1:], lags=[12], return_df=True)
    p_lb = float(ljung["lb_pvalue"].iloc[0])
    print(f"   Ljung-Box (12 rezagos) sobre los residuos: p = {p_lb:.3f} -> "
          + ("residuos sin autocorrelación: el modelo captura la dinámica."
             if p_lb > 0.05 else "queda autocorrelación en los residuos: anotarlo como limitación."))

    carpeta = RAIZ / "salidas" / "resultados"
    carpeta.mkdir(parents=True, exist_ok=True)
    tabla_aic.round(2).to_csv(carpeta / "seleccion_arima_aic.csv", index=False)
    print(f"\nTabla de AIC guardada en {(carpeta / 'seleccion_arima_aic.csv').relative_to(RAIZ)}")