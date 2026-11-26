import numpy as np
import pandas as pd

from modelos.datos_modelo import armar_panel
from modelos.regla_taylor import estimar_regla_taylor


# Panel mensual del proyecto
panel = armar_panel()

# Cortes de entrenamiento
cortes = [
    "2021-12-01",
    "2022-12-01",
    "2023-12-01",
    "2024-12-01",
]

variables = [
    "tpm_lag1",
    "brecha_inflacion_esp",
    "brecha_actividad",
    "fed_funds",
]


def metricas(real, prediccion):
    errores = real - prediccion
    mae = errores.abs().mean()
    rmse = np.sqrt((errores ** 2).mean())
    return mae, rmse


resultados = []

for corte in cortes:

    # Estimamos utilizando solo datos hasta el corte
    coeficientes, _ = estimar_regla_taylor(panel, corte)

    # Evaluamos los 12 meses siguientes
    inicio = pd.Timestamp(corte) + pd.DateOffset(months=1)
    fin = inicio + pd.DateOffset(months=11)
    prueba = panel.loc[inicio:fin]

    if len(prueba) != 12:
        print(f"Corte {corte}: periodo incompleto")
        continue

    real = prueba["tpm"]

    # Pronóstico de Taylor
    pred_taylor = (
        coeficientes["constante"]
        + prueba[variables].mul(
            coeficientes[variables], axis=1
        ).sum(axis=1)
    )

    # Pronóstico ingenuo
    pred_ingenuo = prueba["tpm_lag1"]

    mae_t, rmse_t = metricas(real, pred_taylor)
    mae_i, rmse_i = metricas(real, pred_ingenuo)

    resultados.append({
        "Corte": corte[:7],
        "Meses": len(prueba),
        "MAE Taylor": round(mae_t, 4),
        "RMSE Taylor": round(rmse_t, 4),
        "MAE ingenuo": round(mae_i, 4),
        "RMSE ingenuo": round(rmse_i, 4),
    })


tabla = pd.DataFrame(resultados)

print("\nValidación temporal de la Regla de Taylor")
print(tabla.to_string(index=False))