
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


## 7. Evaluación fuera de muestra a distintos horizontes

Para evaluar la capacidad predictiva de la Regla de Taylor a mediano y largo plazo, se realizaron nueve ejercicios de pronóstico con fechas de corte entre septiembre de 2016 y septiembre de 2024.

En cada corte se estimaron los coeficientes utilizando los datos disponibles hasta esa fecha. Posteriormente, se construyeron pronósticos recursivos a 6, 12 y 24 meses, manteniendo constantes las variables explicativas en sus últimos valores disponibles al momento de la proyección.

Los pronósticos se compararon con un modelo ingenuo, que supone que la TPM permanece constante en el valor observado al inicio de cada período.

### Resultados de la evaluación

| Horizonte | MAE Taylor | RMSE Taylor | MAE ingenuo | RMSE ingenuo |
|---|---:|---:|---:|---:|
| 6 meses | 1,1648 | 1,5547 | 1,0311 | 1,6430 |
| 12 meses | 2,7167 | 3,6135 | 2,0944 | 3,4113 |
| 24 meses | 4,5252 | 6,8272 | 3,6767 | 4,9713 |

Las métricas se expresan en puntos porcentuales de la TPM.

### Interpretación económica

A seis meses, los resultados son mixtos: el modelo ingenuo presenta un menor MAE, mientras que la Regla de Taylor alcanza un menor RMSE.

A doce meses, el modelo ingenuo registra menores errores en ambas métricas. Esta diferencia también se observa a veinticuatro meses, donde la Regla de Taylor presenta errores considerablemente mayores.

En general, los resultados muestran que la Regla de Taylor no supera de manera consistente al modelo ingenuo en los horizontes analizados.

Una posible explicación es la persistencia de la TPM y la dificultad de proyectar su trayectoria durante períodos de cambios importantes en las condiciones económicas.

### Limitaciones de la evaluación

Los pronósticos se construyeron manteniendo constantes las variables explicativas. Por ello, los resultados dependen de este supuesto y no representan necesariamente el desempeño de un modelo que incorpore pronósticos de inflación, actividad y tasas internacionales.

Además, la evaluación considera nueve cortes temporales, con períodos de pronóstico que pueden superponerse. Esto limita la cantidad de evidencia independiente disponible para comparar los modelos.

Los resultados permiten evaluar el desempeño histórico del procedimiento utilizado, pero no garantizan que el comportamiento futuro sea similar.

### Implicancias para el proyecto

La Regla de Taylor resulta útil para analizar la relación entre la política monetaria y sus determinantes macroeconómicos. Sin embargo, su capacidad predictiva debe contrastarse con modelos alternativos.

Por esta razón, las proyecciones futuras a 6, 12 y 24 meses se presentan como un escenario condicionado, cuya interpretación deberá complementarse con los demás modelos del Hito 3.
