
# Guía de ejecución de la Regla de Taylor

## 1. Descripción

Esta sección reúne los códigos utilizados para estimar,
evaluar y proyectar la Tasa de Política Monetaria (TPM)
mediante una Regla de Taylor.

El análisis utiliza datos mensuales del Banco Central
de Chile y FRED, organizados en una base SQLite.

## 2. Base de datos

Los resultados se calculan con la base data/base.db,
con fecha de corte el 30 de septiembre de 2026.

La base no se sube al repositorio: se crea con
python carga.py (o con python ejecutar_todo.py,
que además corre todos los modelos en orden).

## 3. Preparación del entorno

Desde la raíz del proyecto se deben instalar las
dependencias indicadas en requirements.txt:

python -m pip install -r requirements.txt

Los códigos utilizan pandas, numpy y matplotlib,
además de los módulos propios del proyecto.

## 4. Archivos necesarios

Los programas utilizan el panel mensual generado por:

modelos/datos_modelo.py

Este archivo aplica los rezagos de publicación y calcula
la brecha de actividad en tiempo real (filtro HP de una
cola), para que los modelos no usen datos futuros.

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

## 7. Integración (completada)

- El panel mensual (modelos/datos_modelo.py) está integrado.
- La base se reconstruye con python carga.py.
- Se comprobó la ejecución desde un clon limpio del
  repositorio con python ejecutar_todo.py.
- Los resultados se comparan con el ARIMA y la caminata
  aleatoria en modelos/comparacion_modelos.py.
