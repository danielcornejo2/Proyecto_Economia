"""
datos_modelo.py
---------------
Armamos el panel mensual con el que se estiman y evalúan los modelos de la TPM
(regla de Taylor, ARIMA/SARIMA y benchmark ingenuo).

Idea central: cada fila t debe contener SOLO información que el Banco Central
(o un analista) tenía disponible al cierre del mes t-1. Si usamos un dato que
todavía no se publicaba, el pronóstico "fuera de muestra" quedaría
artificialmente bueno (sesgo de anticipación o look-ahead bias).

Para eso se toman dos decisiones:
  1. Rezagos de publicación: cada variable entra rezagada según cuándo se publica.
  2. Brecha de actividad en tiempo real: el filtro HP se recalcula en cada mes
     usando solo los datos de ese momento (filtro "de una cola").

Las transformaciones que ya hace SQL (promedio mensual y variación en 12 meses)
se leen desde sql/consultas.sql y NO se recalculan en Python.

Uso desde la raíz del proyecto:
    python modelos/datos_modelo.py
Uso desde un notebook:
    from modelos.datos_modelo import armar_panel
    panel = armar_panel()
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Configuramos
# ---------------------------------------------------------------------------
RAIZ = Path(__file__).resolve().parent.parent
RUTA_BD = RAIZ / "data" / "base.db"
RUTA_SQL = RAIZ / "sql" / "consultas.sql"

META_INFLACION = 3.0     # meta del BCCh: 3 % anual
LAMBDA_HP = 14_400       # valor estándar del filtro HP para datos mensuales
MESES_MINIMOS_HP = 60    # 5 años mínimos de historia antes de calcular la primera brecha

# Rezago de publicación (en meses) de cada serie, visto desde el cierre del mes t-1.
# Ejemplo: para pronosticar la TPM de octubre, al 30 de septiembre:
#   - la TPM, la EEE, la Fed Funds y el dólar de septiembre ya se conocen  -> rezago 1
#   - el IPC de septiembre se publica el 8 de octubre: solo se conoce el de agosto -> rezago 2
#   - el Imacec de agosto se publica el 1 de octubre: solo se conoce el de julio -> rezago 3
REZAGO_PUBLICACION = {
    "tpm": 1,
    "expectativa_ipc_eee": 1,
    "fed_funds": 1,
    "dolar_observado": 1,
    "ipc": 2,
    "ipc_sae": 2,
    "desempleo": 2,
    "precio_cobre": 2,
    "imacec": 3,
}


# ---------------------------------------------------------------------------
# 1. Lectura desde la base (las consultas viven en sql/consultas.sql)
# ---------------------------------------------------------------------------
def leer_consultas(ruta_bd: Path = RUTA_BD, ruta_sql: Path = RUTA_SQL):
    """
    Ejecuta las consultas 2 (GROUP BY mensual) y 3 (variación en 12 meses)
    del archivo sql/consultas.sql y devuelve dos tablas en formato ancho:
    una fila por mes y una columna por serie.
    """
    if not Path(ruta_bd).exists():
        raise FileNotFoundError(
            f"No existe {ruta_bd}. Primero corre 'python carga.py' para crear la base."
        )

    bloques = [q.strip() for q in Path(ruta_sql).read_text(encoding="utf-8").split(";") if q.strip()]
    q_mensual, q_variacion = bloques[1], bloques[2]

    with sqlite3.connect(ruta_bd) as con:
        mensual = pd.read_sql(q_mensual, con)
        variacion = pd.read_sql(q_variacion, con)

    niveles = mensual.pivot(index="mes", columns="nombre", values="valor_mensual")
    var12 = variacion.pivot(index="mes", columns="nombre", values="variacion_12m")

    # 'AAAA-MM' -> fecha del primer día del mes, con frecuencia mensual explícita
    for tabla in (niveles, var12):
        tabla.index = pd.PeriodIndex(tabla.index, freq="M").to_timestamp()
        tabla.sort_index(inplace=True)

    return niveles.asfreq("MS"), var12.asfreq("MS")


# ---------------------------------------------------------------------------
# 2. Brecha de actividad
# ---------------------------------------------------------------------------
def filtro_hp(y: np.ndarray, lamb: float = LAMBDA_HP) -> np.ndarray:
    """
    Filtro de Hodrick-Prescott (misma implementación del notebook de coyuntura).
    Resuelve (I + lambda K'K) tendencia = y, con K la matriz de segundas diferencias.
    Devuelve el ciclo: y - tendencia.
    """
    y = np.asarray(y, dtype=float)
    n = len(y)
    K = np.zeros((n - 2, n))
    for i in range(n - 2):
        K[i, i:i + 3] = [1.0, -2.0, 1.0]
    tendencia = np.linalg.solve(np.eye(n) + lamb * K.T @ K, y)
    return y - tendencia


def desestacionalizar_log(log_y: pd.Series) -> pd.Series:
    """
    Quita la estacionalidad a log(Imacec) con el método de razón a media móvil.

    Solo usa la serie que recibe: si se le entrega la historia hasta el mes t,
    los factores estacionales se estiman con datos hasta t (no mira el futuro).
    En logaritmos el método es aditivo: log(SA) = log(y) - factor del mes.
    """
    # Media móvil centrada 2x12: mide el nivel "sin estacionalidad" de cada mes.
    # Necesita 6 meses hacia adelante, así que para los últimos 6 meses queda NaN
    # y esos meses no participan en el cálculo de los factores.
    media_movil = log_y.rolling(12, center=True).mean().rolling(2).mean().shift(-1)
    desvio = log_y - media_movil

    # Factor de cada mes calendario = promedio de sus desvíos, centrado en cero
    factor_mes = desvio.groupby(desvio.index.month).mean()
    factor_mes -= factor_mes.mean()

    return log_y - log_y.index.month.map(factor_mes).to_numpy()


def brecha_ex_post(imacec: pd.Series) -> pd.Series:
    """
    Brecha con TODA la muestra (filtro HP de dos colas), en % respecto de la tendencia.
    Sirve para describir el pasado (diagnóstico de coyuntura), NO para pronosticar:
    la brecha de 2015 calculada así usa datos de 2016 en adelante.
    """
    log_sa = desestacionalizar_log(100 * np.log(imacec.dropna()))
    return pd.Series(filtro_hp(log_sa.to_numpy()), index=log_sa.index, name="brecha_ex_post")


def brecha_tiempo_real(imacec: pd.Series, minimo: int = MESES_MINIMOS_HP) -> pd.Series:
    """
    Brecha de actividad en tiempo real (filtro HP de una cola).

    Para cada mes t se toma el Imacec SOLO hasta t, se desestacionaliza, se aplica
    el filtro HP y se guarda el último valor del ciclo. Así la brecha del mes t es
    la que un analista habría calculado en ese momento, sin conocer el futuro.
    """
    log_y = 100 * np.log(imacec.dropna())
    valores = {}
    for fin in range(minimo, len(log_y) + 1):
        historia = log_y.iloc[:fin]
        log_sa = desestacionalizar_log(historia)
        valores[historia.index[-1]] = filtro_hp(log_sa.to_numpy())[-1]
    return pd.Series(valores, name="brecha_tiempo_real")


# ---------------------------------------------------------------------------
# 3. Panel para los modelos
# ---------------------------------------------------------------------------
# DESPUÉS
def armar_panel(ruta_bd: Path = RUTA_BD, eliminar_faltantes: bool = True,
                incluir_mes_siguiente: bool = False) -> pd.DataFrame:
    """
    Devuelve el panel mensual de modelación. En la fila t:
    tpm                   TPM de fin del mes t (variable a pronosticar)
      tpm_lag1              TPM del mes anterior (componente inercial de la regla)
      brecha_inflacion_esp  expectativa de inflación a 12 meses (EEE) menos la meta de 3 %
      inflacion_12m         inflación anual del IPC (calculada en SQL)
      brecha_actividad      brecha del Imacec en tiempo real, en %
      fed_funds             tasa de fondos federales de EE.UU.
      dolar_12m             variación anual del dólar observado (calculada en SQL)
    Todas las explicativas ya vienen rezagadas según REZAGO_PUBLICACION.
    """
    niveles, var12 = leer_consultas(ruta_bd)

    if incluir_mes_siguiente:
        # Se agrega una fila vacía para el mes siguiente al último dato. Al aplicar los
        # rezagos de publicación, esa fila queda con lo que se sabe al cierre del último
        # mes: es la fila con la que se pronostica (ver fila_pronostico).
        siguiente = niveles.index.max() + pd.offsets.MonthBegin(1)
        indice = niveles.index.append(pd.DatetimeIndex([siguiente]))
        niveles, var12 = niveles.reindex(indice), var12.reindex(indice)

    def disponible(serie: pd.Series, nombre: str) -> pd.Series:
        """Desplaza la serie según cuándo se publica (ver REZAGO_PUBLICACION)."""
        return serie.shift(REZAGO_PUBLICACION[nombre])

    brecha = brecha_tiempo_real(niveles["imacec"]).reindex(niveles.index)

    panel = pd.DataFrame({
        "tpm": niveles["tpm"],
        "tpm_lag1": disponible(niveles["tpm"], "tpm"),
        "brecha_inflacion_esp": disponible(niveles["expectativa_ipc_eee"] - META_INFLACION,
                                           "expectativa_ipc_eee"),
        "inflacion_12m": disponible(var12["ipc"], "ipc"),
        "brecha_actividad": disponible(brecha, "imacec"),
        "fed_funds": disponible(niveles["fed_funds"], "fed_funds"),
        "dolar_12m": disponible(var12["dolar_observado"], "dolar_observado"),
    })

    if eliminar_faltantes:
        # Se pierden los primeros meses (antes de tener 5 años de Imacec) y los meses
        # sin EEE. No se rellenan: inventar un dato también contaminaría la estimación.
        panel = panel.dropna()
    return panel

def fila_pronostico(ruta_bd: Path = RUTA_BD) -> pd.Series:
    """
    Fila del primer mes a pronosticar: el mes siguiente al último dato (el corte).

    La última fila de armar_panel() es la del corte, y por construcción solo trae lo
    que se conocía al cierre del mes ANTERIOR al corte. Para proyectar desde el corte
    hay que usar todo lo que se sabe al cierre del corte, así que se arma la fila del
    mes siguiente con los mismos rezagos de publicación.
    Con corte en sep-2026 la fila es oct-2026: EEE y Fed Funds de septiembre, brecha
    de julio (el Imacec se publica con 3 meses de rezago) y TPM de septiembre como
    tpm_lag1. La columna tpm queda vacía: es justamente lo que se va a pronosticar.
    """
    fila = armar_panel(ruta_bd, eliminar_faltantes=False, incluir_mes_siguiente=True).iloc[-1]
    necesarias = ["tpm_lag1", "brecha_inflacion_esp", "brecha_actividad", "fed_funds"]
    faltantes = [c for c in necesarias if pd.isna(fila[c])]
    if faltantes:
        raise ValueError(f"Faltan datos al cierre del corte para: {faltantes}")
    return fila


# ---------------------------------------------------------------------------
# Ejecución directa: revisión rápida del panel
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    panel = armar_panel()
    print(f"Panel de modelación: {len(panel)} meses, "
          f"de {panel.index.min():%Y-%m} a {panel.index.max():%Y-%m}\n")
    print(panel.tail(6).round(2).to_string())

    # Comparación que conviene mostrar en el informe: la brecha ex post (dos colas)
    # versus la de tiempo real. La diferencia es lo que se "vería del futuro".
    niveles, _ = leer_consultas()
    comparacion = pd.concat([brecha_ex_post(niveles["imacec"]),
                             brecha_tiempo_real(niveles["imacec"])], axis=1).dropna()
    print("\nBrecha ex post vs tiempo real (últimos 6 meses, %):")
    print(comparacion.tail(6).round(2).to_string())
    print(f"\nCorrelación entre ambas: {comparacion.corr().iloc[0, 1]:.2f}")