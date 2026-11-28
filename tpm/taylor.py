"""
taylor.py
---------
Regla de Taylor para la TPM de Chile:

    TPM_t = c + ρ·TPM_t−1 + β_π·(EEE − 3) + β_y·brecha + β_f·FedFunds

Una sola estimación (MCO con errores HAC) sirve para los coeficientes, la
significancia, las respuestas de largo plazo, las evaluaciones y la proyección.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm

EXPLICATIVAS = ["tpm_lag1", "brecha_inflacion_esp", "brecha_actividad", "fed_funds"]
DETERMINANTES = EXPLICATIVAS[1:]   # todo menos la inercia
REZAGOS_HAC = 12                   # Newey-West: un año de autocorrelación en datos mensuales
NOMBRES = {
    "constante": "Constante",
    "tpm_lag1": "TPM rezagada (ρ, inercia)",
    "brecha_inflacion_esp": "Brecha de inflación esperada",
    "brecha_actividad": "Brecha de actividad",
    "fed_funds": "Fed Funds",
}


def estimar(panel: pd.DataFrame, fin: str | pd.Timestamp | None = None):
    """MCO con errores HAC usando las filas del panel hasta 'fin' (None = muestra completa)."""
    datos = panel[["tpm"] + EXPLICATIVAS].dropna()
    if fin is not None:
        datos = datos.loc[:fin]
    X = sm.add_constant(datos[EXPLICATIVAS]).rename(columns={"const": "constante"})
    return sm.OLS(datos["tpm"], X).fit(cov_type="HAC", cov_kwds={"maxlags": REZAGOS_HAC})


def coeficientes(modelo) -> pd.Series:
    """Coeficientes estimados, con índice constante, tpm_lag1, ..."""
    return modelo.params.rename("coeficiente")


def estadisticos(modelo) -> pd.Series:
    """Datos generales de la estimación: período, número de meses y R²."""
    indice = modelo.model.data.row_labels
    return pd.Series({"inicio": indice.min(), "fin": indice.max(),
                      "meses": int(modelo.nobs), "R2": modelo.rsquared})


def tabla_coeficientes(modelo) -> pd.DataFrame:
    """Coeficientes de corto plazo y respuestas de largo plazo β/(1−ρ) con su significancia."""
    filas = [{"plazo": "corto", "variable": NOMBRES[v], "coeficiente": modelo.params[v],
              "error_hac": modelo.bse[v], "p_valor": modelo.pvalues[v]}
             for v in modelo.params.index]

    # Largo plazo: error estándar por método delta sobre β y ρ
    rho = modelo.params["tpm_lag1"]
    covarianza = modelo.cov_params()
    for v in DETERMINANTES:
        beta = modelo.params[v]
        largo = beta / (1 - rho)
        gradiente = np.array([1 / (1 - rho), beta / (1 - rho) ** 2])
        sub = covarianza.loc[[v, "tpm_lag1"], [v, "tpm_lag1"]].to_numpy()
        error = float(np.sqrt(gradiente @ sub @ gradiente))
        filas.append({"plazo": "largo", "variable": NOMBRES[v], "coeficiente": largo,
                      "error_hac": error, "p_valor": 2 * (1 - norm.cdf(abs(largo / error)))})

    tabla = pd.DataFrame(filas)
    tabla["significativo_5%"] = tabla["p_valor"] < 0.05
    return tabla


def ajustados(modelo) -> pd.DataFrame:
    """TPM efectiva y ajustada por la regla dentro de la muestra de estimación."""
    return pd.DataFrame({"tpm_efectiva": modelo.model.endog,
                         "tpm_ajustada": modelo.fittedvalues})


def pronostico_un_paso(coef: pd.Series, filas: pd.DataFrame) -> pd.Series:
    """Pronóstico a un mes: usa la TPM observada del mes anterior de cada fila."""
    return coef["constante"] + filas[EXPLICATIVAS].mul(coef[EXPLICATIVAS], axis=1).sum(axis=1)


def proyectar(coef: pd.Series, tpm_inicial: float, determinantes: pd.DataFrame) -> np.ndarray:
    """
    Proyección recursiva: cada TPM proyectada es el rezago del mes siguiente.
    'determinantes' tiene una fila por mes proyectado y una columna por determinante.
    """
    tpm, trayectoria = tpm_inicial, []
    for _, fila in determinantes.iterrows():
        tpm = coef["constante"] + coef["tpm_lag1"] * tpm + (coef[DETERMINANTES] * fila[DETERMINANTES]).sum()
        trayectoria.append(tpm)
    return np.array(trayectoria)


def escenarios(punto_partida: pd.Series, horizonte: int = 24) -> dict[str, pd.DataFrame]:
    """
    Trayectoria de los determinantes en cada escenario (los shocks son ilustrativos):
      Base:             constantes en su último valor conocido.
      Convergencia:     expectativas a la meta y brecha cerrada, lineal en 12 meses.
      Riesgo al alza:   expectativas +1 pp y Fed Funds +0,5 pp.
      Riesgo a la baja: brecha −2 pp, expectativas −0,5 pp y Fed Funds −1 pp.
    """
    meses = np.arange(1, horizonte + 1)
    base = pd.DataFrame({v: np.repeat(punto_partida[v], horizonte) for v in DETERMINANTES},
                        index=meses)

    convergencia = base.copy()
    peso = np.clip(1 - meses / 12, 0, None)   # pasa de 1 a 0 en 12 meses
    convergencia["brecha_inflacion_esp"] = punto_partida["brecha_inflacion_esp"] * peso
    convergencia["brecha_actividad"] = punto_partida["brecha_actividad"] * peso

    alza = base.copy()
    alza["brecha_inflacion_esp"] += 1.0
    alza["fed_funds"] += 0.5

    baja = base.copy()
    baja["brecha_actividad"] -= 2.0
    baja["brecha_inflacion_esp"] -= 0.5
    baja["fed_funds"] -= 1.0

    return {"Base": base, "Convergencia": convergencia,
            "Riesgo al alza": alza, "Riesgo a la baja": baja}


if __name__ == "__main__":
    from modelos.datos_modelo import armar_panel

    modelo = estimar(armar_panel(), "2024-12-01")
    print(estadisticos(modelo))
    print(tabla_coeficientes(modelo).round(3))