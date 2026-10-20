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
| 10 | `tasa_depositos_90d` | Tasa de depósitos en bolsa a 90 días, pesos | `F022.TDB.TIS.D090.NO.Z.D` | BCCh | Diaria | Tasas de mercado |
| 11 | `precio_cobre` | Precio internacional del cobre (FMI) | `PCOPPUSDM` | FRED | Mensual | Externo |
| 12 | `fed_funds` | Tasa de fondos federales de EE.UU. | `FEDFUNDS` | FRED | Mensual | Externo |
| 13 | `ipc_eeuu` | IPC de EE.UU. (CPI-U), desestacionalizado | `CPIAUCSL` | FRED | Mensual | Externo |
| 14 | `produccion_industrial_eeuu` | Producción industrial de EE.UU. | `INDPRO` | FRED | Mensual | Externo |
 
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
 
## Estructura del repositorio
 
```
Proyecto_Economia/
├── extraccion/             # descarga de las series desde las APIs
│   ├── E_BCCH.py           #   Banco Central de Chile -> data/raw/bcch/
│   └── E_FRED.py           #   FRED -> data/raw/fred/
├── bd/
│   └── crear_base.py       # carga los CSV en la base SQLite data/base.db
├── notebooks/              # análisis de coyuntura, regla de Taylor y proyección
├── data/                   # se genera al ejecutar; NO se sube a GitHub
│   ├── raw/bcch/, raw/fred/   # CSV descargados, una subcarpeta por fuente
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