"""
dashboard_tpm.py
----------------
Dashboard del monitor de la TPM, generado en Python desde la base del proyecto.

La guía del Hito 3 pide que el dashboard se genere con código a partir de la base
SQL y que se pueda regenerar sin pasos manuales. Este script lee SOLO desde
data/base.db (y desde sql/consultas.sql, a través de modelos/datos_modelo.py) y
produce tres láminas listas para la presentación y el informe:

  1. Coyuntura: indicadores clave (último dato y cambio en 12 meses) y la
     evolución de la TPM y sus determinantes desde 2015.
  2. Semáforo: estado de cada determinante respecto de su zona "normal",
     con reglas explícitas (ver REGLAS_SEMAFORO).
  3. Proyección: TPM efectiva, proyección a 24 meses por modelo y escenario
     (tabla proyecciones_tpm) y error fuera de muestra de cada modelo
     (tabla metricas_modelos).

Requisito: correr antes carga.py y modelos/proyeccion_escenarios.py
(python ejecutar_todo.py lo hace en orden).

Uso (desde la raíz del proyecto):
    python -m dashboard.dashboard_tpm
Resultados:
    salidas/dashboard/1_coyuntura.png
    salidas/dashboard/2_semaforo.png
    salidas/dashboard/3_proyeccion.png
"""

from __future__ import annotations

import sqlite3
import sys
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from modelos.tpm.datos_modelo import (RUTA_BD, META_INFLACION, brecha_tiempo_real,  # noqa: E402
                                  leer_consultas)

warnings.filterwarnings("ignore")

CARPETA = RAIZ / "salidas" / "dashboard"
DESDE = "2015-01-01"
FUENTE = "Fuente: BCCh y FRED, base del proyecto (corte 2026-09-30)."

# Paleta: colores fijos por serie (nunca se reasignan) y colores de estado reservados
TINTA, TINTA_2, GRILLA = "#191919", "#666666", "#e7e7e7"
AZUL, NARANJA, AQUA, AMARILLO, MAGENTA, VERDE, VIOLETA, ROJO = (
    "#257de0", "#f47230", "#00b894", "#f2a600", "#ee7fac", "#008a17", "#6a4ce2", "#ec4647")
ESTADO = {"En rango": ("#0aac23", "●"), "Atención": ("#fbb315", "▲"), "Alerta": ("#dc3c3d", "■")}

plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": GRILLA, "axes.labelcolor": TINTA_2,
    "xtick.color": TINTA_2, "ytick.color": TINTA_2, "axes.grid": True,
    "grid.color": GRILLA, "grid.linewidth": 0.6, "axes.spines.top": False,
    "axes.spines.right": False, "axes.titleweight": "bold", "axes.titlesize": 10,
    "axes.titlecolor": TINTA, "legend.frameon": False, "lines.linewidth": 2,
})


# ---------------------------------------------------------------------------
# Datos: todo desde la base
# ---------------------------------------------------------------------------
def cargar_datos():
    niveles, var12 = leer_consultas()
    brecha = brecha_tiempo_real(niveles["imacec"]).reindex(niveles.index)
    with sqlite3.connect(RUTA_BD) as con:
        tablas = {t for (t,) in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if not {"proyecciones_tpm", "metricas_modelos"} <= tablas:
            sys.exit("Faltan las tablas de proyecciones en la base: corre antes "
                     "python -m modelos.proyeccion_escenarios (o python ejecutar_todo.py).")
        proyecciones = pd.read_sql("SELECT * FROM proyecciones_tpm", con, parse_dates=["mes"])
        metricas = pd.read_sql("SELECT * FROM metricas_modelos", con)
    return niveles, var12, brecha, proyecciones, metricas


MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def mes(fecha: pd.Timestamp) -> str:
    """Fecha como 'sep-2026' (en español, sin depender del idioma del computador)."""
    return f"{MESES[fecha.month - 1]}-{fecha.year}"


def ultimo(serie: pd.Series) -> tuple[pd.Timestamp, float, float | None]:
    """Último dato disponible, su fecha y el valor 12 meses antes."""
    serie = serie.dropna()
    fecha = serie.index[-1]
    previo = fecha - pd.DateOffset(months=12)
    return fecha, float(serie.iloc[-1]), (float(serie.loc[previo]) if previo in serie.index else None)


# ---------------------------------------------------------------------------
# Semáforo: reglas explícitas
# ---------------------------------------------------------------------------
def regla_rango(x, verde, amarillo):
    """verde/amarillo = (mín, máx). Fuera de ambos rangos: alerta."""
    if verde[0] <= x <= verde[1]:
        return "En rango"
    if amarillo[0] <= x <= amarillo[1]:
        return "Atención"
    return "Alerta"


REGLAS_SEMAFORO = {
    # indicador: (cómo se mide, regla, texto de la regla)
    "Inflación IPC (12m, %)":      lambda x: regla_rango(x, (2, 4), (1, 5)),
    "Inflación SAE (12m, %)":      lambda x: regla_rango(x, (2, 4), (1, 5)),
    "Expectativa EEE 12m (%)":     lambda x: regla_rango(x, (2.75, 3.25), (2.25, 3.75)),
    "Brecha de actividad (%)":     lambda x: regla_rango(x, (-1, 1), (-2, 2)),
    "Desempleo (cambio 12m, pp)":  lambda x: regla_rango(x, (-9, 0.3), (-9, 1.0)),
    "Dólar (var. 12m, %)":         lambda x: regla_rango(x, (-5, 5), (-10, 10)),
    "Fed Funds (cambio 12m, pp)":  lambda x: regla_rango(x, (-0.5, 0.5), (-1.5, 1.5)),
}
TEXTO_REGLAS = ("Reglas: inflación (IPC y SAE) en el rango de tolerancia 2–4 % = en rango; 1–5 % = atención.  "
                "EEE a ±0,25 pp de la meta = en rango; ±0,75 pp = atención.\n"
                "Brecha ±1 % = en rango; ±2 % = atención.  Desempleo: alza en 12 meses ≤ 0,3 pp = en rango; "
                "≤ 1 pp = atención.  Dólar ±5 % = en rango; ±10 % = atención.  Fed Funds ±0,5 pp = en rango; "
                "±1,5 pp = atención.")


def tabla_semaforo(niveles, var12, brecha) -> pd.DataFrame:
    series = {
        "Inflación IPC (12m, %)": var12["ipc"],
        "Inflación SAE (12m, %)": var12["ipc_sae"],
        "Expectativa EEE 12m (%)": niveles["expectativa_ipc_eee"],
        "Brecha de actividad (%)": brecha,
        "Desempleo (cambio 12m, pp)": var12["desempleo"],
        "Dólar (var. 12m, %)": var12["dolar_observado"],
        "Fed Funds (cambio 12m, pp)": var12["fed_funds"],
    }
    filas = []
    for nombre, serie in series.items():
        fecha, valor, previo = ultimo(serie)
        estado = REGLAS_SEMAFORO[nombre](valor)
        filas.append({"Indicador": nombre, "Último dato": mes(fecha),
                      "Valor": valor, "Hace 12 meses": previo, "Estado": estado})
    return pd.DataFrame(filas)


# ---------------------------------------------------------------------------
# Lámina 1: coyuntura
# ---------------------------------------------------------------------------
def tile(ax, titulo, valor, detalle):
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), 1, 1, transform=ax.transAxes, facecolor="#f9f9f9",
                               edgecolor=GRILLA, linewidth=1))
    ax.text(0.06, 0.78, titulo, transform=ax.transAxes, color=TINTA_2, fontsize=9)
    ax.text(0.06, 0.36, valor, transform=ax.transAxes, color=TINTA, fontsize=20, fontweight="bold")
    ax.text(0.06, 0.12, detalle, transform=ax.transAxes, color=TINTA_2, fontsize=8)


def destacar_ultimo(ax, serie, formato="{:.2f}"):
    serie = serie.dropna()
    ax.plot(serie.index[-1], serie.iloc[-1], "o", color=ax.lines[-1].get_color(),
            markersize=6, markeredgecolor="white", markeredgewidth=1.5, zorder=5)
    ax.annotate(formato.format(serie.iloc[-1]), (serie.index[-1], serie.iloc[-1]),
                xytext=(6, 0), textcoords="offset points", va="center", color=TINTA, fontsize=8)


def lamina_coyuntura(niveles, var12, brecha, ruta):
    tpm = niveles["tpm"]
    f_tpm, v_tpm, p_tpm = ultimo(tpm)
    f_ipc, v_ipc, _ = ultimo(var12["ipc"])
    f_eee, v_eee, _ = ultimo(niveles["expectativa_ipc_eee"])
    f_br, v_br, _ = ultimo(brecha)
    f_us, v_us, _ = ultimo(var12["dolar_observado"])

    fig = plt.figure(figsize=(14, 8.4))
    grid = fig.add_gridspec(3, 5, height_ratios=[0.55, 1, 1], hspace=0.7, wspace=0.35)
    tiles = [
        ("TPM", f"{v_tpm:.2f} %", f"{mes(f_tpm)} · {v_tpm - p_tpm:+.2f} pp en 12 meses"),
        ("Inflación IPC 12m", f"{v_ipc:.1f} %", f"{mes(f_ipc)} · meta 3 %"),
        ("Expectativa EEE 12m", f"{v_eee:.1f} %", f"{mes(f_eee)} · {v_eee - META_INFLACION:+.2f} pp vs meta"),
        ("Brecha de actividad", f"{v_br:+.1f} %", f"{mes(f_br)} · HP en tiempo real"),
        ("Dólar observado", f"{v_us:+.1f} %", f"{mes(f_us)} · variación en 12 meses"),
    ]
    for i, (t, v, d) in enumerate(tiles):
        tile(fig.add_subplot(grid[0, i]), t, v, d)

    def panel(fila, col, ancho=1):
        ax = fig.add_subplot(grid[fila, col:col + ancho])
        # Paneles angostos: un año sí y tres no, para que las etiquetas no se monten
        ax.xaxis.set_major_locator(mdates.YearLocator(2 if ancho > 1 else 4))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        return ax

    # TPM y Fed Funds (misma unidad: % anual, un solo eje)
    ax = panel(1, 0, 2)
    ax.plot(tpm.loc[DESDE:], color=AZUL, label="TPM Chile")
    ax.plot(niveles["fed_funds"].loc[DESDE:], color=NARANJA, label="Fed Funds EE.UU.")
    destacar_ultimo(ax, tpm.loc[DESDE:])
    ax.set_title("TPM y tasa de la Fed (% anual)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=2)

    # Inflación con meta y rango
    ax = panel(1, 2, 2)
    ax.axhspan(2, 4, color=GRILLA, alpha=0.6, lw=0, label="Rango de tolerancia 2–4 %")
    ax.axhline(META_INFLACION, color=TINTA_2, lw=1, ls="--")
    ax.plot(var12["ipc"].loc[DESDE:], color=AZUL, label="IPC")
    ax.plot(var12["ipc_sae"].loc[DESDE:], color=NARANJA, label="IPC SAE")
    destacar_ultimo(ax, var12["ipc"].loc[DESDE:], "{:.1f}")
    ax.set_title("Inflación en 12 meses (%)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3)

    # Expectativas
    ax = panel(1, 4)
    ax.axhline(META_INFLACION, color=TINTA_2, lw=1, ls="--")
    ax.plot(niveles["expectativa_ipc_eee"].loc[DESDE:], color=AZUL)
    destacar_ultimo(ax, niveles["expectativa_ipc_eee"].loc[DESDE:], "{:.1f}")
    ax.set_title("Expectativa EEE a 12 meses (%)")

    # Brecha de actividad
    ax = panel(2, 0, 2)
    ax.axhline(0, color=TINTA_2, lw=1)
    ax.plot(brecha.loc[DESDE:], color=AZUL)
    destacar_ultimo(ax, brecha.loc[DESDE:], "{:+.1f}")
    ax.set_title("Brecha de actividad, HP en tiempo real (% sobre la tendencia)")

    # Dólar
    ax = panel(2, 2, 2)
    ax.axhline(0, color=TINTA_2, lw=1)
    ax.plot(var12["dolar_observado"].loc[DESDE:], color=AZUL)
    destacar_ultimo(ax, var12["dolar_observado"].loc[DESDE:], "{:+.1f}")
    ax.set_title("Dólar observado, variación en 12 meses (%)")

    # Desempleo
    ax = panel(2, 4)
    ax.plot(niveles["desempleo"].loc[DESDE:], color=AZUL)
    destacar_ultimo(ax, niveles["desempleo"].loc[DESDE:], "{:.1f}")
    ax.set_title("Desempleo (%)")

    fig.suptitle("Monitor de la TPM · 1. Coyuntura", x=0.06, ha="left", fontsize=14,
                 fontweight="bold", color=TINTA)
    fig.text(0.06, 0.015, FUENTE + " Punto = último dato.", color=TINTA_2, fontsize=8)
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Lámina 2: semáforo
# ---------------------------------------------------------------------------
def lamina_semaforo(tabla: pd.DataFrame, ruta):
    fig, ax = plt.subplots(figsize=(12, 0.62 * len(tabla) + 2.2))
    ax.axis("off")
    columnas = ["Indicador", "Último dato", "Valor", "Hace 12 meses", "Estado"]
    x = [0.0, 0.36, 0.52, 0.66, 0.82]
    alto = 1 / (len(tabla) + 1)
    for xi, c in zip(x, columnas):
        ax.text(xi, 1 - alto / 2, c, fontweight="bold", color=TINTA_2, va="center", fontsize=10)
    ax.axhline(1 - alto, color=TINTA_2, lw=0.8)
    for i, fila in tabla.iterrows():
        y = 1 - alto * (i + 1.5)
        color, icono = ESTADO[fila["Estado"]]
        previo = "—" if fila["Hace 12 meses"] is None or pd.isna(fila["Hace 12 meses"]) \
            else f"{fila['Hace 12 meses']:.2f}"
        valores = [fila["Indicador"], fila["Último dato"], f"{fila['Valor']:.2f}", previo]
        for xi, v in zip(x, valores):
            ax.text(xi, y, v, color=TINTA, va="center", fontsize=10)
        # Estado: ícono + etiqueta (el color nunca va solo)
        ax.text(x[4], y, f"{icono}  {fila['Estado']}", color=color, va="center",
                fontsize=11, fontweight="bold")
        ax.axhline(y - alto / 2, color=GRILLA, lw=0.6)
    fig.suptitle("Monitor de la TPM · 2. Semáforo de los determinantes", x=0.02, ha="left",
                 fontsize=14, fontweight="bold", color=TINTA)
    fig.text(0.02, -0.02, TEXTO_REGLAS + "\n" + FUENTE, color=TINTA_2, fontsize=8, va="top")
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Lámina 3: proyección y evaluación
# ---------------------------------------------------------------------------
def lamina_proyeccion(niveles, proyecciones, metricas, ruta):
    tpm = niveles["tpm"].dropna()
    historia = tpm.loc["2019-01-01":]
    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(15, 5.6), gridspec_kw={"width_ratios": [2.1, 1]})

    # Panel izquierdo: proyección
    ax.plot(historia, color=TINTA, label="TPM efectiva")
    arima = proyecciones[proyecciones["modelo"] == "ARIMA"].sort_values("mes")
    col_li = [c for c in arima.columns if c.startswith("li_")][0]
    col_ls = [c for c in arima.columns if c.startswith("ls_")][0]
    nivel = col_li.split("_")[1]
    ax.fill_between(arima["mes"], arima[col_li], arima[col_ls], color=AZUL, alpha=0.12, lw=0,
                    label=f"ARIMA: intervalo {nivel} %")
    ax.plot(arima["mes"], arima["tpm"], color=AZUL, label=arima["escenario"].iloc[0])
    estilos = {"Base": (NARANJA, "-"), "Convergencia": (VIOLETA, "--"),
               "Riesgo al alza": (ROJO, "--"), "Riesgo a la baja": (AQUA, "--")}
    finales = []
    for escenario, (color, ls) in estilos.items():
        datos = proyecciones[(proyecciones["modelo"] == "Regla de Taylor")
                             & (proyecciones["escenario"] == escenario)].sort_values("mes")
        ax.plot(datos["mes"], datos["tpm"], color=color, ls=ls, label=f"Taylor: {escenario}")
        finales.append((datos["tpm"].iloc[-1], datos["mes"].iloc[-1]))
    # Etiqueta del valor final de cada escenario, separando las que quedarían encimadas
    separacion = 0.03 * (ax.get_ylim()[1] - ax.get_ylim()[0])
    ultimo_y = -np.inf
    for valor, fecha in sorted(finales):
        y = max(valor, ultimo_y + separacion)
        ax.annotate(f"{valor:.2f}", (fecha, valor), xytext=(fecha, y), textcoords="data",
                    va="center", fontsize=8, color=TINTA)
        ultimo_y = y
    caminata = proyecciones[proyecciones["modelo"] == "Caminata aleatoria"].sort_values("mes")
    ax.plot(caminata["mes"], caminata["tpm"], color=TINTA_2, ls=":", label="Caminata aleatoria")
    ax.axvline(historia.index[-1], color=TINTA_2, lw=0.8, ls=":")
    ax.annotate(f"Último dato: {historia.iloc[-1]:.2f} % ({mes(historia.index[-1])})",
                (historia.index[-1], historia.iloc[-1]), xytext=(-175, 45), textcoords="offset points",
                arrowprops={"arrowstyle": "->", "color": TINTA_2}, fontsize=9, color=TINTA)
    ax.set_title("TPM efectiva y proyección a 24 meses (% anual)")
    ax.legend(fontsize=8, ncol=2, loc="upper right")

    # Panel derecho: error fuera de muestra (misma evaluación para los tres modelos)
    cortes = metricas[metricas["evaluacion"].str.startswith("Cortes")]
    tabla = cortes.pivot(index="horizonte", columns="modelo", values="rmse")
    modelos = [m for m in ["Caminata aleatoria", "Regla de Taylor", "ARIMA"] if m in tabla.columns]
    colores = {"Caminata aleatoria": "#9c9c9c", "Regla de Taylor": NARANJA, "ARIMA": AZUL}
    ancho = 0.8 / len(modelos)
    for i, modelo in enumerate(modelos):
        xs = np.arange(len(tabla)) + (i - (len(modelos) - 1) / 2) * ancho
        barras = ax2.bar(xs, tabla[modelo], ancho * 0.92, color=colores[modelo], label=modelo)
        ax2.bar_label(barras, fmt="%.2f", fontsize=8, color=TINTA)
    ax2.set_xticks(range(len(tabla)), [f"{h} meses" for h in tabla.index])
    ax2.set_title("Error de pronóstico fuera de muestra\n(RMSE en pp, cortes 2016–2024; menor es mejor)")
    ax2.grid(axis="x", visible=False)
    ax2.legend(fontsize=8, loc="upper left")

    fig.suptitle("Monitor de la TPM · 3. Proyección y desempeño de los modelos", x=0.06, ha="left",
                 fontsize=14, fontweight="bold", color=TINTA)
    fig.text(0.06, -0.02, FUENTE + " Escenarios ilustrativos; proyecciones condicionadas, "
             "no anuncios del Banco Central.", color=TINTA_2, fontsize=8)
    fig.tight_layout()
    fig.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    CARPETA.mkdir(parents=True, exist_ok=True)
    niveles, var12, brecha, proyecciones, metricas = cargar_datos()
    semaforo = tabla_semaforo(niveles, var12, brecha)

    lamina_coyuntura(niveles, var12, brecha, CARPETA / "1_coyuntura.png")
    lamina_semaforo(semaforo, CARPETA / "2_semaforo.png")
    lamina_proyeccion(niveles, proyecciones, metricas, CARPETA / "3_proyeccion.png")
    semaforo.round(2).to_csv(CARPETA / "semaforo.csv", index=False)

    print("Semáforo de los determinantes:\n")
    print(semaforo.round(2).to_string(index=False))
    print("\nDashboard generado en salidas/dashboard/: 1_coyuntura.png, 2_semaforo.png, "
          "3_proyeccion.png y semaforo.csv")
