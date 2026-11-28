"""
proyeccion.py
-------------
Proyección de la TPM a 24 meses desde el último dato:
  - Regla de Taylor en cuatro escenarios (ver taylor.escenarios).
  - ARIMA con su intervalo de 80 %.
  - Caminata aleatoria (benchmark).
El punto de partida es fila_pronostico(): lo que se sabía al cierre del mes de corte.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from modelos.datos_modelo import armar_panel, fila_pronostico
from tpm import arima, taylor
from tpm.metricas import BENCHMARK

HORIZONTE = 24
HORIZONTES_RESUMEN = [6, 12, 24]


def punto_partida() -> pd.Series:
    """Información disponible al cierre del corte con la que se inicia la proyección."""
    return fila_pronostico()[taylor.EXPLICATIVAS]


def proyectar(horizonte: int = HORIZONTE) -> pd.DataFrame:
    """
    Una fila por mes, modelo y escenario, con la TPM proyectada y, solo para el
    ARIMA, los límites del intervalo (li, ls).
    """
    panel = armar_panel()
    corte = panel.index.max()
    inicio = punto_partida()
    tpm_inicial = float(inicio["tpm_lag1"])
    meses = pd.date_range(corte + pd.offsets.MonthBegin(1), periods=horizonte, freq="MS")
    partes = []

    def agregar(modelo: str, escenario: str, tpm, li=np.nan, ls=np.nan):
        partes.append(pd.DataFrame({"mes": meses, "horizonte": np.arange(1, horizonte + 1),
                                    "modelo": modelo, "escenario": escenario,
                                    "tpm": tpm, "li": li, "ls": ls}))

    # Regla de Taylor estimada con toda la muestra, en cada escenario
    coef = taylor.coeficientes(taylor.estimar(panel))
    for nombre, determinantes in taylor.escenarios(inicio, horizonte).items():
        agregar("Regla de Taylor", nombre, taylor.proyectar(coef, tpm_inicial, determinantes))

    # ARIMA con el orden elegido por AIC en la misma muestra del panel
    tpm = panel["tpm"].asfreq("MS")
    orden, _ = arima.seleccionar_orden(tpm)
    pronostico = arima.pronosticar(tpm, orden, horizonte)
    agregar("ARIMA", f"ARIMA{orden}", pronostico["tpm"].to_numpy(),
            pronostico["li"].to_numpy(), pronostico["ls"].to_numpy())

    # Benchmark: la TPM se queda en su último valor
    agregar(BENCHMARK, "Sin cambio", np.repeat(tpm_inicial, horizonte))

    return pd.concat(partes, ignore_index=True)


def resumen(proyecciones: pd.DataFrame, horizontes: list = HORIZONTES_RESUMEN) -> pd.DataFrame:
    """TPM proyectada por modelo y escenario en los horizontes indicados (columnas)."""
    elegidos = proyecciones[proyecciones["horizonte"].isin(horizontes)]
    return elegidos.pivot_table(index=["modelo", "escenario"], columns="horizonte",
                                values="tpm", sort=False)


def intervalo_arima(proyecciones: pd.DataFrame, horizontes: list = HORIZONTES_RESUMEN) -> pd.DataFrame:
    """Proyección del ARIMA y su intervalo de 80 % en los horizontes indicados."""
    tabla = proyecciones[(proyecciones["modelo"] == "ARIMA")
                         & proyecciones["horizonte"].isin(horizontes)]
    return tabla.set_index("horizonte")[["mes", "tpm", "li", "ls"]]


if __name__ == "__main__":
    print(punto_partida())
    proyecciones = proyectar()
    print(resumen(proyecciones).round(2))
    print(intervalo_arima(proyecciones).round(2))