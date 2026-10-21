# La TPM en Chile: monitor de coyuntura y proyección con una regla de política monetaria

**Proyecto del curso Ciencia de Datos para la Economía (ICO09425), Facultad de Administración y Economía, Universidad Diego Portales.**

**Profesor:** Luis Cuevas

**Integrantes:** Daniel Cornejo, Catarí Garrido, Laura Ruiz, Francisca Silva

> Este trabajo es un ejercicio académico; las proyecciones no representan pronósticos oficiales ni recomendaciones de política o de inversión.

---

## Contenido

1. [Resumen del avance (Hito 2)](#resumen-del-avance-hito-2)
2. [Contexto y pregunta de proyección](#contexto-y-pregunta-de-proyección)
3. [Arquitectura del flujo de trabajo](#arquitectura-del-flujo-de-trabajo)
4. [Datos](#datos)
5. [Base de datos](#base-de-datos)
6. [Consultas SQL](#consultas-sql)
7. [Análisis de coyuntura inicial](#análisis-de-coyuntura-inicial)
8. [Cómo reproducir el proyecto](#cómo-reproducir-el-proyecto)
9. [Estructura del repositorio](#estructura-del-repositorio)
10. [Trabajo en equipo con Git](#trabajo-en-equipo-con-git)
11. [Hitos del proyecto](#hitos-del-proyecto)
12. [Metodología prevista para la proyección](#metodología-prevista-para-la-proyección)
13. [Referencias](#referencias)

---

## Resumen del avance (Hito 2)

| Requisito de la pauta | Dónde está | Estado |
|---|---|---|
| Extracción programática de 12 o más series reales, con un solo comando | `carga.py` (usa `extraccion/E_BCCH.py` y `extraccion/E_FRED.py`) | 13 series del BCCh y FRED |
| Credenciales fuera del código | `.env` local, creado desde `.env.example` (no se sube) | ✓ |
| Base relacional con 3 o más tablas, llaves primarias y foráneas | `bd/crear_base.py` → `data/base.db` (`temas`, `series`, `observaciones`) | ✓ |
| Consultas SQL comentadas con JOIN, GROUP BY y función de ventana | `sql/consultas.sql` | ✓ |
| README, `requirements.txt` y entrega con tag | Este archivo, `requirements.txt` y tag `hito-2` | ✓ |

**Fecha de corte de los datos:** `2026-09-30`. Todos los resultados de este README corresponden a esa fecha.

---

## Contexto y pregunta de proyección

La Tasa de Política Monetaria (TPM) es el principal instrumento del Banco Central de Chile (BCCh) para cumplir su meta de inflación de 3 %. Sus cambios se transmiten a las tasas de mercado, al tipo de cambio, a la demanda y a las expectativas, y con ello a la actividad y a la inflación (Banco Central de Chile, 2020). En los últimos años la TPM llegó a un máximo de 11,25 % (2022–2023) y luego bajó a 4,5 %.

**Variable objetivo:** TPM, promedio mensual (% anual), serie `F022.TPM.TIN.D001.NO.Z.M` del BCCh.

**Horizonte:** 6 a 24 meses.

**Pregunta que guía el trabajo:**

> ¿Cuál es la trayectoria esperada de la TPM en Chile durante los próximos 6 a 24 meses, según la evolución de sus principales determinantes macroeconómicos y una regla de política monetaria estimada con datos chilenos?

---

## Arquitectura del flujo de trabajo

Todo el flujo es programático: no hay descargas manuales ni pasos intermedios a mano.

```
APIs (BCCh + FRED) ──▶ CSV en data/raw/ ──▶ SQLite data/base.db ──▶ sql/consultas.sql ──▶ notebooks/ (Python) ──▶ Power BI
   extraccion/*.py                           bd/crear_base.py         JOIN · GROUP BY ·                            (Hito 3)
                                                                       función de ventana
└──────────────────── carga.py ejecuta las tres primeras etapas con un solo comando ────────────────────┘
```

---

## Datos

### Catálogo de series

Se usan **13 series**, todas descargadas por API: 9 desde la Base de Datos Estadísticos del Banco Central de Chile (servicio SieteRestWS) y 4 desde FRED (Reserva Federal de St. Louis). La justificación de cada serie también está comentada junto a su código en `extraccion/E_BCCH.py` y `extraccion/E_FRED.py`.

| # | Nombre | Serie | Código API | Fuente | Frec. original | Tema | Período | Meses con dato |
|---|---|---|---|---|---|---|---|---|
| 1 | `tpm` | Tasa de política monetaria | `F022.TPM.TIN.D001.NO.Z.M` | BCCh | Mensual | Política monetaria | 2000-01 a 2026-09 | 321 |
| 2 | `ipc` | IPC general, variación mensual | `F074.IPC.VAR.Z.Z.C.M` | BCCh | Mensual | Precios | 2000-01 a 2026-09 | 321 |
| 3 | `ipc_sae` | IPC sin alimentos ni energía, variación mensual empalmada (INE, base 2023) | `F074.IPCSAE.VAR.Z.EP23.Z.M` | BCCh | Mensual | Precios | 2010-01 a 2026-09 | 201 |
| 4 | `expectativa_ipc_eee` | Expectativa de inflación a 12 meses (EEE), mediana | `F089.IPC.V12.14.M` | BCCh | Mensual | Expectativas | 2001-01 a 2026-09 | 302 |
| 5 | `imacec` | Imacec, índice original (referencia 2018) | `F032.IMC.IND.Z.Z.EP18.Z.Z.0.M` | BCCh | Mensual | Actividad | 2000-01 a 2026-08 | 320 |
| 6 | `desempleo` | Tasa de desocupación nacional (INE) | `F049.DES.TAS.INE9.10.M` | BCCh | Mensual | Mercado laboral | 2010-03 a 2026-08 | 198 |
| 7 | `dolar_observado` | Dólar observado, promedio mensual | `F073.TCO.PRE.HIST.M` | BCCh | Mensual | Tipo de cambio | 2000-01 a 2026-09 | 321 |
| 8 | `tasa_bcp_10` | Tasa de bonos en pesos a 10 años, mercado secundario | `F022.BCLP.TIS.AN10.NO.Z.D` | BCCh | Diaria | Tasas de mercado | 2004-07 a 2026-09 | 267 |
| 9 | `tasa_bcu_10` | Tasa de bonos en UF a 10 años, mercado secundario | `F022.BUF.TIS.AN10.UF.Z.D` | BCCh | Diaria | Tasas de mercado | 2002-09 a 2026-09 | 289 |
| 10 | `precio_cobre` | Precio internacional del cobre (FMI) | `PCOPPUSDM` | FRED | Mensual | Externo | 2000-01 a 2026-07 | 319 |
| 11 | `fed_funds` | Tasa de fondos federales de EE.UU. | `FEDFUNDS` | FRED | Mensual | Externo | 2000-01 a 2026-09 | 321 |
| 12 | `ipc_eeuu` | IPC de EE.UU. (CPI-U), desestacionalizado | `CPIAUCSL` | FRED | Mensual | Externo | 2000-01 a 2026-09 | 320 |
| 13 | `produccion_industrial_eeuu` | Producción industrial de EE.UU., desestacionalizada | `INDPRO` | FRED | Mensual | Externo | 2000-01 a 2026-09 | 321 |

### Por qué está cada serie

| Serie | Rol | Mecanismo y signo esperado sobre la TPM |
|---|---|---|
| `tpm` | Objetivo | La TPM se ajusta de forma gradual: su propio pasado la explica (inercia). |
| `ipc` | Explicativa | Si la inflación se aleja de la meta de 3 %, el BCCh mueve la TPM en la misma dirección (+). Se publica con rezago: en los modelos se usará rezagada. |
| `ipc_sae` | Explicativa | Inflación subyacente, sin los precios más volátiles: si sube, la presión es persistente (+). |
| `expectativa_ipc_eee` | Explicativa | La regla de Taylor responde a la inflación esperada (+). Se conoce antes que el IPC. |
| `imacec` | Explicativa | Con el filtro HP se obtiene la brecha de actividad: una economía sobre su potencial presiona la inflación (+). |
| `desempleo` | Explicativa | Más holgura laboral implica menos presión salarial e inflacionaria (−). |
| `dolar_observado` | Explicativa | Canal cambiario: una depreciación encarece los importados y eleva la inflación (+). |
| `fed_funds` | Explicativa | Un alza de la Fed amplía el diferencial de tasas y presiona al peso (+). |
| `ipc_eeuu` | Contexto | Inflación externa que entra por los bienes importados (+). |
| `precio_cobre` | Contexto | Términos de intercambio: aprecia el peso (−) pero impulsa la actividad (+); efecto ambiguo. |
| `produccion_industrial_eeuu` | Contexto | Ciclo de la demanda externa (+ leve). |
| `tasa_bcp_10`, `tasa_bcu_10` | Contexto | Transmisión de la TPM a las tasas nominales y reales de largo plazo. |

### Tratamiento de fechas, frecuencias, faltantes y errores

- **Fecha de corte:** `2026-09-30`, definida en `carga.py` (`FECHA_CORTE`) y modificable con `--hasta`. Se descartan los datos posteriores, para que el resultado sea reproducible.
- **Inicio:** se pide desde `2000-01-01`; cada serie parte en su primer dato disponible.
- **Frecuencia:** todo se guarda mensual, con fecha el día 1 del mes. Las series diarias (tasas de bonos) se convierten a promedio mensual en Python, con la función `a_mensual` de los scripts de extracción, antes de cargarse a la base.
- **Datos faltantes:** los meses sin dato se guardan como `NULL`; no se rellenan ni se eliminan. A la fecha de corte hay 8: 7 de la EEE y 1 del IPC de EE.UU.
- **Rezagos de publicación:** el Imacec y la desocupación llegan a 2026-08 y el cobre a 2026-07.
- **Historia:** todas las series tienen al menos 10 años de datos mensuales. Las más cortas son el IPC SAE (empalmado por el INE, desde 2010-01) y la desocupación (desde 2010-03).
- **Errores:** cada descarga se reintenta hasta 3 veces. Si una serie falla, se informa como `[ERROR]` y **la base no se crea**, para no mezclar datos nuevos con CSV de una descarga anterior. Sin conexión, el proceso se detiene. En FRED, una API key inválida detiene la descarga y el error 429 (exceso de consultas) hace esperar antes de reintentar.
- **Credenciales:** se leen desde `.env` y se reemplazan por `***` en cualquier mensaje de error.

### Datos reales, no sintéticos

El proyecto no usa datos de prueba: no existe una opción `--demo`, y la base solo se llena desde las APIs. Una forma rápida de comprobarlo es revisar los rangos: en la base, la TPM va de 0,5 % a 11,25 % y la desocupación de 5,8 % a 13,1 %, valores consistentes con la historia chilena.

---

## Base de datos

Base SQLite `data/base.db`, creada por `bd/crear_base.py`:

| Tabla | Contenido | Llaves |
|---|---|---|
| `temas` | Clasificación temática (8 temas) | PK `id_tema` |
| `series` | Catálogo: nombre, código API, fuente, frecuencia original, tipo (`tasa`, `indice`, `nivel`, `variacion`), unidad, descripción y tema (13 series) | PK `id_serie`; FK `id_tema` → `temas`; único (`fuente`, `codigo`) |
| `observaciones` | Una fila por serie y mes (3.829 filas) | PK (`id_serie`, `fecha`); FK `id_serie` → `series` |

La vista `v_observaciones` une las tres tablas (tema, serie, frecuencia, fecha y valor).

**Controles de calidad de la carga:**

- Cada CSV se valida antes de insertarse: columnas, fechas `AAAA-MM-DD` sin duplicados, valores numéricos y nombre de serie igual al nombre del archivo.
- La base tiene restricciones `CHECK`: fechas válidas y siempre día 01, fuente, frecuencia y tipo dentro de los valores permitidos.
- La llave primaria (`id_serie`, `fecha`) impide observaciones duplicadas, y la llave foránea impide observaciones de series que no están en el catálogo.
- La base se construye en un archivo temporal, en una sola transacción. Se verifica con `PRAGMA integrity_check` y `PRAGMA foreign_key_check` y solo entonces reemplaza a la anterior.
- Al terminar, `carga.py` muestra la consulta de revisión de la guía (tema → serie → número de observaciones, desde y hasta), para detectar series vacías, descontinuadas o con poca historia.

---

## Consultas SQL

Archivo `sql/consultas.sql`, con tres consultas comentadas. El notebook las lee desde el archivo y las ejecuta con `pd.read_sql`: la variación en 12 meses no se recalcula en Python.

| # | Qué entrega | Técnica SQL |
|---|---|---|
| 1 | Cada observación con el nombre, tipo, unidad y frecuencia de su serie y su tema (panel completo) | `JOIN` entre `observaciones`, `series` y `temas` |
| 2 | Valor de cada serie por mes (`AVG`) y número de observaciones válidas en el mes (`COUNT`). Como los datos ya se guardan mensuales, `n_obs` funciona como control de calidad: 1 = un dato por serie y mes, 0 = mes sin dato | `JOIN` + `GROUP BY` |
| 3 | Variación en 12 meses de cada serie según su tipo: índices y niveles → variación %; tasas → diferencia en puntos porcentuales; series que ya son variación mensual (IPC, IPC SAE) → inflación compuesta de los últimos 12 meses | Funciones de ventana `LAG` y `SUM … OVER`, con `PARTITION BY id_serie ORDER BY mes` |

**Decisiones de la función de ventana:**

- `PARTITION BY id_serie` impide que el valor "de hace 12 filas" pertenezca a otra serie.
- La ventana trabaja sobre series ya mensuales: 12 filas atrás son 12 meses atrás. Esto supone que no faltan meses; se cumple porque la conversión a mensual crea una fila por cada mes, aunque su valor sea `NULL`.
- A una tasa no se le calcula variación porcentual: pasar de 5 % a 6 % se informa como +1 punto porcentual, no como +20 %.

**Ejecutar las consultas sin abrir el notebook** (desde la raíz del proyecto, con el entorno activado):

```bash
python -c "import sqlite3; con = sqlite3.connect('data/base.db'); [print(f'Consulta {i}:', len(con.execute(q).fetchall()), 'filas') for i, q in enumerate(open('sql/consultas.sql', encoding='utf-8').read().split(';'), 1) if q.strip()]"
```

Con la fecha de corte 2026-09-30, cada consulta entrega 3.829 filas.

---

## Análisis de coyuntura inicial

El notebook `notebooks/02_analisis_coyuntura.ipynb` lee las consultas, aplica las transformaciones y construye cinco gráficos, cada uno con título, unidad, fuente, período y una lectura económica:

1. Tasa de Política Monetaria.
2. Inflación anual total y subyacente (SAE) frente a la meta de 3 % y su rango de tolerancia (2–4 %).
3. Imacec desestacionalizado, tendencia HP y brecha de actividad, en paneles separados.
4. Tipo de cambio nominal y expectativas de inflación a 12 meses (EEE).
5. Tipo de cambio nominal y real (índice, base 100 = promedio del período).

| Transformación | Cómo se hace | Dónde |
|---|---|---|
| Variación en 12 meses | Según el tipo de serie (ver consulta 3) | SQL |
| Desestacionalización del Imacec | Razón a media móvil: promedio móvil centrado de 12 meses y factor estacional promedio por mes, normalizado a 1 | Notebook |
| Brecha de actividad | Filtro de Hodrick-Prescott sobre `100 · log(Imacec desestacionalizado)`, λ = 14.400, implementado con `numpy` | Notebook |
| Tipo de cambio real | TCN × IPC EE.UU. / IPC Chile (el IPC chileno se encadena a índice desde su variación mensual) | Notebook |

### Principales hallazgos (datos a septiembre de 2026)

- **TPM:** 4,5 %, 6,75 puntos porcentuales bajo su máximo de 11,25 % (2022–2023) y estable en los últimos meses.
- **Inflación:** el IPC total crece 4,2 % anual, en el límite superior del rango de tolerancia; el IPC SAE, 3,4 %. La presión se concentra en los componentes volátiles y no en una presión de demanda generalizada.
- **Actividad:** la brecha HP promedia −1,5 % en el último trimestre (se usa el promedio porque el filtro es inestable en el extremo de la muestra). La economía opera bajo su potencial.
- **Tipo de cambio:** el peso sigue débil en perspectiva histórica, pero en 12 meses se apreció 1,4 % en términos nominales y 2,5 % en términos reales.
- **Expectativas:** la EEE a 12 meses está en 3,3 %, levemente sobre la meta.

**Lectura:** el diagnóstico apunta a un shock de oferta. En la regla de Taylor los dos términos tiran en direcciones opuestas: la inflación pide una TPM más alta y la brecha negativa una más baja. Eso es consistente con que el BCCh mantenga la tasa en 4,5 %, mientras las expectativas de mediano plazo sigan ancladas.

---

## Cómo reproducir el proyecto

### Requisitos

- **Python 3.9 o superior** (se desarrolló con Python 3.14). Verificar con `python3 --version` (Mac/Linux) o `python --version` (Windows).
- **Git.**
- **Visual Studio Code** con las extensiones de Python y Jupyter (VS Code las sugiere al abrir el proyecto).
- **Cuenta gratuita en la BDE del Banco Central:** <https://si3.bcentral.cl/estadisticas/Principal1/Web_Services/index.htm>
- **API key gratuita de FRED:** <https://fred.stlouisfed.org/docs/api/api_key.html>

### 1. Clonar el repositorio

```bash
git clone https://github.com/danielcornejo2/Proyecto_Economia.git
cd Proyecto_Economia
```

### 2. Crear el entorno e instalar las dependencias

| Sistema | Comando |
|---|---|
| Mac / Linux | `python3 configurar_entorno.py` |
| Windows | `python configurar_entorno.py` |

El script crea el entorno virtual `.venv`, instala `requirements.txt` y crea `.env` a partir de `.env.example`. Se puede ejecutar varias veces: reutiliza el entorno y no borra credenciales ya escritas.

Alternativa manual:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
```

### 3. Activar el entorno

| Sistema | Comando |
|---|---|
| Mac / Linux | `source .venv/bin/activate` |
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |

La terminal debe mostrar `(.venv)` al inicio de la línea. Para salir: `deactivate`.

### 4. Escribir las credenciales

Abrir `.env` y reemplazar los valores de ejemplo con **credenciales propias**, sin comillas ni espacios:

```
BCCH_USER=tu_correo@ejemplo.com
BCCH_PASS=tu_clave
FRED_API_KEY=tu_api_key_de_32_caracteres
```

`.env` es personal, está en el `.gitignore` y **nunca se sube** al repositorio.

### 5. Descargar los datos y crear la base (un solo comando)

```bash
python carga.py --hasta 2026-09-30
```

(`python carga.py` sin argumentos usa la misma fecha de corte.)

El comando descarga las 13 series, descarta los datos posteriores al corte, guarda un CSV por serie en `data/raw/bcch/` y `data/raw/fred/` y construye `data/base.db`. **Se considera correcto si la etapa de descarga muestra una línea `[OK]` por cada una de las 13 series, no aparece ningún `[ERROR]`** y el proceso termina con:

```
[OK] Carga completa: 13 series con fecha de corte 2026-09-30 en data/base.db
```

Para actualizar con otra fecha de corte: `python carga.py --hasta 2026-12-31`.

Alternativa por etapas (descarga hasta el último dato disponible, **sin** fecha de corte):

```bash
python extraccion/E_BCCH.py
python extraccion/E_FRED.py
python bd/crear_base.py
```

Para buscar el código de otra serie:

```bash
python extraccion/E_BCCH.py --buscar "IPC"                       # series mensuales del BCCh
python extraccion/E_BCCH.py --buscar "BCU" --frecuencia DAILY    # series diarias del BCCh
python extraccion/E_FRED.py --buscar "copper"                    # FRED (en inglés)
```

### 6. Ejecutar las consultas y el análisis

- Consultas SQL sin notebook: ver el comando de la sección [Consultas SQL](#consultas-sql).
- Análisis: abrir `notebooks/02_analisis_coyuntura.ipynb` en VS Code, elegir el kernel `.venv` y ejecutar todas las celdas (*Run All*). El notebook lee `../data/base.db` y `../sql/consultas.sql`, por lo que debe ejecutarse desde la carpeta `notebooks/` (VS Code lo hace por defecto).

### Problemas frecuentes

| Mensaje | Causa y solución |
|---|---|
| `faltan BCCH_USER o BCCH_PASS en el archivo .env` | Falta el `.env` o está incompleto: repetir el paso 4. |
| `FRED_API_KEY ... no tiene el formato` | La key debe tener 32 caracteres (minúsculas y números), sin comillas ni espacios. |
| `No hay conexión a internet con la API` | Revisar la red o desactivar la VPN. |
| `[ERROR] Fallaron estas series` | La base no se creó. Volver a ejecutar `carga.py`; si persiste, revisar el código de esa serie con `--buscar`. |

---

## Estructura del repositorio

```
Proyecto_Economia/
├── carga.py                  # pipeline completo: descarga ambas fuentes con fecha de corte y crea la base
├── configurar_entorno.py     # crea .venv, instala dependencias y prepara .env
├── extraccion/
│   ├── E_BCCH.py             # extracción del Banco Central de Chile -> data/raw/bcch/
│   └── E_FRED.py             # extracción de FRED -> data/raw/fred/
├── bd/
│   └── crear_base.py         # esquema SQL, validación de los CSV y carga en data/base.db
├── sql/
│   └── consultas.sql         # consultas comentadas: JOIN, GROUP BY y función de ventana
├── notebooks/
│   ├── 02_analisis_coyuntura.ipynb   # análisis de coyuntura inicial
├── data/                     # se genera al ejecutar carga.py; NO se sube a GitHub
│   ├── raw/bcch/, raw/fred/  #   un CSV por serie
│   └── base.db               #   base de datos SQLite
├── .env.example              # plantilla de credenciales (el .env real no se sube)
├── .gitignore                # excluye .env, data/, *.db, .venv/ y archivos de sistema
├── .vscode/                  # activa .venv en la terminal y recomienda extensiones
├── requirements.txt          # dependencias de Python
└── README.md
```

**No se suben al repositorio:** `.env`, `data/`, la base `*.db` ni `.venv/`. El `.gitignore` los excluye; cada integrante los genera en su computador.

---

## Trabajo en equipo con Git

### Configuración inicial (una vez por computador)

```bash
git config --global user.name "Tu Nombre"
git config --global user.email "tu_correo_de_github@ejemplo.com"
gh auth login        # autenticación por navegador (requiere GitHub CLI)
```

### Flujo de trabajo

1. Traer los últimos cambios: `git checkout main` y `git pull`.
2. Crear una rama por tarea: `git checkout -b nombre-de-la-tarea`.
3. Hacer commits que digan qué cambió, por ejemplo `git commit -m "Agrega series de mercado laboral al catálogo"`. Evitar mensajes como "cambios", "prueba" o "final".
4. Subir la rama (`git push -u origin nombre-de-la-tarea`) y abrir un *pull request* para que otro integrante lo revise antes de integrarlo a `main`.

### Entrega del Hito 2

Antes de crear el tag, un integrante que no escribió la extracción realiza el autochequeo: clonar en una carpeta nueva, seguir los pasos 2 a 6 y verificar que la carga termina con `[OK] Carga completa: 13 series`, sin ningún `[ERROR]`, y que las consultas entregan resultados. Luego, sobre la última versión de `main`:

```bash
git checkout main
git pull
git tag hito-2
git push origin hito-2
```

Para comprobar que el tag está en GitHub: `git ls-remote --tags origin`.

---

## Hitos del proyecto

| Hito | Fecha | Entregable | Estado |
|---|---|---|---|
| Hito 1: Propuesta | Semana 4 | Variable objetivo, pregunta de proyección, series tentativas, mecanismos y repositorio | Entregado |
| Hito 2: Avance de datos | Semana 8 | Extracción por API, base relacional poblada, consultas SQL y análisis de coyuntura inicial (tag `hito-2`) | Entregado |
| Hito 3: Entrega final | Semana 13 | Informe final, repositorio reproducible y monitor Power BI (`.pbix`) | Pendiente |
| Defensa | Semanas 14–15 | Presentación de 15 minutos apoyada en el monitor y preguntas | Pendiente |

---

## Metodología prevista para la proyección

Lo que sigue corresponde al Hito 3 y todavía no está implementado.

### Regla de Taylor

Se estimará una regla de Taylor basada en el IPC, en la versión para economías pequeñas y abiertas de Galí y Monacelli (2005), aplicada a Chile por Caputo y Herrera (2013):

```
i_t = r̄ + φ_π · E_t(π_t+1) + φ_y · x_t
```

- `i_t`: TPM.
- `r̄`: tasa natural de interés real.
- `E_t(π_t+1)`: inflación esperada (EEE).
- `x_t`: brecha de actividad (filtro HP sobre el Imacec).
- `φ_π`, `φ_y`: respuestas de la TPM a la inflación esperada y a la brecha.

Como referencia, Caputo y Herrera (2013) estiman para economías emergentes con metas de inflación una respuesta de largo plazo a la inflación esperada de 1,174, a la brecha de 0,656 y al Fed Funds Rate de 1,2, con un componente inercial importante. Apablaza y Ortiz (2024) confirman, con datos chilenos, que la inercia es el componente que más incide en la TPM.

### Próximos pasos

- **Relaciones:** correlaciones y rezagos entre la TPM y sus predictores, con discusión de los mecanismos.
- **Modelos:** la regla de Taylor estimada (con inercia y Fed Funds Rate) y un ARIMA/SARIMA para la TPM.
- **Evaluación fuera de muestra:** período de evaluación separado, comparación contra una caminata aleatoria y sin sesgo de anticipación, considerando los rezagos de publicación de cada serie.
- **Proyección:** trayectoria de la TPM a 6–24 meses con riesgos al alza y a la baja.
- **Monitor Power BI:** conectado a `data/base.db`, con niveles, variaciones en 12 meses, proyección frente a la trayectoria efectiva y un panel tipo "semáforo".

---

## Referencias

- Apablaza, V., & Ortiz, J. (2024). *Determinantes de la tasa de política monetaria en Chile*. Documento de Trabajo N°30. Observatorio del Contexto Económico, Universidad Diego Portales. https://ocec.udp.cl/cms/wp-content/uploads/2024/03/DT30.pdf
- Banco Central de Chile. (2020). *La política monetaria del Banco Central de Chile en el marco de metas de inflación*. https://www.bcentral.cl/documents/33528/133301/PoliticaMonetariaBcchMarcoMetasInflacion2020.pdf
- Banco Central de Chile. (2026). *Informe de Política Monetaria, septiembre 2026*.
- Caputo, R., & Herrera, L. O. (2013). *Efficient CPI-based Taylor rules in small open economies*. Documento de Trabajo N°694. Banco Central de Chile.
- Galí, J., & Monacelli, T. (2005). Monetary policy and exchange rate volatility in a small open economy. *The Review of Economic Studies*, 72(3), 707–734.
- Hodrick, R. J., & Prescott, E. C. (1997). Postwar U.S. business cycles: An empirical investigation. *Journal of Money, Credit and Banking*, 29(1), 1–16.