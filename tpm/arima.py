"""
arima.py
--------
Modelo ARIMA de la TPM: estacionariedad, selección del orden, estimación,
diagnóstico y pronóstico. Todas las funciones devuelven DataFrames o Series.
"""

from __future__ import annotations

import itertools
import warnings

import numpy as np
import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import acf, adfuller, kpss

from modelos.datos_modelo import leer_consultas

FIN_ENTRENAMIENTO = "2024-12-01"   # mismo entrenamiento que la regla de Taylor
MAXIMO_P_Q = 3                     # se prueban p y q entre 0 y 3
REZAGOS_LJUNG_BOX = 12
NIVEL_INTERVALO = 0.80
PISO_TPM = 0.5                     # mínimo histórico de la TPM (2020): el intervalo no baja de ahí


def cargar_tpm() -> pd.Series:
    """TPM mensual (% anual, fin de mes) desde la base, con frecuencia mensual."""
    niveles, _ = leer_consultas()
    tpm = niveles["tpm"].dropna()
    tpm.index = pd.DatetimeIndex(tpm.index, freq="MS")
    return tpm.rename("tpm")


def ajustar(serie: pd.Series, orden: tuple):
    """Estima un ARIMA sin mostrar los avisos de convergencia de statsmodels."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return ARIMA(serie, order=orden).fit()


def pruebas_estacionariedad(serie: pd.Series) -> pd.DataFrame:
    """
    ADF (H0: raíz unitaria) y KPSS (H0: estacionaria), en nivel y en primera diferencia.
    KPSS informa p = 0,10 cuando el p-valor real es mayor (tope de su tabla).
    """
    filas = {}
    for nombre, datos in {"Nivel": serie, "Primera diferencia": serie.diff().dropna()}.items():
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            adf, p_adf, *_ = adfuller(datos, autolag="AIC")
            estadistico_kpss, p_kpss, *_ = kpss(datos, regression="c", nlags="auto")
        filas[nombre] = {"ADF": adf, "p_ADF": p_adf, "KPSS": estadistico_kpss, "p_KPSS": p_kpss}
    return pd.DataFrame(filas).T


def autocorrelacion_estacional(serie: pd.Series, rezago: int = 12) -> float:
    """Autocorrelación de la serie diferenciada en el rezago 12: si es baja, no hace falta SARIMA."""
    return float(acf(serie.diff().dropna(), nlags=rezago)[rezago])


def seleccionar_orden(serie: pd.Series, d: int = 1,
                      maximo: int = MAXIMO_P_Q) -> tuple[tuple, pd.DataFrame]:
    """Prueba ARIMA(p, d, q) con p, q entre 0 y 'maximo'; devuelve el de menor AIC y la tabla."""
    resultados = []
    for p, q in itertools.product(range(maximo + 1), repeat=2):
        try:
            ajuste = ajustar(serie, (p, d, q))
        except Exception:      # algunas combinaciones no convergen: se omiten
            continue
        resultados.append({"p": p, "d": d, "q": q, "AIC": ajuste.aic, "BIC": ajuste.bic})
    tabla = pd.DataFrame(resultados).sort_values("AIC").reset_index(drop=True)
    mejor = tabla.iloc[0]
    return (int(mejor.p), int(mejor.d), int(mejor.q)), tabla


def tabla_coeficientes(ajuste) -> pd.DataFrame:
    """Coeficientes del ARIMA con su error estándar y p-valor."""
    return pd.DataFrame({"coeficiente": ajuste.params, "error": ajuste.bse,
                         "p_valor": ajuste.pvalues})


def p_valor_ljung_box(ajuste, rezagos: int = REZAGOS_LJUNG_BOX) -> float:
    """p-valor de Ljung-Box sobre los residuos (p > 0,05: sin autocorrelación)."""
    # Se omite el primer residuo, que en un modelo diferenciado no es informativo
    prueba = acorr_ljungbox(ajuste.resid.iloc[1:], lags=[rezagos], return_df=True)
    return float(prueba["lb_pvalue"].iloc[0])


def pronosticar(serie: pd.Series, orden: tuple, pasos: int,
                nivel: float = NIVEL_INTERVALO, piso: float = PISO_TPM) -> pd.DataFrame:
    """Pronóstico a 'pasos' meses con su intervalo; el límite inferior no baja del piso."""
    tabla = ajustar(serie, orden).get_forecast(steps=pasos).summary_frame(alpha=1 - nivel)
    return pd.DataFrame({
        "horizonte": np.arange(1, pasos + 1),
        "tpm": tabla["mean"].to_numpy(),
        "li": np.maximum(tabla["mean_ci_lower"].to_numpy(), piso),
        "ls": tabla["mean_ci_upper"].to_numpy(),
    }, index=tabla.index.rename("mes"))


if __name__ == "__main__":
    entrenamiento = cargar_tpm().loc[:FIN_ENTRENAMIENTO]
    print(pruebas_estacionariedad(entrenamiento).round(3))
    orden, tabla_aic = seleccionar_orden(entrenamiento)
    ajuste = ajustar(entrenamiento, orden)
    print(f"\nARIMA{orden}\n", tabla_coeficientes(ajuste).round(3))
    print(f"Ljung-Box p = {p_valor_ljung_box(ajuste):.3f}")