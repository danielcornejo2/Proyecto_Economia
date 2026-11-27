"""
significancia_taylor.py
-----------------------
significancia estadística de la regla de Taylor y respuestas de largo plazo.

regla_taylor.py estima los coeficientes por MCO pero no informa si son
estadísticamente distintos de cero. Este script estima la MISMA especificación:

    TPM_t = c + ρ·TPM_{t-1} + β_π·(EEE − 3)_t + β_y·brecha_t + β_f·FedFunds_t + e_t

con errores estándar robustos HAC (Newey-West, 12 rezagos). Se usan errores
robustos porque en series mensuales los residuos suelen estar autocorrelacionados
y ser heterocedásticos; con errores MCO normales los p-valores saldrían demasiado
optimistas.

Respuestas de largo plazo: como la regla tiene inercia (ρ), el efecto total de
una variable es β / (1 − ρ). Es el número comparable con la literatura
(Caputo y Herrera, 2013: inflación esperada 1,174; brecha 0,656; Fed Funds 1,2).
Su error estándar se calcula con el método delta.

Se estima con dos muestras:
  - Entrenamiento (hasta 2024-12): la que usan las evaluaciones fuera de muestra.
  - Muestra completa (hasta el último mes): la que usa la proyección.

Uso (desde la raíz del proyecto):
    python -m modelos.significancia_taylor
Resultado:
    hito_3/resultados/significancia_taylor.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from modelos.datos_modelo import armar_panel  # noqa: E402
from modelos.regla_taylor import EXPLICATIVAS  # noqa: E402

REZAGOS_HAC = 12
NOMBRES = {
    "const": "Constante",
    "tpm_lag1": "TPM rezagada (ρ, inercia)",
    "brecha_inflacion_esp": "Brecha de inflación esperada",
    "brecha_actividad": "Brecha de actividad",
    "fed_funds": "Fed Funds",
}


def estimar(panel: pd.DataFrame, fin: str | None = None):
    """MCO con errores HAC sobre la muestra hasta 'fin' (o completa)."""
    datos = panel[["tpm"] + EXPLICATIVAS].dropna()
    if fin is not None:
        datos = datos.loc[:fin]
    X = sm.add_constant(datos[EXPLICATIVAS])
    modelo = sm.OLS(datos["tpm"], X).fit(cov_type="HAC", cov_kwds={"maxlags": REZAGOS_HAC})
    return modelo, datos


def tabla_coeficientes(modelo, muestra: str) -> pd.DataFrame:
    """Coeficientes de corto plazo y respuestas de largo plazo con su significancia."""
    filas = []
    for variable in modelo.params.index:
        filas.append({"muestra": muestra, "plazo": "corto", "variable": NOMBRES[variable],
                      "coeficiente": modelo.params[variable], "error_hac": modelo.bse[variable],
                      "p_valor": modelo.pvalues[variable]})

    # Largo plazo: β / (1 − ρ), con error estándar por método delta
    rho = modelo.params["tpm_lag1"]
    cov = modelo.cov_params()
    for variable in ["brecha_inflacion_esp", "brecha_actividad", "fed_funds"]:
        beta = modelo.params[variable]
        largo = beta / (1 - rho)
        gradiente = np.array([1 / (1 - rho), beta / (1 - rho) ** 2])   # d/dβ, d/dρ
        sub = cov.loc[[variable, "tpm_lag1"], [variable, "tpm_lag1"]].to_numpy()
        error = float(np.sqrt(gradiente @ sub @ gradiente))
        z = largo / error
        filas.append({"muestra": muestra, "plazo": "largo", "variable": NOMBRES[variable],
                      "coeficiente": largo, "error_hac": error,
                      "p_valor": 2 * (1 - norm.cdf(abs(z)))})
    tabla = pd.DataFrame(filas)
    tabla["significativo_5%"] = np.where(tabla["p_valor"] < 0.05, "sí", "no")
    return tabla


if __name__ == "__main__":
    panel = armar_panel()
    resultados = []
    for etiqueta, fin in [("Entrenamiento (hasta 2024-12)", "2024-12-01"),
                          ("Muestra completa", None)]:
        modelo, datos = estimar(panel, fin)
        print(f"\n=== {etiqueta}: {datos.index.min():%Y-%m} a {datos.index.max():%Y-%m} "
              f"({len(datos)} meses), R² = {modelo.rsquared:.3f} ===")
        tabla = tabla_coeficientes(modelo, etiqueta)
        print(tabla.drop(columns="muestra").round(3).to_string(index=False))
        resultados.append(tabla)

    print("\nReferencia (Caputo y Herrera, 2013), largo plazo: inflación esperada 1,174; "
          "brecha 0,656; Fed Funds 1,2.")
    print("Lectura: p < 0,05 = la variable tiene un efecto estadísticamente distinto de cero.")

    carpeta = RAIZ / "hito_3" / "resultados"
    carpeta.mkdir(parents=True, exist_ok=True)
    pd.concat(resultados).round(4).to_csv(carpeta / "significancia_taylor.csv", index=False)
    print("\nGuardado en hito_3/resultados/significancia_taylor.csv")