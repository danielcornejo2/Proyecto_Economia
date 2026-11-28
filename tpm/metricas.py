"""
metricas.py
-----------
Métricas de error de pronóstico, en puntos porcentuales de TPM.
Una sola función para todas las evaluaciones del proyecto.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

BENCHMARK = "Caminata aleatoria"


def tabla_metricas(detalle: pd.DataFrame, modelos: list[str], real: str = "tpm_real",
                   benchmark: str = BENCHMARK, por: str | None = "horizonte") -> pd.DataFrame:
    """
    MAE, RMSE y R² fuera de muestra frente al benchmark, por grupo.

    detalle: una fila por pronóstico, con la columna 'real' y una columna por modelo.
    por:     columna para agrupar (horizonte, corte...). None = una sola tabla.
    R² OOS > 0 significa que el modelo le gana al benchmark.
    """
    grupos = detalle.groupby(por) if por else [("total", detalle)]
    filas = []
    for valor, grupo in grupos:
        ecm_benchmark = ((grupo[real] - grupo[benchmark]) ** 2).mean()
        for modelo in modelos:
            error = grupo[real] - grupo[modelo]
            ecm = (error ** 2).mean()
            filas.append({
                (por or "grupo"): valor,
                "modelo": modelo,
                "n": len(grupo),
                "MAE": error.abs().mean(),
                "RMSE": np.sqrt(ecm),
                # Si el benchmark no se equivoca nunca (TPM sin cambios), el R² no existe
                "R2_OOS": 1 - ecm / ecm_benchmark if ecm_benchmark > 0 else np.nan,
            })
    return pd.DataFrame(filas)