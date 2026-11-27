
import numpy as np
import pandas as pd
from pathlib import Path

from modelos.datos_modelo import armar_panel
from modelos.regla_taylor import estimar_regla_taylor


# Panel mensual de la base original del Hito 2
panel = armar_panel()

# Fechas desde las que se harán los pronósticos
cortes = [pd.Timestamp(f"{anio}-09-01") for anio in range(2016, 2025)]
horizontes = [6, 12, 24]

variables = [
    "brecha_inflacion_esp",
    "brecha_actividad",
    "fed_funds",
]

resultados = []

for corte in cortes:

    if corte not in panel.index:
        continue

    # Estimación con información hasta el corte
    coeficientes, _ = estimar_regla_taylor(
        panel, corte.strftime("%Y-%m-%d")
    )

    # TPM observada al corte
    ultimo = panel.loc[corte]
    tpm_inicial = float(ultimo["tpm"])

    # Variables disponibles para pronosticar el mes siguiente
    fila_siguiente = panel.loc[corte + pd.offsets.MonthBegin(1)]

    # Mantenemos constantes las variables explicativas
    componente_fijo = float(coeficientes["constante"])

    for variable in variables:
        componente_fijo += float(
            coeficientes[variable] * fila_siguiente[variable]        )

    # Pronósticos recursivos de hasta 24 meses
    tpm_proyectada = tpm_inicial

    for paso in range(1, 25):

        tpm_proyectada = (
            componente_fijo
            + coeficientes["tpm_lag1"] * tpm_proyectada
        )

        if paso not in horizontes:
            continue

        fecha_objetivo = corte + pd.DateOffset(months=paso)

        if fecha_objetivo not in panel.index:
            continue

        tpm_real = float(panel.loc[fecha_objetivo, "tpm"])

        resultados.append({
            "corte": corte.strftime("%Y-%m"),
            "horizonte": paso,
            "fecha_objetivo": fecha_objetivo,
            "tpm_real": tpm_real,
            "taylor": float(tpm_proyectada),
            "ingenuo": tpm_inicial,
        })


tabla = pd.DataFrame(resultados)

print("\nEvaluación fuera de muestra por horizonte")

resumen = []

for horizonte in horizontes:

    datos = tabla[tabla["horizonte"] == horizonte]

    if datos.empty:
        continue

    fila = {
        "Horizonte": horizonte,
        "Cortes": len(datos),
    }

    for modelo in ["taylor", "ingenuo"]:
        errores = datos["tpm_real"] - datos[modelo]

        fila[f"MAE {modelo}"] = round(
            errores.abs().mean(), 4
        )
        fila[f"RMSE {modelo}"] = round(
            np.sqrt((errores ** 2).mean()), 4
        )

    resumen.append(fila)


resumen = pd.DataFrame(resumen)
print(resumen.to_string(index=False))

# Guardar resultados para el informe
carpeta = Path("salidas/resultados")
carpeta.mkdir(parents=True, exist_ok=True)

tabla.to_csv(
    carpeta / "evaluacion_horizontes_detalle.csv",
    index=False
)

resumen.to_csv(
    carpeta / "evaluacion_horizontes_resumen.csv",
    index=False
)

print("\nEvaluación guardada correctamente")
