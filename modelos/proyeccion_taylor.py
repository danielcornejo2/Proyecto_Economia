
from pathlib import Path

import pandas as pd

from modelos.datos_modelo import armar_panel
from modelos.regla_taylor import estimar_regla_taylor


# Datos mensuales de la base original del Hito 2
panel = armar_panel()

# Último mes disponible
corte = panel.index.max()

# Estimamos con toda la información disponible hasta el corte
coeficientes, _ = estimar_regla_taylor(
    panel, corte.strftime("%Y-%m-%d")
)

# Últimos valores conocidos
ultimo = panel.iloc[-1]
tpm_anterior = float(ultimo["tpm"])

# Escenario inicial: variables económicas constantes
variables = [
    "brecha_inflacion_esp",
    "brecha_actividad",
    "fed_funds",
]

componente_fijo = float(coeficientes["constante"])

for variable in variables:
    componente_fijo += float(
        coeficientes[variable] * ultimo[variable]
    )

# Proyección mensual hasta 24 meses
fechas = pd.date_range(
    start=corte + pd.offsets.MonthBegin(1),
    periods=24,
    freq="MS"
)

resultados = []

for horizonte, fecha in enumerate(fechas, start=1):

    # La TPM proyectada pasa a ser el rezago del mes siguiente
    tpm_proyectada = (
        componente_fijo
        + coeficientes["tpm_lag1"] * tpm_anterior
    )

    resultados.append({
        "mes": fecha,
        "horizonte": horizonte,
        "tpm_taylor": float(tpm_proyectada),
        "tpm_ingenua": float(ultimo["tpm"]),
    })

    tpm_anterior = float(tpm_proyectada)

proyecciones = pd.DataFrame(resultados)

# Mostramos los horizontes solicitados
resumen = proyecciones[
    proyecciones["horizonte"].isin([6, 12, 24])
]

print("Proyección de TPM: escenario de variables constantes")
print("Fecha de corte:", corte.strftime("%Y-%m"))
print("TPM inicial:", ultimo["tpm"])
resumen = resumen.copy()
resumen[["tpm_taylor", "tpm_ingenua"]] = resumen[
    ["tpm_taylor", "tpm_ingenua"]
].round(4)

print(resumen.to_string(index=False))

# Guardamos los resultados
carpeta = Path("hito_3/resultados")
carpeta.mkdir(parents=True, exist_ok=True)

ruta = carpeta / "proyeccion_taylor_24m.csv"
proyecciones.to_csv(ruta, index=False)

print("Resultados guardados en:", ruta)
