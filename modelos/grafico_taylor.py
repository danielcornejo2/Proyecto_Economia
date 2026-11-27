from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from modelos.evaluacion_taylor import (
    real,
    pred_taylor,
    pred_ingenuo,
)

# Comparación de pronósticos fuera de muestra
plt.figure(figsize=(11, 5))

plt.plot(real.index, real, label="TPM real", linewidth=2)
plt.plot(pred_taylor.index, pred_taylor,
         label="Regla de Taylor", linestyle="--")
plt.plot(pred_ingenuo.index, pred_ingenuo,
         label="Modelo ingenuo", linestyle=":")

plt.title("TPM real y pronósticos fuera de muestra")
plt.xlabel("Mes")
plt.ylabel("TPM (%)")
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

# Guardar el gráfico para el informe
carpeta = Path("hito_3/graficos")
carpeta.mkdir(parents=True, exist_ok=True)

plt.savefig(carpeta / "comparacion_tpm.png", dpi=300)
plt.close()
print("Gráfico guardado en hito_3/graficos/comparacion_tpm.png")
