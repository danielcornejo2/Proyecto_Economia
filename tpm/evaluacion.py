"""
evaluacion.py
-------------
Evaluaciones fuera de muestra, todas sin sesgo de anticipación: cada modelo se
estima solo con los datos disponibles en el momento del pronóstico.
Cada función devuelve el detalle (una fila por pronóstico) y la tabla de métricas.
"""

from __future__ import annotations

import pandas as pd

from tpm import arima, taylor
from tpm.metricas import BENCHMARK, tabla_metricas

CORTES_ANUALES = [pd.Timestamp(f"{anio}-09-01") for anio in range(2016, 2025)]
HORIZONTES_LARGOS = [6, 12, 24]
FIN_ENTRENAMIENTO = "2024-12-01"
INICIO_RECIENTE, FIN_RECIENTE = "2025-01-01", "2026-09-01"
HORIZONTES_RECIENTES = [1, 6, 12]
CORTES_VALIDACION = ["2021-12-01", "2022-12-01", "2023-12-01", "2024-12-01"]
MESES_VALIDACION = 12


def evaluar_cortes(panel: pd.DataFrame, cortes: list = CORTES_ANUALES,
                   horizontes: list = HORIZONTES_LARGOS):
    """
    Comparación principal: regla de Taylor, ARIMA y caminata aleatoria con el mismo diseño.
    En cada corte se estima con datos hasta el corte y se pronostica a 6, 12 y 24 meses.
      - Taylor: parte de la TPM del corte y usa la fila siguiente del panel, que contiene
        lo que se sabía al cierre del corte; los determinantes quedan fijos.
      - ARIMA: orden elegido una sola vez con datos hasta el primer corte.
    Devuelve (detalle, métricas, orden del ARIMA).
    """
    tpm = panel["tpm"].asfreq("MS")
    orden, _ = arima.seleccionar_orden(tpm.loc[:cortes[0]])
    pasos = max(horizontes)
    filas = []
    for corte in cortes:
        coef = taylor.coeficientes(taylor.estimar(panel, corte))
        fila_siguiente = panel.loc[corte + pd.offsets.MonthBegin(1)]
        determinantes = pd.DataFrame([fila_siguiente[taylor.DETERMINANTES]] * pasos)
        tpm_corte = float(panel.loc[corte, "tpm"])
        ruta_taylor = taylor.proyectar(coef, tpm_corte, determinantes)
        ruta_arima = arima.pronosticar(tpm.loc[:corte], orden, pasos)["tpm"].to_numpy()

        for h in horizontes:
            objetivo = corte + pd.DateOffset(months=h)
            if objetivo not in tpm.index or pd.isna(tpm.loc[objetivo]):
                continue   # el horizonte cae después del último dato
            filas.append({"corte": corte, "horizonte": h, "mes_objetivo": objetivo,
                          "tpm_real": tpm.loc[objetivo], BENCHMARK: tpm_corte,
                          "Regla de Taylor": ruta_taylor[h - 1], "ARIMA": ruta_arima[h - 1]})

    detalle = pd.DataFrame(filas)
    metricas = tabla_metricas(detalle, [BENCHMARK, "Regla de Taylor", "ARIMA"])
    return detalle, metricas, orden


def evaluar_un_paso(panel: pd.DataFrame, fin_entrenamiento: str = FIN_ENTRENAMIENTO,
                    inicio: str = INICIO_RECIENTE, fin: str = FIN_RECIENTE):
    """
    Regla de Taylor a un mes: coeficientes estimados hasta 'fin_entrenamiento' y un
    pronóstico por mes entre 'inicio' y 'fin', con la TPM observada del mes anterior.
    Benchmark: la TPM del mes anterior. Devuelve (detalle, métricas).
    """
    coef = taylor.coeficientes(taylor.estimar(panel, fin_entrenamiento))
    prueba = panel.loc[inicio:fin]
    detalle = pd.DataFrame({
        "tpm_real": prueba["tpm"],
        "Regla de Taylor": taylor.pronostico_un_paso(coef, prueba),
        BENCHMARK: prueba["tpm_lag1"],
    })
    detalle["error_taylor"] = detalle["tpm_real"] - detalle["Regla de Taylor"]
    detalle["error_caminata"] = detalle["tpm_real"] - detalle[BENCHMARK]
    metricas = tabla_metricas(detalle, ["Regla de Taylor", BENCHMARK], por=None)
    return detalle, metricas


def validacion_temporal(panel: pd.DataFrame, cortes: list = CORTES_VALIDACION,
                        meses: int = MESES_VALIDACION):
    """
    Repite la evaluación a un mes con varios cortes: se reestima en cada corte y se
    evalúan los 'meses' siguientes. Devuelve (detalle, métricas por corte).
    """
    partes = []
    for corte in cortes:
        inicio = pd.Timestamp(corte) + pd.DateOffset(months=1)
        fin = inicio + pd.DateOffset(months=meses - 1)
        if len(panel.loc[inicio:fin]) != meses:
            continue   # el período de prueba está incompleto
        detalle, _ = evaluar_un_paso(panel, corte, inicio, fin)
        partes.append(detalle.assign(corte=pd.Timestamp(corte)))

    detalle = pd.concat(partes)
    metricas = tabla_metricas(detalle, ["Regla de Taylor", BENCHMARK], por="corte")
    return detalle, metricas


def evaluar_arima_reciente(tpm: pd.Series | None = None, inicio: str = INICIO_RECIENTE,
                           fin: str = FIN_RECIENTE, horizontes: list = HORIZONTES_RECIENTES):
    """
    ARIMA con d = 1 y, como robustez, con d = 0, frente a la caminata aleatoria.
    Los órdenes se eligen una vez con datos hasta el primer origen de pronóstico
    (12 meses antes de 'inicio'). Para cada mes objetivo y horizonte se reestima con
    los datos hasta el origen. Devuelve (detalle, métricas, órdenes).
    """
    tpm = arima.cargar_tpm() if tpm is None else tpm
    primer_origen = pd.Timestamp(inicio) - pd.DateOffset(months=max(horizontes))
    entrenamiento = tpm.loc[:primer_origen]
    ordenes = {}
    for d in (1, 0):
        orden, _ = arima.seleccionar_orden(entrenamiento, d=d)
        ordenes[f"ARIMA{orden}"] = orden

    filas = []
    for h in horizontes:
        for objetivo in tpm.loc[inicio:fin].index:
            origen = objetivo - pd.DateOffset(months=h)
            historia = tpm.loc[:origen]
            fila = {"horizonte": h, "mes_objetivo": objetivo, "origen": origen,
                    "tpm_real": tpm.loc[objetivo], BENCHMARK: historia.iloc[-1]}
            for nombre, orden in ordenes.items():
                fila[nombre] = arima.pronosticar(historia, orden, h)["tpm"].iloc[-1]
            filas.append(fila)

    detalle = pd.DataFrame(filas)
    metricas = tabla_metricas(detalle, [BENCHMARK] + list(ordenes))
    return detalle, metricas, ordenes


if __name__ == "__main__":
    from modelos.datos_modelo import armar_panel

    _, metricas, orden = evaluar_cortes(armar_panel())
    print(f"ARIMA{orden}\n", metricas.round(3))