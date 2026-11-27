from pathlib import Path

import numpy as np
import pandas as pd

from modelos.datos_modelo import armar_panel
from modelos.regla_taylor import estimar_regla_taylor


# Panel mensual con la base original del Hito 2
panel = armar_panel()

# Estimación hasta diciembre de 2024
coeficientes, resultados = estimar_regla_taylor(
    panel, "2024-12-01"
)

# Período fuera de muestra
prueba = panel.loc["2025-01-01":"2026-09-01"]

variables = [
    "tpm_lag1",
    "brecha_inflacion_esp",
    "brecha_actividad",
    "fed_funds",
]

# Valores observados
real = prueba["tpm"]

# Pronósticos de la Regla de Taylor
pred_taylor = (
    coeficientes["constante"]
    + prueba[variables].mul(coeficientes[variables], axis=1).sum(axis=1)
)

# Pronóstico ingenuo: TPM del mes anterior
pred_ingenuo = prueba["tpm_lag1"]


# Métricas de evaluación
def calcular_metricas(real, prediccion):
    errores = real - prediccion
    mae = errores.abs().mean()
    rmse = np.sqrt((errores**2).mean())
    return mae, rmse


mae_taylor, rmse_taylor = calcular_metricas(real, pred_taylor)
mae_ingenuo, rmse_ingenuo = calcular_metricas(real, pred_ingenuo)

print("Evaluación fuera de muestra")
print("Meses evaluados:", len(prueba))
print(f"Regla de Taylor: MAE={mae_taylor:.4f}, RMSE={rmse_taylor:.4f}")
print(f"Modelo ingenuo: MAE={mae_ingenuo:.4f}, RMSE={rmse_ingenuo:.4f}")

# Guardar métricas de evaluación
carpeta = Path("salidas/resultados")
carpeta.mkdir(parents=True, exist_ok=True)

metricas = pd.DataFrame({
    "modelo": ["Regla de Taylor", "Caminata aleatoria"],
    "mae": [mae_taylor, mae_ingenuo],
    "rmse": [rmse_taylor, rmse_ingenuo],
})

metricas.to_csv(
    carpeta / "evaluacion_taylor_metricas.csv",
    index=False,
    encoding="utf-8-sig"
)

# Guardar pronósticos y errores mensuales
detalle = pd.DataFrame({
    "mes": prueba.index,
    "tpm_real": real.to_numpy(),
    "taylor": pred_taylor.to_numpy(),
    "ingenuo": pred_ingenuo.to_numpy(),
    "error_taylor": (real - pred_taylor).to_numpy(),
    "error_ingenuo": (real - pred_ingenuo).to_numpy(),
    "error_abs_taylor": (real - pred_taylor).abs().to_numpy(),
    "error_abs_ingenuo": (real - pred_ingenuo).abs().to_numpy(),
    "error_cuadrado_taylor": ((real - pred_taylor) ** 2).to_numpy(),
    "error_cuadrado_ingenuo": ((real - pred_ingenuo) ** 2).to_numpy(),
})

detalle.to_csv(
    carpeta / "evaluacion_taylor_detalle.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Métricas y detalle de Taylor guardados en CSV")
