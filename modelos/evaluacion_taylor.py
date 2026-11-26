import numpy as np

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