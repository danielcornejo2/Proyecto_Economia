# Hito 3 - Datos y fuentes de información

## 1. Fuentes de información

Para el desarrollo del proyecto "La TPM en Chile:
monitos de coyuntura y proyección con una regla 
de política monetaria", se utilizan series
macroeconómicas provenientes de fuentes oficiales
naciones e internacionales.

La información se obtiene mediante las APIs del
Banco Central de Chile (BCCh) y de Federal Reserve
Economic Data (FRED), permitiendo construir una
base de datos para el análisis económico y la
elaboración de pronósticos de la Tasa de Política
Monetaria (TPM).

El proyecto considera 13 series económicas:
9 provenientes del Banco Central de Chile y
4 de FRED.

Estas series permiten estudiar la evolución
de la TPM y su relación con variables como
la inflación, la actividad económica, las 
expectativas y ,las condiciones financieras.

## 2. Banco Central de Chile (BCCh)

### 2.1. Descripción de la fuente

El Banco Central de Chile costituye la principal
fuente de información del proyecto, debido a que
proporciona estadísticas económicas y financieras 
relevantes para el análisis de la política monetaria.

Los datos se obtienen desde la Base de Datos
Estadísticos (BDE), utilizando el servicio
SieteRestWS del Banco Central.

Esta herramienta permite acceder de manera
programática a las series económicas, evitando
la descarga manual de información.

### 2.2. Variables utilizadas

El proyecto incorpora nueve series provenientes
del Banco Central de Chile:

1. Tasa de Política Monetaria (TPM).
2. Índice de Precios al Consumidor (IPC).
3. IPC sin alimentos ni energía (IPC SAE).
4. Índice Mensual de Actividad Económica (Imacec).
5. Tipo de cambio nominal (dólar observado).
6. Expectativas de inflación a 12 meses (EEE).
7. Tasa de bonos en pesos a 10 años (BCP).
8. Tasa de bonos en UF a 10 años (BCU).
9. Tasa de desocupación nacional.

Estas variables permiten analizar las condiciones
monetarias, inflacionarias, productivas y
financieras de la economía chilena.

La TPM corresponde a la variable principal
del estudio, mientras que las demás series
permiten examinar sus determinantes y
contextualizar su comportamiento.

### 2.3. Importancia para la investigación

La utilización de información del Banco Central
permite estudiar la evolución histórica de la TPM
y su relación con las principales condiciones
macroeconómicas nacionales.

En particular, el IPC y el IPC SAE proporcionan
información sobre las presiones inflacionarias,
mientras que el Imacec permite analizar
el comportamiento de la actividad económica.

Las expectativas de inflación y las tasas
de mercado aportan información sobre las
condiciones financieras y monetarias.

Estas variables resultan relevantes para
el análisis de la política monetaria y
su relación con el marco de la regla de Taylor.

## 3. Federal Reserve Economic Data (FRED)

### 3.1. Descripción de la fuente

Federal Reserve Economic Data (FRED) es una
plataforma de información económica administrada
por el Banco de la Reserva Federal de St. Louis,
en Estados Unidos.

Esta fuente proporciona acceso a series
económicas nacionales e internacionales,
permitiendo complementar el análisis de
las condiciones macroeconómicas chilenas.

En el proyecto, la información se obtiene
mediante la API de FRED, utilizando
procedimientos automatizados en Python.

### 3.2. Variables utilizadas

El proyecto incorpora cuatro series
provenientes de FRED:

1. Precio internacional del cobre.
2. Tasa de fondos federales de Estados Unidos.
3. Índice de Precios al Consumidor de Estados Unidos.
4. Índice de producción industrial estadounidense.

Estas variables permiten incorporar información
del entorno económico internacional al análisis
de la TPM en Chile.

### 3.3. Importancia para la investigación

La incorporación de indicadores internacionales
permite contextualizar los factores externos
que pueden influir sobre la economía chilena.

ata de fondos federales proporciona
información sobre las condiciones monetarias
de Estados Unidos y su posible relación 
con las tasas de interés y el tipo de cambio.

Por su parte, el precio internacional del cobre
permite considerar la importancia de los
términos de intercambio para una economía
exportadora como Chile.

El IPC estadounidense y la producción industrial
permiten observar las condiciones de inflación
y actividad económica del entorno externo.

De esta manera, las series de FRED complementan
la información nacional y permiten ampliar
el análisis de los determinantes de la TPM.

## 4. Integración de las fuentes

Las series del Banco Central de Chile y FRED
se integran mediante un proceso automatizado
de extracción, almacenamiento y análisis.

Los scripts utilizados para obtener la
información se encuentran en el repositorio
original del proyecto:

- extraccion/E_BCCH.py
- extraccion/E_FRED.py

Los datos descargados se almacenan inicialmente
en archivos CSV y posteriormente se incorporan
a una base de datos relacional SQLite.

El proyecto utiliza una frecuencia mensual
para integrar las series, convirtiendo las
observaciones de mayor frecuencia mediante
promedios mensuales cuando corresponde.

La fecha de corte documentada para los datos
del Hito 2 es el 30 de septiembre de 2026.

Esta organización permite trabajar con
información estructurada y facilita la
reproducción de los análisis económicos.

## 5. Consideraciones sobre los datos

La utilización de fuentes oficiales permite 
trabajar con series económicas documentadas
y procedimientos de extracción reproducibles.

Sin embargo, las variables presentan
diferencias en sus períodos de disponibilidad
y en sus frecuencias originales.

Por esta razón, el proyecto contempla
procedimientos de transformación y 
validación antes de utilizar la información
en los análisis y modelos de pronóstico.

Las características particulares de cada
serie y las transformaciones aplicadas
se documentarán en los siguientes apartados.

## 6. Descripción de las series económicas

### 6.1. Catálogo de variables

El proyecto utiliza 13 series económicas provenientes
del Banco Central de Chile (BCCh) y de Federal Reserve
Economic Data (FRED).

Estas variables permiten analizar la evolución de la
Tasa de Política Monetaria (TPM), sus principales
determinantes macroeconómicos y las condiciones
económicas nacionales e internacionales.

La TPM corresponde a la variable objetivo de la
investigación, mientras que las demás series cumplen
funciones explicativas o de contextualización económica.

### 6.2. Series del Banco Central de Chile

El proyecto considera nueve series provenientes
del Banco Central de Chile.

| Serie | Código API | Unidad | Frecuencia original |
|---|---|---|---|
| TPM | F022.TPM.TIN.D001.NO.Z.M | % anual | Mensual |
| IPC | F074.IPC.VAR.Z.Z.C.M | % variación mensual | Mensual |
| IPC SAE | F074.IPCSAE.VAR.Z.EP23.Z.M | % variación mensual | Mensual |
| Imacec | F032.IMC.IND.Z.Z.EP18.Z.Z.0.M | Índice 2018=100 | Mensual |
| Dólar observado | F073.TCO.PRE.HIST.M | Pesos por dólar | Mensual |
| Expectativas EEE | F089.IPC.V12.14.M | % | Mensual |
| Tasa BCP 10 años | F022.BCLP.TIS.AN10.NO.Z.D | % anual | Diaria |
| Tasa BCU 10 años | F022.BUF.TIS.AN10.UF.Z.D | % anual (en UF) | Diaria |
| Desempleo | F049.DES.TAS.INE9.10.M | % de la fuerza de trabajo | Mensual |

### 6.3. Función económica de las variables nacionales

**Tasa de Política Monetaria (TPM)**

Constituye la variable principal del proyecto.
Representa el instrumento utilizado por el Banco
Central de Chile para conducir la política monetaria
y contribuir al cumplimiento de la meta de inflación.

El análisis busca estudiar su comportamiento
histórico y elaborar pronósticos sobre su
trayectoria futura.

**Índice de Precios al Consumidor (IPC)**

Permite analizar la evolución de la inflación
general de la economía chilena.

Su importancia radica en que las desviaciones
de la inflación respecto de la meta del Banco
Central constituyen uno de los elementos
considerados en las decisiones de política monetaria.

**IPC sin alimentos ni energía (IPC SAE)**

Representa una medida de inflación subyacente
que excluye los componentes de alimentos y energía.

Permite analizar las presiones inflacionarias
subyacentes y complementar el estudio del IPC general.

**Índice Mensual de Actividad Económica (Imacec)**

Proporciona información sobre la evolución
de la actividad económica chilena.

En el proyecto se utiliza como insumo para
estimar la brecha de actividad mediante
el filtro de Hodrick-Prescott.

Esta brecha permite estudiar si la actividad
económica se encuentra por encima o por
debajo de su tendencia estimada.

**Dólar observado**

Representa el tipo de cambio nominal
entre el peso chileno y el dólar estadounidense.

Permite analizar el canal cambiario y
su posible relación con las presiones
inflacionarias y la política monetaria.

**Expectativas de inflación (EEE)**

Corresponden a las expectativas de inflación
a 12 meses obtenidas mediante la Encuesta
de Expectativas Económicas.

Esta variable permite estudiar las
perspectivas inflacionarias y su relación
con las decisiones del Banco Central.

**Tasa BCP a 10 años**

Corresponde a una tasa de interés de
bonos en pesos a largo plazo.

Se utiliza para contextualizar las
condiciones del mercado financiero
y la transmisión de la política monetaria.

**Tasa BCU a 10 años**

Representa una tasa de interés de
bonos denominados en UF a largo plazo.

Permite analizar las condiciones de
financiamiento real y complementar
el estudio de las tasas de mercado.

**Tasa de desempleo**

Mide la proporción de personas desocupadas
respecto de la fuerza de trabajo.

Esta variable permite analizar las
condiciones del mercado laboral y
las posibles presiones sobre la
actividad económica y la inflación.

### 6.4. Series de Federal Reserve Economic Data

El proyecto incorpora cuatro series económicas
internacionales provenientes de FRED.

| Serie | Código API | Unidad | Frecuencia original |
|---|---|---|---|
| Precio del cobre | PCOPPUSDM | Dólares por tonelada métrica | Mensual |
| Fed Funds Rate | FEDFUNDS | % anual | Mensual |
| IPC de Estados Unidos | CPIAUCSL | Índice 1982-84=100 | Mensual |
| Producción industrial de EE.UU. | INDPRO | Índice 2017=100 | Mensual |

### 6.5. Función económica de las variables internacionales

**Precio internacional del cobre**

Permite incorporar información sobre los
términos de intercambio de la economía chilena.

Dado que el cobre constituye una exportación
relevante para Chile, sus variaciones pueden
influir sobre la actividad económica y
el tipo de cambio.

**Tasa de fondos federales de Estados Unidos**

Representa una medida de las condiciones
monetarias estadounidenses.

Su incorporación permite estudiar la relación
entre las tasas internacionales, las condiciones
financieras y el comportamiento de la TPM chilena.

**Índice de Precios al Consumidor de Estados Unidos**

Permite analizar la evolución del nivel
de precios de la economía estadounidense.

Esta variable proporciona información sobre
las condiciones inflacionarias externas,
relevantes para una economía abierta como Chile.

**Producción industrial estadounidense**

Representa un indicador de la actividad
industrial de Estados Unidos.

Permite contextualizar las condiciones
de la demanda externa y su posible
relación con la actividad económica chilena.

### 6.6. Clasificación de las variables

Las series económicas pueden organizarse
según la función prevista en el proyecto.

**Variable objetivo:**

- Tasa de Política Monetaria (TPM).

**Variables explicativas consideradas:**

- IPC general.
- IPC SAE.
- Expectativas de inflación EEE.
- Imacec y brecha de actividad.
- Tasa de desempleo.
- Dólar observado.
- Tasa de fondos federales.

**Variables de contexto económico:**

- Precio internacional del cobre.
- IPC de Estados Unidos.
- Producción industrial estadounidense.
- Tasas BCP y BCU a 10 años.

Esta clasificación corresponde al planteamiento
documentado en el repositorio original.

La selección definitiva de variables utilizadas
en cada modelo de pronóstico deberá coincidir
con la especificación implementada en Python.

### 6.7. Importancia del conjunto de datos

La integración de estas 13 series permite
estudiar la TPM desde una perspectiva
macroeconómica que considera factores
nacionales e internacionales.

Las variables de precios, actividad y
expectativas proporcionan información
relevante para el marco de la regla de Taylor.

Por su parte, los indicadores financieros
y externos permiten complementar el análisis
de las condiciones económicas que enfrenta Chile.

De esta manera, el conjunto de datos
constituye la base para desarrollar el
diagnóstico de coyuntura y los modelos
de pronóstico correspondientes al Hito 3.
