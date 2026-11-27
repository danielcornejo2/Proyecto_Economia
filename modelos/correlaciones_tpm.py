"""
correlaciones_tpm.py
--------------------
correlaciones cruzadas y rezagos entre la TPM y sus determinantes.

Pregunta que responde: ¿qué variables se mueven ANTES que la TPM, con cuántos
meses de anticipación y en qué dirección? Eso conecta los datos con los
mecanismos de transmisión del Hito 1 (signo esperado y rezago de cada variable).

Decisión clave: NO se correlacionan niveles. La TPM, el dólar o el IPC en nivel
tienen tendencia, y dos series con tendencia aparecen correlacionadas aunque no
tengan relación (correlación espuria). Por eso se usan CAMBIOS EN 12 MESES,
que ya vienen calculados desde SQL (consulta 3 de sql/consultas.sql):
  - TPM: cambio en 12 meses, en puntos porcentuales.
  - Explicativas: variación en 12 meses (inflación, dólar, cobre, Imacec...).
  - Expectativas EEE: se usa su nivel menos la meta de 3 % (ya no tiene tendencia).

Para cada variable X y cada rezago k (0 a 24 meses) se calcula
    corr( cambio TPM en t , X en t-k )
Si la correlación más alta aparece en k = 6, X se mueve unos 6 meses antes que la TPM.

Uso (desde la raíz del proyecto):
    python modelos/correlaciones_tpm.py
Resultados:
    hito_3/resultados/correlaciones_tpm.csv   tabla completa (variable x rezago)
    hito_3/resultados/resumen_rezagos.csv     rezago de mayor correlación por variable
    hito_3/graficos/correlaciones_tpm.png     mapa de calor
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")            # guarda el gráfico en archivo, sin abrir ventanas
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from modelos.datos_modelo import leer_consultas, META_INFLACION  # noqa: E402

CARPETA_RESULTADOS = RAIZ / "hito_3" / "resultados"
CARPETA_GRAFICOS = RAIZ / "hito_3" / "graficos"
REZAGO_MAXIMO = 24

# Variable -> (nombre para mostrar, signo esperado según el Hito 1)
VARIABLES = {
    "ipc":             ("Inflación IPC (12m)",          "+"),
    "ipc_sae":         ("Inflación SAE (12m)",          "+"),
    "eee_brecha":      ("Expectativa EEE − meta",       "+"),
    "imacec":          ("Imacec (var. 12m)",            "+"),
    "desempleo":       ("Desempleo (cambio 12m, pp)",   "−"),
    "dolar_observado": ("Dólar (var. 12m)",             "+"),
    "precio_cobre":    ("Cobre (var. 12m)",             "+/−"),
    "fed_funds":       ("Fed Funds (cambio 12m, pp)",   "+"),
}


def preparar_series() -> tuple[pd.Series, pd.DataFrame]:
    """Devuelve el cambio en 12 meses de la TPM y la tabla de explicativas."""
    niveles, var12 = leer_consultas()
    tpm_12m = var12["tpm"].rename("tpm_12m")

    explicativas = var12[[c for c in VARIABLES if c in var12.columns]].copy()
    explicativas["eee_brecha"] = niveles["expectativa_ipc_eee"] - META_INFLACION
    return tpm_12m, explicativas[list(VARIABLES)]


def correlaciones_cruzadas(objetivo: pd.Series, explicativas: pd.DataFrame,
                           rezago_maximo: int = REZAGO_MAXIMO) -> pd.DataFrame:
    """
    Tabla con una fila por variable y una columna por rezago k:
    corr(objetivo en t, variable en t-k). Usa solo los meses con ambos datos.
    """
    tabla = {}
    for columna in explicativas:
        tabla[columna] = {
            k: objetivo.corr(explicativas[columna].shift(k))
            for k in range(rezago_maximo + 1)
        }
    return pd.DataFrame(tabla).T


def resumir(tabla: pd.DataFrame) -> pd.DataFrame:
    """Para cada variable: rezago con la correlación más fuerte (en valor absoluto)."""
    rezago = tabla.abs().idxmax(axis=1)
    resumen = pd.DataFrame({
        "variable": [VARIABLES[v][0] for v in tabla.index],
        "rezago_meses": rezago.values,
        "correlacion": [tabla.loc[v, k] for v, k in rezago.items()],
        "correlacion_rezago_0": tabla[0].values,
        "signo_esperado": [VARIABLES[v][1] for v in tabla.index],
    }, index=tabla.index)
    resumen["signo_observado"] = np.where(resumen["correlacion"] >= 0, "+", "−")
    return resumen.sort_values("correlacion", key=abs, ascending=False)


def graficar(tabla: pd.DataFrame, ruta: Path) -> None:
    """Mapa de calor: filas = variables, columnas = rezago en meses."""
    fig, ax = plt.subplots(figsize=(12, 4.8))
    imagen = ax.imshow(tabla.to_numpy(), cmap="RdBu_r", vmin=-1, vmax=1, aspect="auto")
    ax.set_yticks(range(len(tabla)), [VARIABLES[v][0] for v in tabla.index])
    ax.set_xticks(range(0, tabla.shape[1], 2), range(0, tabla.shape[1], 2))
    ax.set_xlabel("Rezago k (meses): la variable se mide k meses antes que la TPM")

    # Marca con un punto el rezago de mayor correlación de cada variable
    for fila, variable in enumerate(tabla.index):
        ax.plot(tabla.loc[variable].abs().idxmax(), fila, "ko", ms=4)

    fig.colorbar(imagen, ax=ax, label="Correlación")
    ax.set_title("Correlación entre el cambio en 12 meses de la TPM y sus determinantes rezagados\n"
                 "Fuente: BCCh y FRED, base del proyecto. Punto negro = rezago de mayor correlación.",
                 fontsize=10)
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    CARPETA_RESULTADOS.mkdir(parents=True, exist_ok=True)
    CARPETA_GRAFICOS.mkdir(parents=True, exist_ok=True)

    tpm_12m, explicativas = preparar_series()
    tabla = correlaciones_cruzadas(tpm_12m, explicativas)
    resumen = resumir(tabla)

    tabla.round(3).to_csv(CARPETA_RESULTADOS / "correlaciones_tpm.csv")
    resumen.round(3).to_csv(CARPETA_RESULTADOS / "resumen_rezagos.csv")
    graficar(tabla, CARPETA_GRAFICOS / "correlaciones_tpm.png")

    print("Rezago de mayor correlación con el cambio en 12 meses de la TPM:\n")
    print(resumen.round(2).to_string(index=False))
    print(f"\nArchivos guardados en {CARPETA_RESULTADOS.relative_to(RAIZ)} "
          f"y {CARPETA_GRAFICOS.relative_to(RAIZ)}")