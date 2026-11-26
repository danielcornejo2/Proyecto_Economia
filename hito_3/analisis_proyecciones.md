
# Análisis de las proyecciones de la TPM

## 1. Metodología

Se proyectó la Tasa de Política Monetaria (TPM) de Chile mediante una Regla de Taylor estimada con datos mensuales provenientes de la base utilizada en el Hito 2.

La estimación considera la TPM rezagada, la brecha de inflación esperada, la brecha de actividad y la tasa de fondos federales de Estados Unidos.

Para construir las proyecciones se utilizó la información disponible hasta septiembre de 2026, último mes de la muestra.

La TPM futura se calculó de manera recursiva: cada valor proyectado se utilizó como TPM rezagada del mes siguiente.

## 2. Supuestos de proyección

Se construyó un escenario de referencia en el que las variables explicativas se mantienen constantes en sus últimos valores disponibles.

Este supuesto permite analizar la trayectoria implícita en la Regla de Taylor, pero no representa necesariamente la evolución futura de la economía.

Por lo tanto, los resultados deben interpretarse como proyecciones condicionadas y no como estimaciones definitivas de las decisiones del Banco Central.

## 3. Resultados

La última TPM observada, correspondiente a septiembre de 2026, fue de 4,50 %.

| Horizonte | Fecha | Regla de Taylor | Modelo ingenuo |
|---|---|---:|---:|
| 6 meses | Marzo 2027 | 4,1876 % | 4,50 % |
| 12 meses | Septiembre 2027 | 4,0029 % | 4,50 % |
| 24 meses | Septiembre 2028 | 3,8291 % | 4,50 % |

Los resultados muestran una trayectoria descendente de la TPM bajo el escenario considerado.

A seis meses, la tasa proyectada alcanza aproximadamente 4,19 %. A doce meses disminuye a 4,00 % y, al finalizar el horizonte de veinticuatro meses, llega a 3,83 %.

En contraste, el modelo ingenuo mantiene constante la TPM en 4,50 % durante todo el período.

## 4. Interpretación económica

La Regla de Taylor sugiere una reducción gradual de la TPM bajo los supuestos establecidos.

Esta trayectoria está condicionada por los coeficientes estimados y por la elevada persistencia de la tasa, reflejada en el coeficiente positivo de la TPM rezagada.

La disminución proyectada no debe interpretarse como una decisión anunciada por el Banco Central, sino como el resultado del modelo econométrico bajo un escenario específico.

## 5. Evaluación y limitaciones

En la evaluación fuera de muestra a un mes, realizada entre enero de 2025 y septiembre de 2026, el modelo ingenuo obtuvo menores errores que la Regla de Taylor.

| Modelo | MAE | RMSE |
|---|---:|---:|
| Regla de Taylor | 0,1035 | 0,1241 |
| Modelo ingenuo | 0,0310 | 0,0715 |

Por lo tanto, aunque la Regla de Taylor permite estudiar la relación entre la TPM y sus determinantes macroeconómicos, no superó al benchmark ingenuo en esa evaluación.

También se realizaron cuatro cortes de validación temporal, cuyos resultados muestran que el desempeño relativo de los modelos varía según el período analizado.

Es importante distinguir esta evaluación a un mes de las proyecciones recursivas a 6, 12 y 24 meses. Estas últimas todavía no cuentan con una evaluación fuera de muestra específica para cada horizonte.

Finalmente, mantener constantes las variables explicativas constituye una simplificación. Los cambios futuros en inflación, actividad o condiciones financieras internacionales podrían modificar las proyecciones.

## 6. Conclusión preliminar

La Regla de Taylor proyecta una disminución gradual de la TPM, desde 4,50 % en septiembre de 2026 hasta aproximadamente 3,83 % en septiembre de 2028.

Sin embargo, los resultados deben interpretarse con cautela debido a los supuestos del escenario y al desempeño del modelo frente al benchmark ingenuo.

Estas proyecciones deberán complementarse con los resultados de los demás modelos y la evaluación conjunta del proyecto.
