"""
proyeccion_escenarios.py
------------------------
proyección de la TPM a 24 meses con escenarios de riesgo, y carga de
proyecciones y métricas a data/base.db (hito de sincronización del plan).

1) Regla de Taylor estimada con toda la muestra, en cuatro escenarios para sus
   determinantes (se aplican desde el primer mes proyectado):
   - Base: determinantes constantes en su último valor (igual que proyeccion_taylor.py).
   - Convergencia: las expectativas vuelven a la meta de 3 % y la brecha de
     actividad se cierra, ambas de forma lineal en 12 meses (Fed Funds constante).
   - Riesgo al alza: las expectativas suben 1 pp sobre la meta (por ejemplo, por
     una depreciación del peso o un shock de petróleo) y la Fed sube 0,5 pp.
   - Riesgo a la baja: la actividad cae 2 pp bajo su tendencia (recesión global),
     las expectativas bajan 0,5 pp y la Fed recorta 1 pp.
   Los tamaños de los shocks son ilustrativos: sirven para mostrar hacia dónde y
   cuánto se mueve la TPM según la regla, no son pronósticos de esas variables.

2) ARIMA de la TPM (orden elegido por AIC con toda la muestra) con su intervalo
   de confianza de 80 %: muestra la incertidumbre del pronóstico.

3) Caminata aleatoria: la TPM se queda en su último valor (benchmark).

4) Se guardan en data/base.db dos tablas nuevas, que se recrean en cada ejecución:
   - proyecciones_tpm(fecha_corte, mes, horizonte, modelo, escenario, tpm, li_80, ls_80)
   - metricas_modelos(evaluacion, horizonte, modelo, mae, rmse, r2_oos, n)
   Así el dashboard y el informe leen todo desde la base, sin archivos sueltos.
   Como carga.py vuelve a crear la base desde cero, este script debe correr
   DESPUÉS de carga.py y de las evaluaciones (ejecutar_todo.py ya lo hace).

Uso (desde la raíz del proyecto):
    python -m modelos.proyeccion_escenarios
Resultados:
    hito_3/resultados/proyeccion_escenarios.csv
    hito_3/graficos/proyeccion_escenarios.png
    tablas proyecciones_tpm y metricas_modelos en data/base.db
"""

from __future__ import annotations

import sqlite3
import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from modelos.arima_tpm import elegir_orden  # noqa: E402
from modelos.datos_modelo import RUTA_BD, armar_panel  # noqa: E402
from modelos.regla_taylor import estimar_regla_taylor  # noqa: E402

warnings.filterwarnings("ignore")

HORIZONTE = 24
PISO_TPM = 0.5   # mínimo histórico de la TPM (2020): el intervalo no baja de ese nivel
DETERMINANTES = ["brecha_inflacion_esp", "brecha_actividad", "fed_funds"]


def trayectorias_determinantes(ultimo: pd.Series) -> dict[str, pd.DataFrame]:
    """Valor de cada determinante en los 24 meses proyectados, por escenario."""
    meses = np.arange(1, HORIZONTE + 1)
    base = pd.DataFrame({v: np.repeat(ultimo[v], HORIZONTE) for v in DETERMINANTES}, index=meses)

    convergencia = base.copy()
    peso = np.clip(1 - meses / 12, 0, None)            # 1 -> 0 en 12 meses
    convergencia["brecha_inflacion_esp"] = ultimo["brecha_inflacion_esp"] * peso
    convergencia["brecha_actividad"] = ultimo["brecha_actividad"] * peso

    alza = base.copy()
    alza["brecha_inflacion_esp"] += 1.0
    alza["fed_funds"] += 0.5

    baja = base.copy()
    baja["brecha_actividad"] -= 2.0
    baja["brecha_inflacion_esp"] -= 0.5
    baja["fed_funds"] -= 1.0

    return {"Base": base, "Convergencia": convergencia,
            "Riesgo al alza": alza, "Riesgo a la baja": baja}


def proyectar_taylor(coef: pd.Series, tpm_inicial: float, determinantes: pd.DataFrame) -> list[float]:
    """Proyección recursiva: la TPM proyectada es el rezago del mes siguiente."""
    tpm, trayectoria = tpm_inicial, []
    for _, fila in determinantes.iterrows():
        tpm = (float(coef["constante"]) + float(coef["tpm_lag1"]) * tpm
               + sum(float(coef[v]) * float(fila[v]) for v in DETERMINANTES))
        trayectoria.append(tpm)
    return trayectoria


def guardar_en_bd(proyecciones: pd.DataFrame, ruta_bd: Path = RUTA_BD) -> pd.DataFrame:
    """Recrea las tablas de proyecciones y métricas dentro de la base del proyecto."""
    carpeta = RAIZ / "hito_3" / "resultados"
    metricas = []
    fuentes = {
        "Cortes sep-2016 a sep-2024": ("comparacion_modelos_resumen.csv", "cortes"),
        "Ene-2025 a sep-2026 (ARIMA)": ("evaluacion_arima_metricas.csv", "meses_evaluados"),
    }
    for evaluacion, (archivo, columna_n) in fuentes.items():
        ruta = carpeta / archivo
        if not ruta.exists():
            print(f"  Aviso: no existe {archivo}; corre antes la evaluación correspondiente.")
            continue
        tabla = pd.read_csv(ruta)
        metricas.append(pd.DataFrame({
            "evaluacion": evaluacion, "horizonte": tabla["horizonte_meses"],
            "modelo": tabla["modelo"], "mae": tabla["MAE"], "rmse": tabla["RMSE"],
            "r2_oos": tabla["R2_OOS_vs_caminata"], "n": tabla[columna_n]}))
    metricas = pd.concat(metricas, ignore_index=True) if metricas else pd.DataFrame()

    with sqlite3.connect(ruta_bd) as con:
        con.executescript("""
            DROP TABLE IF EXISTS proyecciones_tpm;
            CREATE TABLE proyecciones_tpm (
                fecha_corte TEXT    NOT NULL,   -- último mes con dato al proyectar
                mes         TEXT    NOT NULL,   -- mes proyectado (AAAA-MM-01)
                horizonte   INTEGER NOT NULL,   -- meses adelante (1 a 24)
                modelo      TEXT    NOT NULL,   -- Regla de Taylor, ARIMA, Caminata aleatoria
                escenario   TEXT    NOT NULL,   -- Base, Convergencia, Riesgo al alza, ...
                tpm         REAL    NOT NULL,   -- TPM proyectada (% anual)
                li_80       REAL,               -- límite inferior del intervalo (solo ARIMA)
                ls_80       REAL,               -- límite superior del intervalo (solo ARIMA)
                PRIMARY KEY (fecha_corte, mes, modelo, escenario)
            );
            DROP TABLE IF EXISTS metricas_modelos;
            CREATE TABLE metricas_modelos (
                evaluacion TEXT    NOT NULL,    -- diseño de la evaluación fuera de muestra
                horizonte  INTEGER NOT NULL,    -- meses adelante
                modelo     TEXT    NOT NULL,
                mae        REAL,
                rmse       REAL,
                r2_oos     REAL,                -- frente a la caminata aleatoria
                n          INTEGER,             -- pronósticos evaluados
                PRIMARY KEY (evaluacion, horizonte, modelo)
            );
        """)
        proyecciones.to_sql("proyecciones_tpm", con, if_exists="append", index=False)
        if not metricas.empty:
            metricas.to_sql("metricas_modelos", con, if_exists="append", index=False)
    return metricas


def graficar(tpm: pd.Series, proyecciones: pd.DataFrame, ruta: Path) -> None:
    historia = tpm.loc["2019-01-01":]
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(historia.index, historia, color="black", lw=2, label="TPM efectiva")

    arima = proyecciones[proyecciones["modelo"] == "ARIMA"]
    meses_arima = pd.to_datetime(arima["mes"])
    ax.fill_between(meses_arima, arima["li_80"], arima["ls_80"], color="#1f77b4", alpha=0.15,
                    label="ARIMA: intervalo 80 %")
    ax.plot(meses_arima, arima["tpm"], color="#1f77b4", lw=2, label=arima["escenario"].iloc[0])

    colores = {"Base": "#d62728", "Convergencia": "#9467bd",
               "Riesgo al alza": "#ff7f0e", "Riesgo a la baja": "#2ca02c"}
    for escenario, color in colores.items():
        datos = proyecciones[(proyecciones["modelo"] == "Regla de Taylor")
                             & (proyecciones["escenario"] == escenario)]
        ax.plot(pd.to_datetime(datos["mes"]), datos["tpm"], color=color, lw=1.6,
                ls="-" if escenario == "Base" else "--", label=f"Taylor: {escenario}")

    caminata = proyecciones[proyecciones["modelo"] == "Caminata aleatoria"]
    ax.plot(pd.to_datetime(caminata["mes"]), caminata["tpm"], color="grey", ls=":", lw=1.5,
            label="Caminata aleatoria")

    ax.axvline(historia.index[-1], color="grey", lw=0.8, ls=":")
    ultimo = historia.iloc[-1]
    ax.annotate(f"Último dato: {ultimo:.2f} % ({historia.index[-1]:%b-%Y})",
                (historia.index[-1], ultimo), xytext=(-170, 40), textcoords="offset points",
                arrowprops={"arrowstyle": "->", "color": "grey"}, fontsize=9)
    ax.set_ylabel("TPM (% anual)")
    ax.set_title("TPM de Chile: proyección a 24 meses por modelo y escenario\n"
                 "Fuente: BCCh y FRED, base del proyecto. Escenarios ilustrativos.", fontsize=10)
    ax.legend(fontsize=8, ncol=2, loc="upper right")
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    panel = armar_panel()
    corte = panel.index.max()
    ultimo = panel.loc[corte]
    tpm_inicial = float(ultimo["tpm"])
    meses = pd.date_range(corte + pd.offsets.MonthBegin(1), periods=HORIZONTE, freq="MS")
    filas = []

    def agregar(modelo, escenario, valores, li=None, ls=None):
        for h, (mes, valor) in enumerate(zip(meses, valores), start=1):
            filas.append({"fecha_corte": f"{corte:%Y-%m-%d}", "mes": f"{mes:%Y-%m-%d}",
                          "horizonte": h, "modelo": modelo, "escenario": escenario,
                          "tpm": float(valor),
                          "li_80": None if li is None else float(li[h - 1]),
                          "ls_80": None if ls is None else float(ls[h - 1])})

    # 1) Regla de Taylor por escenario
    coef, _ = estimar_regla_taylor(panel, f"{corte:%Y-%m-%d}")
    for escenario, determinantes in trayectorias_determinantes(ultimo).items():
        agregar("Regla de Taylor", escenario, proyectar_taylor(coef, tpm_inicial, determinantes))

    # 2) ARIMA con intervalo de 80 %
    tpm = panel["tpm"].asfreq("MS")
    orden, _ = elegir_orden(tpm)
    pronostico = ARIMA(tpm, order=orden).fit().get_forecast(steps=HORIZONTE).summary_frame(alpha=0.20)
    agregar("ARIMA", f"ARIMA{orden}", pronostico["mean"].to_numpy(),
            np.maximum(pronostico["mean_ci_lower"].to_numpy(), PISO_TPM), pronostico["mean_ci_upper"].to_numpy())

    # 3) Caminata aleatoria
    agregar("Caminata aleatoria", "Sin cambio", np.repeat(tpm_inicial, HORIZONTE))

    proyecciones = pd.DataFrame(filas)
    carpeta_res = RAIZ / "hito_3" / "resultados"
    carpeta_graf = RAIZ / "hito_3" / "graficos"
    carpeta_res.mkdir(parents=True, exist_ok=True)
    carpeta_graf.mkdir(parents=True, exist_ok=True)
    proyecciones.round(4).to_csv(carpeta_res / "proyeccion_escenarios.csv", index=False)
    graficar(tpm, proyecciones, carpeta_graf / "proyeccion_escenarios.png")
    metricas = guardar_en_bd(proyecciones)

    resumen = (proyecciones[proyecciones["horizonte"].isin([6, 12, 24])]
               .assign(nombre=lambda d: d["modelo"] + " - " + d["escenario"])
               .pivot(index="nombre", columns="horizonte", values="tpm"))
    resumen.columns = [f"{h} meses" for h in resumen.columns]
    print(f"TPM al corte ({corte:%Y-%m}): {tpm_inicial:.2f} %\n")
    print("TPM proyectada (% anual):")
    print(resumen.round(2).to_string())
    arima = proyecciones[proyecciones["modelo"] == "ARIMA"].set_index("horizonte")
    for h in (6, 12, 24):
        print(f"  Intervalo 80 % del ARIMA a {h} meses: "
              f"{arima.loc[h, 'li_80']:.2f} % a {arima.loc[h, 'ls_80']:.2f} %")
    print(f"\nGuardado en data/base.db: proyecciones_tpm ({len(proyecciones)} filas) y "
          f"metricas_modelos ({len(metricas)} filas).")
    print("Archivos: hito_3/resultados/proyeccion_escenarios.csv y "
          "hito_3/graficos/proyeccion_escenarios.png")