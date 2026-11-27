

"""
Regla de Taylor para la TPM de Chile.
Modelo con inercia, inflación esperada,
brecha de actividad y Fed Funds.
"""

import numpy as np
import pandas as pd

EXPLICATIVAS = [
    "tpm_lag1",
    "brecha_inflacion_esp",
    "brecha_actividad",
    "fed_funds",
]


def estimar_regla_taylor(panel, fecha_fin_entrenamiento):
    """Estima la regla usando datos hasta la fecha indicada."""

    columnas = ["tpm"] + EXPLICATIVAS

    faltantes = [c for c in columnas if c not in panel.columns]
    if faltantes:
        raise ValueError(f"Faltan columnas: {faltantes}")

    if not isinstance(panel.index, pd.DatetimeIndex):
        raise ValueError("El panel debe tener un índice de fechas.")

    fecha_corte = pd.Timestamp(fecha_fin_entrenamiento)

    datos = panel.loc[
        panel.index <= fecha_corte, columnas
    ].copy()

    datos = datos.replace(
        [np.inf, -np.inf], np.nan
    ).dropna()

    if len(datos) <= len(EXPLICATIVAS) + 1:
        raise ValueError("No hay suficientes observaciones.")

    # Variable dependiente
    y = datos["tpm"].to_numpy(dtype=float)

    # Variables explicativas y constante
    X = datos[EXPLICATIVAS].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(X)), X])

    # Estimación por mínimos cuadrados ordinarios
    beta, _, rango, _ = np.linalg.lstsq(X, y, rcond=None)

    if rango < X.shape[1]:
        raise ValueError("Las variables no tienen rango completo.")

    # Coeficientes estimados
    coeficientes = pd.Series(
        beta,
        index=["constante"] + EXPLICATIVAS,
        name="coeficiente"
    )

    # Valores ajustados dentro del entrenamiento
    resultados = pd.DataFrame(
        {
            "tpm_efectiva": y,
            "tpm_ajustada": X @ beta
        },
        index=datos.index
    )

    return coeficientes, resultados
