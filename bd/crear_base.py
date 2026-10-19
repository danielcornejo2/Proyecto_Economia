

from __future__ import annotations

import argparse
import logging
import os
import sqlite3
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------

RAIZ = Path(__file__).resolve().parent.parent          # carpeta raíz del proyecto
CARPETA_DATOS = RAIZ / "data" / "raw"                  # CSV de la extracción
RUTA_BASE = RAIZ / "data" / "base.db"                  # base de datos de salida

# Subcarpeta de data/raw/ -> nombre de la fuente en la base
FUENTES = {"bcch": "BCCh", "fred": "FRED"}

COLUMNAS_CSV = {"fecha", "valor", "serie", "codigo"}   # columnas que escriben los extractores

log = logging.getLogger("crear_base")


@dataclass(frozen=True)
class MetaSerie:
    """Metadatos de una serie que no vienen en el CSV."""

    fuente: str        # 'BCCh' o 'FRED'
    frecuencia: str    # frecuencia original en la API (en la base todo queda mensual)
    tema: str          # debe existir en TEMAS
    tipo: str          # 'tasa', 'indice', 'nivel' o 'variacion': define la transformación correcta
    unidad: str
    descripcion: str


# Clasificación temática de los indicadores: {tema: descripción}
TEMAS = {
    "Política monetaria": "Instrumento de política del Banco Central (variable objetivo)",
    "Precios": "Inflación total y subyacente",
    "Expectativas": "Expectativas de inflación de encuestas",
    "Actividad": "Actividad económica agregada",
    "Mercado laboral": "Empleo y desempleo",
    "Tipo de cambio": "Paridad peso/dólar",
    "Tasas de mercado": "Tasas de bonos y depósitos del mercado financiero",
    "Externo": "Entorno internacional: EE.UU. y materias primas",
}

# Catálogo de series: la llave es el nombre corto (igual que en SERIES de los extractores
# y que el nombre del CSV). El código de la API se toma del propio CSV al cargar.
CATALOGO = {
    # ----- Banco Central de Chile -----
    "tpm": MetaSerie("BCCh", "Mensual", "Política monetaria", "tasa", "% anual",
                     "Tasa de política monetaria, promedio mensual"),
    "ipc": MetaSerie("BCCh", "Mensual", "Precios", "variacion", "% variación mensual",
                     "IPC general, variación mensual"),
    "ipc_sae": MetaSerie("BCCh", "Mensual", "Precios", "variacion", "% variación mensual",
                         "IPC sin alimentos ni energía, variación mensual empalmada (INE, base 2023)"),
    "imacec": MetaSerie("BCCh", "Mensual", "Actividad", "indice", "índice 2018=100",
                        "Imacec, índice original, referencia 2018"),
    "dolar_observado": MetaSerie("BCCh", "Mensual", "Tipo de cambio", "nivel", "pesos por dólar",
                                 "Dólar observado, promedio mensual"),
    "expectativa_ipc_eee": MetaSerie("BCCh", "Mensual", "Expectativas", "tasa", "%",
                                     "Expectativa de inflación a 12 meses (EEE), mediana"),
    "tasa_bcp_10": MetaSerie("BCCh", "Diaria", "Tasas de mercado", "tasa", "% anual",
                             "Tasa de mercado secundario, bonos en pesos a 10 años (BCP/BTP)"),
    "tasa_bcu_10": MetaSerie("BCCh", "Diaria", "Tasas de mercado", "tasa", "% anual (en UF)",
                             "Tasa de mercado secundario, bonos en UF a 10 años (BCU/BTU)"),
    "tasa_depositos_90d": MetaSerie("BCCh", "Diaria", "Tasas de mercado", "tasa", "% anual",
                                    "Tasa de depósitos en bolsa a 90 días, pesos, mercado secundario"),
    "desempleo": MetaSerie("BCCh", "Mensual", "Mercado laboral", "tasa", "% de la fuerza de trabajo",
                           "Tasa de desocupación nacional, INE"),
    # ----- FRED -----
    "precio_cobre": MetaSerie("FRED", "Mensual", "Externo", "nivel", "dólares por tonelada métrica",
                              "Precio internacional del cobre (FMI)"),
    "fed_funds": MetaSerie("FRED", "Mensual", "Externo", "tasa", "% anual",
                           "Tasa de fondos federales de EE.UU., promedio mensual"),
    "ipc_eeuu": MetaSerie("FRED", "Mensual", "Externo", "indice", "índice 1982-84=100",
                          "IPC de EE.UU. (CPI-U), desestacionalizado"),
    "produccion_industrial_eeuu": MetaSerie("FRED", "Mensual", "Externo", "indice", "índice 2017=100",
                                            "Producción industrial de EE.UU., desestacionalizada"),
}

# ---------------------------------------------------------------------------
# Esquema SQL
# ---------------------------------------------------------------------------
ESQUEMA_SQL = """
PRAGMA foreign_keys = ON;

-- Clasificación temática de los indicadores
CREATE TABLE temas (
    id_tema     INTEGER PRIMARY KEY,
    tema        TEXT    NOT NULL UNIQUE,
    descripcion TEXT
);

-- Catálogo de series: una fila por serie
CREATE TABLE series (
    id_serie    INTEGER PRIMARY KEY,
    nombre      TEXT    NOT NULL UNIQUE,            -- nombre corto (= nombre del CSV)
    codigo      TEXT    NOT NULL,                   -- código de la serie en la API
    fuente      TEXT    NOT NULL CHECK (fuente IN ('BCCh', 'FRED')),
    frecuencia  TEXT    NOT NULL                    -- frecuencia original en la API
                CHECK (frecuencia IN ('Diaria', 'Quincenal', 'Mensual', 'Trimestral', 'Anual')),
    tipo        TEXT    NOT NULL CHECK (tipo IN ('tasa', 'indice', 'nivel', 'variacion')),
    unidad      TEXT    NOT NULL,
    descripcion TEXT    NOT NULL,
    id_tema     INTEGER NOT NULL REFERENCES temas (id_tema),
    UNIQUE (fuente, codigo)
);

-- Observaciones mensuales: una fila por serie y mes
--   fecha: texto 'AAAA-MM-DD', siempre el día 1 del mes. El CHECK rechaza fechas inválidas
--          (date() devuelve NULL si la fecha no existe) y fechas que no sean día 01.
--   valor: NULL cuando la API no entregó dato para ese mes (no se rellena ni se elimina).
CREATE TABLE observaciones (
    id_serie INTEGER NOT NULL REFERENCES series (id_serie),
    fecha    TEXT    NOT NULL
             CHECK (date(fecha) IS NOT NULL AND date(fecha) = fecha AND substr(fecha, 9, 2) = '01'),
    valor    REAL,
    PRIMARY KEY (id_serie, fecha)
);

CREATE INDEX idx_observaciones_fecha ON observaciones (fecha);
CREATE INDEX idx_series_tema ON series (id_tema);

-- Vista de consolidación: cada observación con su serie y su tema
CREATE VIEW v_observaciones AS
SELECT t.tema,
       s.id_serie,
       s.nombre,
       s.frecuencia,
       o.fecha,
       o.valor
FROM observaciones AS o
JOIN series        AS s ON s.id_serie = o.id_serie
JOIN temas         AS t ON t.id_tema  = s.id_tema;
"""

# Consulta de revisión de la guía del Hito 2 (etapa 3): una fila por tema y serie
CONSULTA_REVISION = """
SELECT t.tema,
       s.nombre,
       s.frecuencia,
       COUNT(o.valor) AS n_obs,
       MIN(o.fecha)   AS desde,
       MAX(o.fecha)   AS hasta
FROM temas AS t
LEFT JOIN series        AS s ON s.id_tema  = t.id_tema
LEFT JOIN observaciones AS o ON o.id_serie = s.id_serie
GROUP BY t.tema, s.nombre
ORDER BY t.tema, n_obs;
"""


class CSVInvalido(Exception):
    """El CSV no tiene el formato que escriben los scripts de extracción."""


# ---------------------------------------------------------------------------
# Lectura y validación de los CSV
# ---------------------------------------------------------------------------
def validar_catalogo() -> None:
    """Verifica que cada serie del catálogo apunte a un tema existente."""
    temas_desconocidos = {m.tema for m in CATALOGO.values()} - TEMAS.keys()
    if temas_desconocidos:
        raise ValueError(f"Temas del CATALOGO que no están en TEMAS: {sorted(temas_desconocidos)}")


def listar_csv(carpeta_datos: Path) -> list[tuple[Path, str]]:
    """Devuelve [(ruta_csv, fuente)] de todas las subcarpetas de fuentes conocidas."""
    archivos = []
    for subcarpeta, fuente in FUENTES.items():
        archivos += [(ruta, fuente) for ruta in sorted((carpeta_datos / subcarpeta).glob("*.csv"))]
    return archivos


def leer_csv(ruta: Path) -> pd.DataFrame:
    """
    Lee y valida un CSV de la extracción. Devuelve columnas fecha ('AAAA-MM-DD'), valor,
    serie y codigo. Lanza CSVInvalido si el archivo no cumple el formato esperado.
    """
    df = pd.read_csv(ruta)

    faltantes = COLUMNAS_CSV - set(df.columns)
    if faltantes:
        raise CSVInvalido(f"faltan las columnas {sorted(faltantes)}")
    if df.empty:
        raise CSVInvalido("el archivo no tiene filas")
    if df["serie"].nunique() != 1 or df["serie"].iloc[0] != ruta.stem:
        raise CSVInvalido(f"la columna 'serie' debe ser '{ruta.stem}' en todas las filas")
    if df["codigo"].nunique() != 1:
        raise CSVInvalido("la columna 'codigo' tiene más de un valor")

    fechas = pd.to_datetime(df["fecha"], format="%Y-%m-%d", errors="coerce")
    if fechas.isna().any():
        raise CSVInvalido("hay fechas que no tienen el formato AAAA-MM-DD")
    if fechas.duplicated().any():
        raise CSVInvalido("hay fechas repetidas")

    valores = pd.to_numeric(df["valor"], errors="coerce")
    no_numericos = valores.isna() & df["valor"].notna()
    if no_numericos.any():
        raise CSVInvalido(f"hay {int(no_numericos.sum())} valores que no son números")

    return pd.DataFrame({
        "fecha": fechas.dt.strftime("%Y-%m-%d"),
        "valor": valores,
        "serie": df["serie"],
        "codigo": df["codigo"].astype(str),
    }).sort_values("fecha", ignore_index=True)


# ---------------------------------------------------------------------------
# Escritura en la base
# ---------------------------------------------------------------------------
def insertar_temas(con: sqlite3.Connection) -> dict[str, int]:
    """Inserta los temas y devuelve {tema: id_tema}."""
    con.executemany(
        "INSERT INTO temas (tema, descripcion) VALUES (?, ?)",
        TEMAS.items(),
    )
    return dict(con.execute("SELECT tema, id_tema FROM temas"))


def insertar_serie(con: sqlite3.Connection, nombre: str, codigo: str, meta: MetaSerie,
                   id_tema: int) -> int:
    """Inserta una serie del catálogo y devuelve su id_serie."""
    cursor = con.execute(
        """
        INSERT INTO series (nombre, codigo, fuente, frecuencia, tipo, unidad, descripcion, id_tema)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (nombre, codigo, meta.fuente, meta.frecuencia, meta.tipo, meta.unidad,
         meta.descripcion, id_tema),
    )
    return cursor.lastrowid


def insertar_observaciones(con: sqlite3.Connection, id_serie: int, df: pd.DataFrame) -> None:
    """Inserta las observaciones de una serie; los NaN se guardan como NULL."""
    filas = (
        (id_serie, fecha, None if pd.isna(valor) else float(valor))
        for fecha, valor in zip(df["fecha"], df["valor"])
    )
    con.executemany("INSERT INTO observaciones (id_serie, fecha, valor) VALUES (?, ?, ?)", filas)


def verificar_integridad(con: sqlite3.Connection) -> None:
    """Comprueba la integridad del archivo y que no haya llaves foráneas rotas."""
    if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        raise RuntimeError("PRAGMA integrity_check falló")
    rotas = con.execute("PRAGMA foreign_key_check").fetchall()
    if rotas:
        raise RuntimeError(f"Hay {len(rotas)} filas con llaves foráneas inválidas")


def construir_base(carpeta_datos: Path, ruta_base: Path) -> list[str]:
    """
    Construye la base completa en un archivo temporal y, si todo sale bien, reemplaza
    la base anterior. Devuelve la lista de problemas encontrados (vacía si no hubo).
    """
    validar_catalogo()
    archivos = listar_csv(carpeta_datos)
    if not archivos:
        raise FileNotFoundError(
            f"No hay CSV en {carpeta_datos}. Primero ejecuta los scripts de extraccion/."
        )

    problemas: list[str] = []
    ruta_base.parent.mkdir(parents=True, exist_ok=True)
    ruta_temporal = ruta_base.with_suffix(".tmp")
    ruta_temporal.unlink(missing_ok=True)

    con = sqlite3.connect(ruta_temporal)
    try:
        con.executescript(ESQUEMA_SQL)           # crea tablas, índices y vista
        con.execute("PRAGMA foreign_keys = ON")
        with con:                                # una sola transacción: todo o nada
            ids_tema = insertar_temas(con)
            cargadas = set()
            for ruta, fuente in archivos:
                nombre = ruta.stem
                meta = CATALOGO.get(nombre)
                if meta is None:
                    problemas.append(f"{ruta.name}: no está en CATALOGO, no se cargó")
                    continue
                if meta.fuente != fuente:
                    problemas.append(f"{ruta.name}: está en la carpeta de {fuente}, "
                                     f"pero el CATALOGO dice {meta.fuente}; no se cargó")
                    continue
                try:
                    df = leer_csv(ruta)
                except CSVInvalido as e:
                    problemas.append(f"{ruta.name}: {e}; no se cargó")
                    continue

                id_serie = insertar_serie(con, nombre, df["codigo"].iloc[0], meta, ids_tema[meta.tema])
                insertar_observaciones(con, id_serie, df)
                cargadas.add(nombre)
                log.info("[OK] %-28s %4d meses  %3d sin dato  %s a %s", nombre, len(df),
                         df["valor"].isna().sum(), df["fecha"].iloc[0][:7], df["fecha"].iloc[-1][:7])

            for nombre in sorted(CATALOGO.keys() - cargadas):
                if not any(p.startswith(f"{nombre}.csv") for p in problemas):
                    problemas.append(f"{nombre}: está en CATALOGO pero no hay CSV (¿falló la extracción?)")

        verificar_integridad(con)
    except Exception:
        con.close()
        ruta_temporal.unlink(missing_ok=True)
        raise
    con.close()

    os.replace(ruta_temporal, ruta_base)        # reemplazo atómico de la base anterior
    return problemas


def mostrar_resumen(ruta_base: Path) -> None:
    """Imprime la consulta de revisión de la guía: series, observaciones y fechas por tema."""
    with sqlite3.connect(ruta_base) as con:
        resumen = pd.read_sql_query(CONSULTA_REVISION, con)
    print("\nRevisión de la base (temas -> series -> observaciones):")
    print(resumen.to_string(index=False))


def main() -> int:
    parser = argparse.ArgumentParser(description="Crea data/base.db a partir de los CSV de data/raw/.")
    parser.add_argument("--datos", type=Path, default=CARPETA_DATOS,
                        help="carpeta con las subcarpetas bcch/ y fred/ (por defecto data/raw)")
    parser.add_argument("--salida", type=Path, default=RUTA_BASE,
                        help="ruta de la base de datos (por defecto data/base.db)")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
    try:
        problemas = construir_base(args.datos, args.salida)
    except Exception as e:                      # error grave: la base anterior no se toca
        log.error("[ERROR] No se pudo crear la base: %s", e)
        return 1

    mostrar_resumen(args.salida)
    print(f"\nBase creada en {args.salida}")
    if problemas:
        print("\nProblemas encontrados:")
        for problema in problemas:
            print(f"  [ERROR] {problema}")
        return 1
    print("Sin problemas: todas las series del catálogo quedaron cargadas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
