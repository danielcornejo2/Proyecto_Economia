# Resultados de la Regla de Taylor

## 1. Estimación del modelo

Se estimó una Regla de Taylor utilizando el panel mensual
construido a partir de la base de datos del Hito 2.

El período de entrenamiento comprende desde marzo de 2005
hasta diciembre de 2024, con 238 observaciones.

Los coeficientes estimados fueron:

| Variable | Coeficiente |
|---|---:|
| Constante | 0.2275 |
| TPM rezagada | 0.9139 |
| Brecha de inflación esperada | 0.3112 |
| Brecha de actividad | 0.0247 |
| Fed Funds | 0.0294 |

El coeficiente de la TPM rezagada es el de mayor magnitud,
lo que refleja una elevada persistencia de la política
monetaria. Esto es coherente con el ajuste gradual que suele
caracterizar las decisiones sobre tasas de interés.

Los coeficientes de inflación esperada, actividad y Fed Funds
son positivos. Sin embargo, todavía no se ha comprobado
su significancia estadística.

## 2. Evaluación fuera de muestra

Para evaluar la capacidad predictiva del modelo, se utilizaron
21 observaciones mensuales entre enero de 2025 y septiembre
de 2026.

Se comparó la Regla de Taylor con un modelo ingenuo, que
pronostica la TPM del mes siguiente utilizando el valor
observado en el mes anterior.

| Modelo | MAE | RMSE |
|---|---:|---:|
| Regla de Taylor | 0.1035 | 0.1241 |
| Modelo ingenuo | 0.0310 | 0.0715 |

El modelo ingenuo obtuvo menores errores en ambas métricas,
por lo que presentó un mejor desempeño predictivo en el
período evaluado.

Esto puede relacionarse con la persistencia de la TPM, ya
que sus variaciones mensuales fueron relativamente pequeñas
durante buena parte del período de evaluación.

## 3. Interpretación del gráfico

El gráfico de comparación muestra que ambos modelos
reproducen parte de la trayectoria observada de la TPM.

Sin embargo, la Regla de Taylor presenta mayores diferencias
respecto de los valores reales en algunos meses.

El modelo ingenuo sigue más de cerca la TPM observada,
lo que es consistente con sus menores valores de MAE y RMSE.

## 4. Limitaciones

Los resultados corresponden a una evaluación de pronósticos
a un mes y no permiten concluir cuál modelo será superior
para horizontes de 6 a 24 meses.

Además, los coeficientes se mantuvieron fijos durante el
período de evaluación. Será necesario complementar este
análisis con otras ventanas de entrenamiento y validación
temporal para evaluar su estabilidad.

También queda pendiente verificar la significancia
estadística de los coeficientes y contrastar estos resultados
con los demás modelos del proyecto.