
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd

from modelos.datos_modelo import armar_panel


# Datos históricos del Hito 2
panel = armar_panel()
historico = panel.loc["2024-01-01":, "tpm"]

# Proyecciones calculadas anteriormente
ruta = Path("salidas/resultados/proyeccion_taylor_24m.csv")
proyecciones = pd.read_csv(ruta, parse_dates=["mes"])

# Última TPM observada
ultimo_mes = panel.index.max()
ultima_tpm = float(panel["tpm"].iloc[-1])

# Unimos el último dato real con los pronósticos
fechas = [ultimo_mes] + proyecciones["mes"].tolist()

taylor = [ultima_tpm] + proyecciones["tpm_taylor"].tolist()
ingenuo = [ultima_tpm] + proyecciones["tpm_ingenua"].tolist()

# Gráfico comparativo
fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(
    historico.index,
    historico.values,
    label="TPM observada",
    linewidth=2
)

ax.plot(
    fechas,
    taylor,
    label="Regla de Taylor",
    linestyle="--",
    linewidth=2
)

ax.plot(
    fechas,
    ingenuo,
    label="Modelo ingenuo",
    linestyle=":",
    linewidth=2
)

# Separación entre datos históricos y proyecciones
ax.axvline(
    ultimo_mes,
    linestyle="--",
    alpha=0.5,
    label="Inicio de proyecciones"
)

ax.set_title("TPM histórica y proyecciones a 24 meses")
ax.set_xlabel("Mes")
ax.set_ylabel("TPM (%)")
ax.grid(alpha=0.3)
ax.legend()

fig.autofmt_xdate()
fig.tight_layout()

# Guardamos el gráfico
carpeta = Path("salidas/graficos")
carpeta.mkdir(parents=True, exist_ok=True)

ruta_grafico = carpeta / "proyeccion_tpm_24m.png"

fig.savefig(ruta_grafico, dpi=300)
plt.close(fig)

print("Gráfico de proyecciones generado correctamente")
print("Archivo:", ruta_grafico)

