# La TPM en Chile: monitor de coyuntura y proyección con una regla de política monetaria
 
**Proyecto del curso Ciencia de Datos para la Economía (ICO09425) — Facultad de Administración y Economía, Universidad Diego Portales.**
 
**Profesor:** Luis Cuevas
 
**Integrantes:** Daniel Cornejo, Catarí Garrido, Laura Ruiz, Francisca Silva
 
> Este trabajo es un ejercicio académico; las proyecciones no representan pronósticos oficiales ni recomendaciones de política o de inversión.
 
---
 
## Contenido
 
1. [Contexto y motivación](#contexto-y-motivación)
2. [Objetivo y pregunta de investigación](#objetivo-y-pregunta-de-investigación)
3. [Metodología](#metodología)
4. [Datos](#datos)
5. [Estructura del repositorio](#estructura-del-repositorio)
6. [Cómo reproducir el proyecto](#cómo-reproducir-el-proyecto)
7. [Guía de trabajo con Git para el equipo](#guía-de-trabajo-con-git-para-el-equipo)
8. [Hitos del proyecto](#hitos-del-proyecto)
9. [Referencias](#referencias)

---

## Contexto y motivación
 
La Tasa de Política Monetaria (TPM) es uno de los principales instrumentos que utiliza el Banco Central de Chile (BCCh) para conducir la política monetaria y cumplir su objetivo de estabilidad de precios. A través de sus modificaciones, el Banco Central influye sobre las tasas de interés del sistema financiero y, en consecuencia, sobre las decisiones de consumo, ahorro e inversión de los agentes económicos, afectando la actividad económica y la inflación (Banco Central de Chile, s.f.).
 
En los últimos años la economía chilena ha enfrentado fluctuaciones importantes en inflación y actividad, lo que ha exigido ajustes significativos de la TPM. Este proyecto hace un seguimiento de la coyuntura macroeconómica chilena y proyecta la trayectoria de la TPM, combinando el monitoreo de sus principales determinantes con una regla de política monetaria estimada con datos chilenos.
 
## Objetivo y pregunta de investigación
 
**Variable objetivo:** TPM (Tasa de Política Monetaria), promedio mensual.
 
**Pregunta que guía el trabajo:**
 
> ¿Cuál es la trayectoria esperada de la TPM en Chile durante los próximos 6 a 24 meses, según la evolución de sus principales determinantes macroeconómicos y una regla de política monetaria estimada con datos chilenos?
 
Para responderla, el proyecto:
 
1. Construye un monitor de coyuntura con las principales series macroeconómicas chilenas y externas.
2. Estima una regla de Taylor para Chile y contrasta la TPM que predice la regla con la TPM efectivamente observada.
3. Identifica los períodos en que la política monetaria se apartó de lo que la regla sugería y discute posibles razones económicas de esas desviaciones.
4. Proyecta la trayectoria esperada de la TPM a 6-24 meses.

## Metodología
 
### Regla de Taylor
 
Se estima una regla de Taylor basada en inflación del IPC, en la versión para economías pequeñas y abiertas de Galí y Monacelli (2005), aplicada a Chile por Caputo y Herrera (2013):
 
```
i_t = r̄ + φ_π^CPI · E_t(π_t+1) + φ_y^CPI · x_t
```
 
Donde:
 
- `i_t`: TPM (variable a explicar).
- `r̄`: tasa natural de interés real.
- `E_t(π_t+1)`: inflación esperada del IPC.
- `φ_π^CPI`, `φ_y^CPI`: coeficientes de respuesta de la TPM a la inflación esperada y a la brecha de actividad, respectivamente.
- `x_t`: brecha de actividad, construida aplicando el filtro de Hodrick y Prescott (1997) al Imacec, siguiendo la metodología de brecha de producto de Caputo y Herrera (2013).
Como referencia empírica, Caputo y Herrera (2013) estiman para un panel de economías emergentes con metas de inflación (donde Chile se encuadra) una respuesta de largo plazo a la inflación esperada levemente superior a 1 (1,174) —consistente con el principio de Taylor—, una respuesta positiva y menor a la brecha de producto (0,656), una respuesta significativa al Fed Funds Rate (1,2 en el largo plazo) y un componente inercial alto en la tasa (≈21,7 %). En la misma línea, Apablaza y Ortiz (2024), con datos chilenos hasta enero de 2024, confirman que la inercia es el componente que más incide en la evolución de la TPM y que cada punto porcentual de desviación en las expectativas de inflación a 11 meses genera un ajuste de 27 puntos base en la tasa.
 
### Canales de transmisión
 
Más allá de la regla como ecuación, el análisis busca entender los canales por los que los movimientos de la TPM se transmiten al resto de la economía (Banco Central de Chile, 2020):
 
- **Canal de tasas de interés de mercado:** la TPM se traspasa a las tasas de corto plazo (depósitos) y a las de largo plazo (bonos en pesos y en UF), afectando el crédito.
- **Canal cambiario:** cambios en la tasa doméstica alteran las expectativas de tipo de cambio; cuando el peso se deprecia, suben los precios relativos de los bienes transables.
- **Canal de demanda:** modifica las decisiones de consumo e inversión y, con ello, el Imacec y el mercado laboral.
- **Canal de valorización de activos:** se transmite a través de los precios de bonos, acciones y viviendas.
- **Canal de expectativas:** descrito por el BCCh como "fundamental"; los anuncios de política monetaria anclan (o no) las expectativas de inflación (EEE), afectando la fijación de precios y salarios.
## Datos
 
Se utilizan **14 series económicas**, todas descargadas de forma programática vía API (no hay descargas manuales). La fuente principal es la Base de Datos Estadísticos (BDE) del Banco Central de Chile, a través del servicio SieteRestWS. Para los indicadores externos se usa la API de FRED (Federal Reserve Economic Data, Reserva Federal de St. Louis).
 
La selección cubre la variable objetivo (TPM), sus determinantes según la regla de Taylor (inflación, inflación subyacente, expectativas y brecha de actividad vía Imacec) y los indicadores de contexto del monitor (tipo de cambio, tasas de mercado, empleo y entorno externo).
 
| # | Nombre en el proyecto | Serie | Código | Fuente | Frecuencia original | Tema |
|---|---|---|---|---|---|---|
| 1 | `tpm` | Tasa de política monetaria | `F022.TPM.TIN.D001.NO.Z.M` | BCCh | Mensual | Política monetaria |
| 2 | `ipc` | IPC general, variación mensual | `F074.IPC.VAR.Z.Z.C.M` | BCCh | Mensual | Precios |
| 3 | `ipc_sae` | IPC sin alimentos ni energía, variación mensual empalmada (INE, base 2023) | `F074.IPCSAE.VAR.Z.EP23.Z.M` | BCCh | Mensual | Precios |
| 4 | `expectativa_ipc_eee` | Expectativa de inflación a 12 meses (EEE), mediana | `F089.IPC.V12.14.M` | BCCh | Mensual | Expectativas |
| 5 | `imacec` | Imacec, índice original (referencia 2018) | `F032.IMC.IND.Z.Z.EP18.Z.Z.0.M` | BCCh | Mensual | Actividad |
| 6 | `desempleo` | Tasa de desocupación nacional (INE) | `F049.DES.TAS.INE9.10.M` | BCCh | Mensual | Mercado laboral |
| 7 | `dolar_observado` | Dólar observado, promedio mensual | `F073.TCO.PRE.HIST.M` | BCCh | Mensual | Tipo de cambio |
| 8 | `tasa_bcp_10` | Tasa de mercado secundario, bonos en pesos a 10 años | `F022.BCLP.TIS.AN10.NO.Z.D` | BCCh | Diaria | Tasas de mercado |
| 9 | `tasa_bcu_10` | Tasa de mercado secundario, bonos en UF a 10 años | `F022.BUF.TIS.AN10.UF.Z.D` | BCCh | Diaria | Tasas de mercado |
| 10 | `tasa_depositos_90d` | Tasa de interés de depósitos a 90 días | `F022.TDB.TIS.D090.NO.Z.D` | BCCh | Diaria | Tasas de mercado |
| 11 | `precio_cobre` | Precio internacional del cobre (FMI) | `PCOPPUSDM` | FRED | Mensual | Externo |
| 12 | `fed_funds` | Tasa de fondos federales de EE.UU. | `FEDFUNDS` | FRED | Mensual | Externo |
| 13 | `ipc_eeuu` | IPC de EE.UU. (CPI-U), desestacionalizado | `CPIAUCSL` | FRED | Mensual | Externo |
| 14 | `produccion_industrial_eeuu` | Producción industrial de EE.UU. | `INDPRO` | FRED | Mensual | Externo |


### Funcionamiento del script de extracción del Banco Central (`E_BCCH.py`)

El archivo `extraccion/E_BCCH.py` permite descargar automáticamente 10 indicadores económicos desde la Base de Datos Estadísticos (BDE) del Banco Central de Chile, utilizando su API SieteRestWS.

**Objetivo del script**

Obtener información económica real y actualizable para analizar la trayectoria de la Tasa de Política Monetaria (TPM), sus determinantes macroeconómicos y los principales canales de transmisión de la política monetaria.

**Configuración inicial**

El script define los siguientes elementos:

- `URL_API`: dirección del servicio web del Banco Central.
- `FECHA_INICIO`: fecha inicial de consulta, establecida en `2000-01-01`.
- `SERIES`: diccionario que contiene los nombres y códigos de los 10 indicadores seleccionados.
- `CARPETA_SALIDA`: directorio `data/raw/bcch/`, donde se almacenan los CSV.

**Funciones principales**

| Función | Descripción |
|---|---|
| `cargar_credenciales()` | Obtiene `BCCH_USER` y `BCCH_PASS` desde `.env` y comprueba que estén configuradas. |
| `ocultar_credenciales()` | Oculta el usuario y la contraseña en los mensajes de error. |
| `llamar_api()` | Consulta la API mediante `requests`, comprueba la respuesta y realiza hasta tres intentos ante errores. |
| `descargar_serie()` | Descarga las observaciones de una serie y las convierte en un DataFrame de pandas con fecha y valor. |
| `a_mensual()` | Convierte las observaciones a frecuencia mensual mediante el promedio de los valores disponibles en cada mes. |
| `leer_fecha_corte()` | Interpreta y valida la fecha proporcionada mediante `--hasta`. |
| `buscar_series()` | Busca indicadores en el catálogo del Banco Central mediante una palabra clave. |
| `main()` | Coordina la descarga, el procesamiento, la generación de CSV y el reporte de errores. |

**Procesamiento de los datos**

1. Se cargan las credenciales desde el archivo `.env`.
2. Se consulta la API para cada una de las 10 series económicas.
3. Se convierten las fechas al formato utilizado por pandas y los valores a formato numérico.
4. Las observaciones que la API identifica con un estado distinto de `OK` se consideran faltantes.
5. Si se indicó una fecha de corte, se eliminan las observaciones posteriores.
6. Se calcula el promedio mensual mediante `resample("MS").mean()`. Las fechas mensuales corresponden al primer día de cada mes.
7. Se agregan las columnas `serie` y `codigo`.
8. Se genera un archivo CSV independiente para cada indicador en `data/raw/bcch/`.

Cada CSV contiene las columnas `fecha`, `valor`, `serie` y `codigo`.

**Tratamiento de errores**

El script incorpora mecanismos para mejorar la seguridad y confiabilidad de la extracción:

- Comprueba que existan las credenciales necesarias.
- Realiza hasta tres intentos de consulta ante errores de la API o de conexión.
- Oculta las credenciales en los mensajes de error.
- Identifica los valores faltantes sin reemplazarlos artificialmente.
- Informa el número de meses descargados y la cantidad de datos faltantes por serie.
- Identifica las series que presentaron errores y finaliza con un código de error si alguna descarga falló.

**Ejecución**

Para descargar los indicadores hasta la fecha de corte del Hito 2:

```bash
python extraccion/E_BCCH.py --hasta 2026-09-30
```

Para buscar series en el catálogo del Banco Central:

```bash
python extraccion/E_BCCH.py --buscar "IPC"
```

El resultado de la extracción se utiliza posteriormente para construir la base de datos SQLite mediante `bd/crear_base.py`.


### Funcionamiento del script de extracción de FRED (`E_FRED.py`)

El archivo `extraccion/E_FRED.py` permite descargar automáticamente cuatro indicadores económicos internacionales desde Federal Reserve Economic Data (FRED), utilizando la API oficial de la Reserva Federal de St. Louis.

**Objetivo del script**

Incorporar variables internacionales relevantes para el análisis de la Tasa de Política Monetaria (TPM) de Chile, considerando factores externos como las condiciones monetarias de Estados Unidos, la actividad económica internacional y el precio del cobre.

**Indicadores seleccionados**

| Variable | Código FRED | Relevancia económica |
|---|---|---|
| Precio del cobre | `PCOPPUSDM` | Permite incorporar un indicador externo relevante para la economía chilena por su importancia en las exportaciones. |
| Tasa de fondos federales | `FEDFUNDS` | Representa las condiciones de política monetaria de Estados Unidos. |
| IPC de Estados Unidos | `CPIAUCSL` | Permite analizar la evolución del nivel de precios estadounidense. |
| Producción industrial de Estados Unidos | `INDPRO` | Aproxima la evolución de la actividad industrial estadounidense. |

**Configuración inicial**

El script define los siguientes elementos:

- `URL_API`: dirección de la API oficial de FRED.
- `FECHA_INICIO`: fecha inicial de consulta, establecida en `2000-01-01`.
- `SERIES`: diccionario con los nombres y códigos de los cuatro indicadores.
- `CARPETA_SALIDA`: directorio `data/raw/fred/`, donde se almacenan los CSV.

**Funciones principales**

| Función | Descripción |
|---|---|
| `cargar_api_key()` | Lee `FRED_API_KEY` desde `.env` y valida su formato. |
| `ocultar_credenciales()` | Evita mostrar la clave de acceso en los mensajes de error. |
| `mensaje_de_error()` | Obtiene la descripción del error entregada por la API. |
| `llamar_api()` | Realiza solicitudes a FRED, comprueba las respuestas y aplica reintentos cuando corresponde. |
| `descargar_serie()` | Descarga las observaciones de un indicador y las convierte en un DataFrame de pandas. |
| `a_mensual()` | Transforma las observaciones a frecuencia mensual mediante el promedio de los valores disponibles. |
| `leer_fecha_corte()` | Valida la fecha indicada mediante el argumento `--hasta`. |
| `buscar_series()` | Permite buscar indicadores en el catálogo de FRED. |
| `main()` | Coordina la extracción, transformación, almacenamiento y reporte de errores. |

**Procesamiento de los datos**

1. Se carga la clave `FRED_API_KEY` desde el archivo `.env`.
2. Se consulta la API de FRED para descargar cada indicador.
3. Las observaciones recibidas se organizan en un DataFrame de pandas.
4. Se convierten las fechas y los valores a formatos adecuados para su procesamiento.
5. Los valores faltantes, identificados por FRED mediante un punto (`.`), se convierten en valores nulos.
6. Se descartan las observaciones posteriores a la fecha de corte, cuando esta se especifica.
7. Se utiliza `resample("MS").mean()` para obtener una observación mensual por serie.
8. Se incorporan las columnas `serie` y `codigo`.
9. Se guarda un archivo CSV por indicador en `data/raw/fred/`.

Cada CSV contiene las columnas `fecha`, `valor`, `serie` y `codigo`.

**Tratamiento de errores**

El programa incorpora los siguientes controles:

- Verifica que exista una clave de acceso a FRED y que tenga el formato esperado.
- Oculta la clave de acceso en los mensajes de error.
- Identifica errores de conexión y respuestas incorrectas de la API.
- Realiza hasta tres intentos ante errores que pueden ser temporales.
- Aplica una espera mayor cuando FRED responde con el código HTTP 429, asociado a un exceso de solicitudes.
- Distingue errores definitivos, como una clave inválida o una serie inexistente.
- Conserva los valores faltantes sin reemplazarlos artificialmente.
- Informa la cantidad de meses descargados y los datos faltantes de cada serie.
- Identifica las series que fallaron y finaliza con un código de error si corresponde.

**Ejecución**

Para descargar los indicadores hasta la fecha de corte del Hito 2:

```bash
python extraccion/E_FRED.py --hasta 2026-09-30
```

Para buscar indicadores en el catálogo de FRED:

```bash
python extraccion/E_FRED.py --buscar "copper"
```

Los archivos descargados se utilizan posteriormente, junto con los indicadores del Banco Central, para construir la base de datos SQLite mediante `bd/crear_base.py`.


### Funcionamiento del script de construcción de la base de datos (`crear_base.py`)

El archivo `bd/crear_base.py` construye una base de datos relacional SQLite a partir de los archivos CSV generados por los scripts de extracción del Banco Central de Chile y FRED.

**Objetivo del script**

Centralizar y organizar los 14 indicadores económicos del proyecto en una base de datos estructurada, con información sobre sus fuentes, características, clasificación temática y observaciones mensuales.

**Configuración inicial**

El script utiliza los siguientes elementos:

- `CARPETA_DATOS`: directorio `data/raw/`, que contiene los CSV de ambas fuentes.
- `RUTA_BASE`: ubicación del archivo SQLite de salida, `data/base.db`.
- `FUENTES`: identifica las carpetas `bcch/` y `fred/`.
- `COLUMNAS_CSV`: establece las columnas obligatorias `fecha`, `valor`, `serie` y `codigo`.
- `TEMAS`: define ocho categorías económicas.
- `CATALOGO`: registra los metadatos de las 14 series seleccionadas.
- `MetaSerie`: estructura que almacena la fuente, frecuencia original, tema, tipo, unidad y descripción de cada indicador.

**Estructura de la base de datos**

La base contiene tres tablas relacionadas:

| Tabla | Contenido | Clave primaria |
|---|---|---|
| `temas` | Categorías económicas y sus descripciones. | `id_tema` |
| `series` | Identificación, fuente, código y características de cada indicador. | `id_serie` |
| `observaciones` | Valores mensuales de cada serie económica. | `(id_serie, fecha)` |

Las relaciones entre las tablas se establecen mediante claves foráneas:

- `series.id_tema` se relaciona con `temas.id_tema`.
- `observaciones.id_serie` se relaciona con `series.id_serie`.

La clave primaria compuesta de `observaciones` impide almacenar dos observaciones de una misma serie para el mismo mes.

El programa también crea índices para facilitar consultas y una vista llamada `v_observaciones`, que reúne la información de las tres tablas.

**Funciones principales**

| Función | Descripción |
|---|---|
| `validar_catalogo()` | Comprueba que los temas asignados a las series estén definidos. |
| `listar_csv()` | Localiza los CSV en las carpetas de las fuentes conocidas. |
| `leer_csv()` | Lee los archivos y valida sus columnas, fechas, códigos y valores. |
| `insertar_temas()` | Registra las categorías económicas en la tabla `temas`. |
| `insertar_serie()` | Registra los metadatos de cada indicador en la tabla `series`. |
| `insertar_observaciones()` | Inserta las observaciones mensuales en la tabla `observaciones`. |
| `verificar_integridad()` | Ejecuta comprobaciones de integridad de SQLite y de claves foráneas. |
| `construir_base()` | Coordina la creación de las tablas y la carga de los datos. |
| `mostrar_resumen()` | Presenta las series cargadas, sus observaciones válidas y sus rangos de fechas. |
| `main()` | Ejecuta el proceso y comunica los resultados o errores. |

**Proceso de construcción**

1. Se comprueba que el catálogo de indicadores esté correctamente definido.
2. Se buscan los archivos CSV en `data/raw/bcch/` y `data/raw/fred/`.
3. Se crea una base de datos temporal con las tablas, índices y vista correspondientes.
4. Se insertan las ocho categorías económicas en la tabla `temas`.
5. Se valida cada CSV antes de incorporarlo a la base.
6. Se registran las características de cada indicador en `series`.
7. Se insertan los valores mensuales en `observaciones`.
8. Los valores faltantes de pandas (`NaN`) se almacenan como `NULL` en SQLite.
9. Se verifica la integridad de la base y sus relaciones.
10. Si no ocurren errores graves, la base temporal reemplaza al archivo de base de datos anterior.
11. Se muestra un resumen de las series cargadas y los problemas detectados.

**Validaciones y controles**

El script verifica que:

- Los archivos CSV contengan las cuatro columnas obligatorias.
- Los archivos no estén vacíos.
- El nombre de cada serie coincida con el nombre de su archivo.
- Cada CSV corresponda a un único código de indicador.
- Las fechas tengan el formato esperado y no estén duplicadas.
- Los valores no faltantes sean numéricos.
- Los indicadores pertenezcan a las fuentes y temas definidos.
- No existan relaciones inválidas entre las tablas.
- No se repita una combinación de serie y fecha.

La base admite valores `NULL` cuando no existen observaciones disponibles, evitando reemplazar artificialmente los datos faltantes.

**Seguridad de la construcción**

El programa utiliza una base temporal y una transacción para proteger la consistencia de los datos. Si ocurre un error grave durante la construcción, elimina el archivo temporal y conserva la base anterior.

Cuando encuentra archivos faltantes o inválidos, registra esos problemas y puede finalizar con un código de error, aunque haya logrado cargar las demás series. Por esta razón, se debe comprobar que el mensaje final indique que todas las series del catálogo quedaron cargadas.

**Ejecución**

Para construir la base de datos desde la carpeta raíz del proyecto:

```bash
python bd/crear_base.py
```

El archivo generado se almacena en:

`data/base.db`

El programa también permite indicar otras rutas mediante los argumentos `--datos` y `--salida`.

**Resultado esperado**

Una base de datos SQLite que contenga los ocho temas económicos, las 14 series seleccionadas y sus observaciones mensuales, lista para realizar consultas SQL y análisis posteriores.


### Funcionamiento del script de carga automática (`carga.py`)

El archivo `carga.py` coordina la extracción de indicadores económicos desde el Banco Central de Chile y FRED, su transformación a frecuencia mensual y la construcción de la base de datos SQLite.

**Objetivo del script**

Automatizar el proceso completo de obtención y almacenamiento de datos económicos, permitiendo reproducir la base del proyecto mediante una sola ejecución.

**Configuración inicial**

El script utiliza:

- `FECHA_CORTE`: fecha de corte predeterminada, `2026-09-30`.
- `E_BCCH`: módulo de extracción del Banco Central de Chile.
- `E_FRED`: módulo de extracción de FRED.
- `crear_base`: módulo encargado de construir la base de datos SQLite.
- `pandas`: biblioteca utilizada para interpretar las fechas y procesar las observaciones.

**Funciones principales**

| Función | Descripción |
|---|---|
| `descargar_fuente()` | Descarga las series de una fuente, aplica la fecha de corte, convierte los datos a frecuencia mensual y guarda los CSV. |
| `main()` | Coordina la extracción desde ambas fuentes, verifica errores y ejecuta la construcción de la base de datos. |

**Etapas del proceso**

1. Se establece la fecha de corte, que por defecto corresponde al 30 de septiembre de 2026.
2. Se cargan las credenciales del Banco Central desde `.env`.
3. Se descargan los 10 indicadores del Banco Central.
4. Se carga la clave de acceso a FRED desde `.env`.
5. Se descargan los cuatro indicadores internacionales.
6. Se eliminan las observaciones posteriores a la fecha de corte.
7. Se convierten las observaciones a frecuencia mensual mediante promedios.
8. Se guarda un archivo CSV por indicador en la carpeta de su fuente.
9. Si alguna descarga falla, se informa el error y no se ejecuta la construcción de la base.
10. Si las descargas finalizan correctamente, se ejecuta `crear_base.construir_base()` para generar `data/base.db`.
11. Se presenta un resumen de las series y observaciones almacenadas.
12. Si no se detectan problemas, se muestra un mensaje de carga completa.

**Tratamiento de errores**

El script identifica fallas durante la descarga y muestra mensajes `[ERROR]` con el nombre del indicador afectado.

Si una o más series no pueden descargarse, se detiene el proceso antes de construir la base de datos, evitando utilizar involuntariamente los CSV anteriores para completar una nueva carga.

Los CSV que ya existían o que fueron generados antes del error pueden permanecer en `data/raw/`. Por ello, ante una falla, se recomienda revisar los mensajes y volver a ejecutar el proceso completo.

El script también utiliza las validaciones de integridad implementadas en `crear_base.py`.

**Ejecución**

Desde la carpeta raíz del repositorio:

```bash
python carga.py
```

Este comando descarga las series y construye la base utilizando la fecha de corte predeterminada `2026-09-30`.

También es posible especificar otra fecha:

```bash
python carga.py --hasta 2026-09-30
```

**Archivos generados**

- `data/raw/bcch/`: archivos CSV del Banco Central.
- `data/raw/fred/`: archivos CSV de FRED.
- `data/base.db`: base de datos SQLite con los indicadores y sus observaciones mensuales.

**Resultado esperado**

Una base de datos SQLite con los 14 indicadores económicos del proyecto, organizados por tema y fuente, junto con sus observaciones mensuales hasta la fecha de corte establecida.


 
### Tratamiento de errores, datos faltantes y frecuencias
 
- **Fecha de corte:** `2026-09-30`. Todas las series se cortan en esa fecha para que el análisis sea reproducible.
- **Frecuencia:** todo se guarda en frecuencia mensual. Las series diarias se convierten a promedio del mes.
- **Datos faltantes:** los meses sin dato en la API se guardan como valores vacíos (`NULL`); no se rellenan ni se eliminan.
- **Rezago de publicación:** algunas series terminan antes de la fecha de corte porque se publican con rezago (por ejemplo, el Imacec y el precio del cobre).
- **Historia disponible:** la desocupación parte en 2010-03 y el IPC SAE empalmado en 2010-01; ambas tienen más de 10 años de historia mensual.
- **Errores de conexión:** cada descarga se reintenta hasta 3 veces. Si una serie falla, el script la informa como `ERROR` y continúa con las demás; al final lista las que fallaron.

### Base de datos
 
Los CSV descargados se cargan en una base SQLite (`data/base.db`) con tres tablas relacionadas:
 
| Tabla | Contenido | Llaves |
|---|---|---|
| `temas` | Clasificación temática de los indicadores | PK `id_tema` |
| `series` | Catálogo: nombre, código, fuente, frecuencia, tipo, unidad y tema | PK `id_serie`; FK `id_tema` → `temas` |
| `observaciones` | Una fila por serie y mes (`fecha` en formato `AAAA-MM-DD`, `valor`) | PK (`id_serie`, `fecha`); FK `id_serie` → `series` |
 
Además, la vista `v_observaciones` une las tres tablas (tema, serie, fecha y valor).


### Población de la base de datos

La base de datos SQLite se construye mediante el script `bd/crear_base.py`, utilizando los archivos CSV descargados desde las API del Banco Central de Chile (BCCh) y FRED.

El proceso de población se realiza en las siguientes etapas:

1. **Lectura de los archivos:** el programa identifica los CSV almacenados en `data/raw/bcch/` y `data/raw/fred/`.

2. **Validación de los datos:** comprueba que los archivos contengan las columnas `fecha`, `valor`, `serie` y `codigo`. Además, verifica que las fechas sean válidas, no estén duplicadas y que los valores sean numéricos.

3. **Población de la tabla `temas`:** incorpora las 8 categorías económicas definidas en el proyecto, como política monetaria, precios, actividad económica y sector externo.

4. **Población de la tabla `series`:** registra los 14 indicadores económicos con sus respectivos códigos, fuentes, frecuencias originales, tipos, unidades, descripciones y temas asociados.

5. **Población de la tabla `observaciones`:** incorpora los valores mensuales de cada indicador junto con sus fechas. Los datos faltantes se almacenan como `NULL`, sin reemplazarlos por valores estimados.

6. **Verificación de integridad:** comprueba que la base de datos sea válida y que las relaciones entre las tablas respeten las llaves foráneas.

**Ejecución de la carga**

Después de descargar los archivos CSV, la base de datos puede construirse mediante:

```bash
python bd/crear_base.py
```

También se puede automatizar todo el proceso de descarga y creación de la base con:

```bash
python carga.py --hasta 2026-09-30
```

El archivo generado se guarda en `data/base.db` y contiene las tres tablas relacionadas: `temas`, `series` y `observaciones`.


### Consultas SQL

El archivo `sql/consultas.sql` contiene tres consultas SQL que permiten explorar, organizar y analizar los 14 indicadores económicos almacenados en la base de datos SQLite (`data/base.db`). Estas consultas utilizan las tablas `temas`, `series` y `observaciones`, creadas mediante el archivo `bd/crear_base.py`.

Su objetivo es comprobar las relaciones entre las tablas, resumir las observaciones mensuales y calcular transformaciones económicas utilizando funciones de ventana.

#### 1. Consulta JOIN: relación entre tablas

La primera consulta utiliza `JOIN` para relacionar las tablas `observaciones`, `series` y `temas` mediante sus claves primarias y foráneas.

Permite obtener cada observación económica junto con su clasificación temática y las características del indicador al que pertenece.

**Comandos utilizados:**

- `SELECT`: selecciona las columnas que se mostrarán en el resultado.
- `FROM`: indica la tabla principal de la consulta.
- `JOIN`: relaciona las tablas mediante sus identificadores comunes.
- `ON`: establece la condición que deben cumplir las tablas para relacionarse.
- `ORDER BY`: ordena los resultados por tema, nombre de la serie y fecha.

**Resultado:** una tabla que contiene el tema económico, nombre del indicador, tipo de variable, unidad de medida, frecuencia original, fecha y valor.

Esta consulta permite comprobar que cada observación esté correctamente asociada con su serie económica y su clasificación temática.

#### 2. Consulta GROUP BY: agrupación mensual

La segunda consulta utiliza `GROUP BY`, `AVG()` y `COUNT()` para agrupar las observaciones por indicador y mes, calcular el promedio de los valores disponibles y contar las observaciones válidas.

**Comandos utilizados:**

- `GROUP BY`: agrupa las observaciones que pertenecen a una misma serie y mes.
- `strftime('%Y-%m', o.fecha)`: obtiene el año y mes de cada fecha.
- `AVG(o.valor)`: calcula el promedio de los valores no nulos dentro de cada grupo.
- `COUNT(o.valor)`: cuenta las observaciones que tienen un valor válido.
- `ORDER BY`: organiza los resultados por nombre de la serie y mes.

**Importante:** los scripts de extracción `E_BCCH.py` y `E_FRED.py` ya convierten las observaciones a frecuencia mensual antes de almacenarlas en SQLite. Por lo tanto, esta consulta no transforma directamente datos diarios en mensuales, sino que resume y verifica información previamente mensualizada.

Como normalmente existe una observación por serie y mes, `AVG()` devuelve el valor mensual almacenado y `COUNT()` permite identificar si ese valor está disponible.

**Resultado:** una tabla con el nombre del indicador, su frecuencia original, el mes, el valor mensual y el número de observaciones válidas.

#### 3. Consulta con funciones de ventana: variación en 12 meses

La tercera consulta utiliza funciones de ventana para calcular transformaciones de los indicadores económicos durante un período de 12 meses.

El procedimiento considera que las variables tienen diferentes características económicas, por lo que no corresponde aplicar la misma fórmula a todas.

**Transformaciones según el tipo de indicador:**

- **Tasas:** se calcula la diferencia respecto de 12 meses atrás, expresada en puntos porcentuales. Por ejemplo, si una tasa pasa de 5 % a 6 %, el cambio corresponde a 1 punto porcentual.
- **Índices y niveles:** se calcula la variación porcentual respecto del valor de 12 meses atrás. Esto permite analizar, por ejemplo, el crecimiento de un índice de actividad económica.
- **Variaciones mensuales:** se calcula la variación acumulada compuesta de los últimos 12 valores porcentuales. Este procedimiento se utiliza para indicadores como el IPC y el IPC SAE, que ya representan variaciones mensuales.

**Funciones y comandos utilizados:**

- `WITH`: crea una consulta temporal denominada `mensual`, utilizada para organizar los datos antes del cálculo.
- `LAG(valor, 12)`: obtiene el valor ubicado 12 observaciones anteriores dentro de la misma serie.
- `PARTITION BY`: separa los cálculos por indicador económico, evitando mezclar observaciones de distintas series.
- `ORDER BY`: establece el orden cronológico de las observaciones.
- `ROWS BETWEEN 11 PRECEDING AND CURRENT ROW`: define una ventana móvil que considera la observación actual y hasta 11 anteriores.
- `CASE`: selecciona la transformación correspondiente según el tipo de indicador.
- `SUM()` y `LN()`: intervienen en el cálculo de la composición de las variaciones mensuales.
- `EXP()`: permite obtener el resultado de la acumulación compuesta.
- `ROUND()`: redondea los resultados a dos decimales.

**Resultado:** una tabla con el nombre del indicador, su tipo, el mes, el valor observado, la transformación calculada para 12 meses y la unidad correspondiente.

Esta consulta permite analizar la evolución de los indicadores respetando sus unidades de medida y diferencias económicas.

#### 4. Consideraciones metodológicas

Para interpretar correctamente las variaciones de 12 meses, es necesario considerar la continuidad temporal y la disponibilidad de las observaciones.

La función `LAG(valor, 12)` recupera el valor ubicado 12 filas anteriores, lo que corresponde a 12 meses atrás cuando existen observaciones mensuales consecutivas.

Asimismo, la ventana móvil de 12 observaciones permite calcular la composición de las variaciones mensuales. Sin embargo, la consulta no comprueba explícitamente que todos los meses sean consecutivos ni que los 12 valores necesarios estén disponibles.

Por lo tanto, antes de interpretar los resultados, se recomienda verificar la existencia de meses faltantes y valores nulos.

Estas precauciones son importantes para evitar interpretaciones incorrectas de las variaciones económicas.

#### 5. Ejecución de las consultas

Una vez creada la base de datos mediante `carga.py` o `bd/crear_base.py`, se debe abrir el archivo `data/base.db` utilizando una herramienta compatible con SQLite.

Posteriormente, se pueden ejecutar las instrucciones contenidas en `sql/consultas.sql`.

Las tres consultas permiten:

1. Comprobar las relaciones entre las tablas y la clasificación de los indicadores.
2. Resumir y verificar las observaciones mensuales disponibles.
3. Calcular transformaciones de 12 meses mediante funciones de ventana.

En conjunto, constituyen herramientas para revisar la consistencia de la información y preparar los indicadores utilizados en el análisis de coyuntura económica del proyecto.

 
## Estructura del repositorio
 
```
Proyecto_Economia/
├── extraccion/             # descarga de las series desde las APIs
│   ├── E_BCCH.py           # Banco Central de Chile -> data/raw/bcch/
│   └── E_FRED.py           # FRED -> data/raw/fred/
├── bd/
│   └── crear_base.py       # carga los CSV en la base SQLite data/base.db
├── carga.py                # automatiza la descarga de las 14 series y la creación de la base
├── notebooks/              # análisis de coyuntura, regla de Taylor y proyección
├── data/                   # se genera al ejecutar; NO se sube a GitHub
│   ├── raw/bcch/, raw/fred/ # CSV descargados, una subcarpeta por fuente
│   └── base.db             # base de datos relacional
├── configurar_entorno.py   # crea .venv, instala dependencias y prepara .env
├── .env.example            # plantilla de credenciales (el .env real no se sube)
├── requirements.txt        # dependencias de Python
└── README.md
```
 
## Cómo reproducir el proyecto
 
### Requisitos
 
- **Python 3.10 o superior.** Para verificarlo: `python3 --version` (Mac/Linux) o `python --version` (Windows).
- **Git** instalado (ver la [guía de trabajo con Git](#guía-de-trabajo-con-git-para-el-equipo)).
- **Visual Studio Code** con las extensiones de Python y Jupyter. Al abrir el proyecto, VS Code sugiere instalarlas y activa el entorno `.venv` en cada terminal.
- Una **cuenta gratuita en la BDE** del Banco Central: <https://si3.bcentral.cl/estadisticas/Principal1/Web_Services/index.htm>
- Una **API key gratuita de FRED**: <https://fred.stlouisfed.org/docs/api/api_key.html>
### 1. Clonar el repositorio
 
```bash
git clone https://github.com/danielcornejo2/Proyecto_Economia.git
cd Proyecto_Economia
```
 
### 2. Configurar el entorno (un solo comando)
 
| Sistema | Comando |
|---|---|
| Mac / Linux | `python3 configurar_entorno.py` |
| Windows | `python configurar_entorno.py` |
 
El script crea el entorno virtual `.venv`, instala las dependencias de `requirements.txt` y crea el archivo `.env` a partir de `.env.example`. Se puede ejecutar varias veces sin riesgo: reutiliza el entorno y no borra credenciales ya escritas.
 
Alternativa manual, con el entorno ya activado: `pip install -r requirements.txt`.
 
### 3. Activar el entorno
 
| Sistema | Comando |
|---|---|
| Mac / Linux | `source .venv/bin/activate` |
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
 
La terminal debe mostrar `(.venv)` al inicio de la línea. Para salir del entorno al terminar de trabajar, escribe `deactivate`.
 
### 4. Escribir tus credenciales
 
Abre el archivo `.env` (en la raíz) y reemplaza los valores de ejemplo con **tus propias** credenciales, sin comillas ni espacios:
 
```
BCCH_USER=tu_correo@ejemplo.com
BCCH_PASS=tu_clave
FRED_API_KEY=tu_api_key_de_32_caracteres
```
 
El archivo `.env` es personal, está en el `.gitignore` y **nunca se sube al repositorio**. Si ya tenías un `.env` antiguo, vuelve a ejecutar `configurar_entorno.py`: agrega las variables nuevas sin borrar las que ya tenías.


### Ejecución automática del proceso de carga

El proyecto incluye el archivo `carga.py`, que permite ejecutar automáticamente los scripts de extracción del Banco Central de Chile (BCCh) y FRED, y posteriormente construir la base de datos SQLite.

Para ejecutar el proceso completo con la fecha de corte del Hito 2, utiliza:

```bash
python carga.py --hasta 2026-09-30
```

Este comando realiza las siguientes operaciones:

1. Descarga las 10 series económicas del Banco Central de Chile.
2. Descarga las 4 series económicas de FRED.
3. Guarda los archivos CSV en las carpetas correspondientes de `data/raw/`.
4. Ejecuta `bd/crear_base.py` para construir la base SQLite.
5. Verifica el resultado de la carga y comunica si se producen errores.

También se puede ejecutar sin indicar una fecha:

```bash
python carga.py
```

En ese caso, se utiliza la fecha de corte predeterminada (`2026-09-30`).

**Importante:** Antes de ejecutar este comando, se debe haber configurado el entorno virtual y las credenciales del archivo `.env`.

Los pasos 5 y 6 que aparecen a continuación permiten realizar manualmente la extracción y creación de la base de datos, en caso de que se prefiera ejecutar cada etapa por separado.

 
### 5. Descargar los datos con la fecha de corte

 
```bash
python extraccion/E_BCCH.py --hasta 2026-09-30
python extraccion/E_FRED.py --hasta 2026-09-30
```
 
Cada serie debe mostrar una línea `OK`, y ninguna `ERROR`. Los CSV quedan en `data/raw/bcch/` y `data/raw/fred/`. Para actualizar los datos basta con volver a ejecutar los mismos comandos.
 
Para buscar el código de otra serie:
 
```bash
python extraccion/E_BCCH.py --buscar "IPC"                        # series mensuales del BCCh
python extraccion/E_BCCH.py --buscar "BCU" --frecuencia DAILY     # series diarias del BCCh
python extraccion/E_FRED.py --buscar "copper"                     # FRED (en inglés)
```
 
### 6. Crear la base de datos
 
```bash
python bd/crear_base.py
```
 
El script valida cada CSV, construye `data/base.db` desde cero, muestra una tabla de revisión (temas, series, número de observaciones y fechas) y termina con el mensaje `Sin problemas: todas las series del catálogo quedaron cargadas.`
 
## Guía de trabajo con Git para el equipo
 
### Configuración inicial (una sola vez por computador)
 
1. Instalar Git: <https://git-scm.com/downloads>
2. Registrar tu nombre y correo de GitHub en la terminal:
```bash
   git config --global user.name "Tu Nombre"
   git config --global user.email "tu_correo_de_github@ejemplo.com"
```
 
3. Iniciar sesión en GitHub desde la terminal y elegir la opción de autenticación por navegador:
```bash
   gh auth login
```
 
   Requiere GitHub CLI: <https://cli.github.com>
 
4. Clonar el repositorio y entrar a la carpeta (ver el paso 1 de la sección anterior).
### Flujo de trabajo diario
 
1. Traer los últimos cambios del equipo antes de empezar:
```bash
   git checkout main
   git pull
```
 
2. Crear una rama para tu tarea (no trabajar directo en `main`):
```bash
   git checkout -b nombre-de-la-tarea
```
 
3. Hacer los cambios y guardarlos con commits descriptivos. Se puede usar la terminal:
```bash
   git add archivo_modificado.py
   git commit -m "Agrega fecha de corte --hasta a la extracción de FRED"
```
 
   O el panel **Source Control** de VS Code (`Ctrl + Shift + G`): escribir el mensaje y presionar **Commit**.
 
4. Subir la rama y abrir un *pull request* en GitHub para que otro integrante lo revise antes de integrarlo a `main`:
```bash
   git push -u origin nombre-de-la-tarea
```
 
**Buenas prácticas para los mensajes de commit:** empezar con un verbo y decir qué cambió (por ejemplo, "Corrige el código de la serie IPC SAE" o "Agrega consultas SQL con funciones de ventana"). Evitar mensajes como "cambios", "prueba" o "final".
 
**Nunca se suben** el archivo `.env`, la carpeta `data/` ni la base de datos: el `.gitignore` ya los excluye.
 
## Hitos del proyecto
 
| Hito | Fecha | Entregable | Estado |
|---|---|---|---|
| Hito 1: Propuesta | Semana 4 | Documento breve con la variable objetivo, la pregunta de proyección, las series y fuentes tentativas, los mecanismos económicos y el enlace al repositorio. | Entregado |
| Hito 2: Avance de datos | Semana 8 | Extracción programática, base de datos relacional poblada y consultas SQL. Se entrega con el tag `hito-2`. | En curso |
| Hito 3: Entrega final | Semana 13 | Informe final, repositorio reproducible y monitor en Power BI (`.pbix`). | Pendiente |
 
## Referencias
 
- Apablaza, V., & Ortiz, J. (2024). *Determinantes de la tasa de política monetaria en Chile*. Documento de Trabajo N°30. Observatorio del Contexto Económico, Universidad Diego Portales. https://ocec.udp.cl/cms/wp-content/uploads/2024/03/DT30.pdf
- Banco Central de Chile. (s.f.). *Política monetaria*. https://www.bcentral.cl
- Banco Central de Chile. (2020). *La política monetaria del Banco Central de Chile en el marco de metas de inflación*. Santiago: Banco Central de Chile. https://www.bcentral.cl/documents/33528/133301/PoliticaMonetariaBcchMarcoMetasInflacion2020.pdf
- Caputo, R., & Herrera, L. O. (2013). *Efficient CPI-based Taylor rules in small open economies*. Documento de Trabajo N°694. Banco Central de Chile.
- Galí, J., & Monacelli, T. (2005). Monetary policy and exchange rate volatility in a small open economy. *The Review of Economic Studies*, 72(3), 707–734.
- Hodrick, R. J., & Prescott, E. C. (1997). Postwar U.S. business cycles: An empirical investigation. *Journal of Money, Credit and Banking*, 29(1), 1–16.