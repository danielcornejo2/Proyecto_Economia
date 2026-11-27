
# Guía de ejecución de la Regla de Taylor

## 1. Descripción

Esta sección reúne los códigos utilizados para estimar,
evaluar y proyectar la Tasa de Política Monetaria (TPM)
mediante una Regla de Taylor.

El análisis utiliza datos mensuales del Banco Central
de Chile y FRED, organizados en una base SQLite.

## 2. Base de datos

Los resultados fueron calculados utilizando una copia
de la base original del Hito 2, con fecha de corte
en septiembre de 2026.

Para ejecutar los programas, la base debe encontrarse en:

data/base.db

La base utilizada para las pruebas se conserva localmente.
Este archivo no forma parte de los commits de esta rama.

## 3. Preparación del entorno

Desde la raíz del proyecto se deben instalar las
dependencias indicadas en requirements.txt:

python -m pip install -r requirements.txt

Los códigos utilizan pandas, numpy y matplotlib,
además de los módulos propios del proyecto.

## 4. Archivos necesarios

Los programas utilizan el panel mensual generado por:

modelos/datos_modelo.py

Este archivo corresponde al trabajo desarrollado en la
rama feat/datos-modelo y deberá integrarse con el resto
del proyecto antes de la entrega definitiva.

## 5. Ejecución de los modelos

Los siguientes comandos deben ejecutarse desde la raíz
del repositorio.

### Evaluación fuera de muestra a un mes

python -m modelos.evaluacion_taylor

Compara la Regla de Taylor con el modelo ingenuo
mediante MAE y RMSE.

### Gráfico de evaluación

python -m modelos.grafico_taylor

Genera el gráfico de TPM observada y pronósticos
durante el período de evaluación.

### Validación temporal

python -m modelos.validacion_temporal

Evalúa los modelos utilizando cuatro cortes de
entrenamiento, entre diciembre de 2021 y 2024.

### Proyección futura

python -m modelos.proyeccion_taylor

Calcula una trayectoria recursiva de la TPM a 24 meses,
manteniendo constantes las variables explicativas.

### Gráfico de proyecciones

python -m modelos.grafico_proyeccion_taylor

Genera la comparación entre TPM histórica,
Regla de Taylor y modelo ingenuo hasta 2028.

### Evaluación de distintos horizontes

python -m modelos.evaluacion_horizontes

Evalúa los pronósticos a 6, 12 y 24 meses
utilizando nueve cortes históricos.

## 6. Resultados

Los archivos CSV se guardan en:

hito_3/resultados/

Los gráficos PNG se guardan en:

hito_3/graficos/

Los resultados corresponden a un escenario condicionado
y deben interpretarse junto con sus supuestos y
limitaciones metodológicas.

## 7. Pendientes de integración

- Incorporar oficialmente el panel mensual de Catari.
- Garantizar la disponibilidad o reconstrucción de la base.
- Comprobar la ejecución desde una instalación nueva.
- Integrar los resultados con los demás modelos del Hito 3.
