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

