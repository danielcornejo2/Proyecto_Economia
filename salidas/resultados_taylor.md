# Resultados de la Regla de Taylor

Cifras actualizadas con la TPM de fin de mes desde agosto de 2001 (serie diaria del BCCh) y con la base cortada al 30 de septiembre de 2026. Todas se reproducen con `python ejecutar_todo.py`.

## 1. Estimación del modelo

Se estimó una Regla de Taylor con el panel mensual del proyecto (`modelos/datos_modelo.py`), que usa solo información disponible en cada mes: rezagos de publicación y brecha de actividad calculada con el filtro HP en tiempo real.

El período de entrenamiento va de marzo de 2005 a diciembre de 2024 (238 observaciones). Los errores estándar son robustos HAC (Newey-West, 12 rezagos), porque en datos mensuales los residuos suelen estar autocorrelacionados.

| Variable | Coeficiente | Error HAC | p-valor | Largo plazo β/(1−ρ) | p-valor largo plazo |
|---|---:|---:|---:|---:|---:|
| Constante | 0,249 | 0,052 | 0,000 | | |
| TPM rezagada (ρ) | 0,908 | 0,028 | 0,000 | | |
| Brecha de inflación esperada | 0,313 | 0,054 | 0,000 | 3,402 | 0,000 |
| Brecha de actividad | 0,029 | 0,015 | 0,059 | 0,317 | 0,029 |
| Fed Funds | 0,031 | 0,031 | 0,313 | 0,341 | 0,172 |

R² = 0,984. Con la muestra completa (hasta septiembre de 2026) los coeficientes son prácticamente iguales (ρ = 0,910; inflación esperada 0,308; actividad 0,028; Fed Funds 0,027), lo que indica que la regla es estable en el tiempo.

Interpretación:

- **Inercia.** El coeficiente de la TPM rezagada (0,91) es el de mayor magnitud y es muy significativo. El Banco Central ajusta la tasa de forma gradual, lo que coincide con Apablaza y Ortiz (2024).
- **Inflación esperada.** Es el determinante principal. Su respuesta de largo plazo (3,4) es mayor que 1, así que se cumple el principio de Taylor: ante un alza de las expectativas, la TPM sube más que proporcionalmente.
- **Actividad.** Tiene un efecto positivo y menor. Es significativa al 5 % en el largo plazo y al 10 % en el corto plazo.
- **Fed Funds.** No es significativa una vez que se controla por expectativas y actividad. Esto es coherente con un tipo de cambio flexible que da autonomía a la política monetaria.

Comparación con Caputo y Herrera (2013), respuestas de largo plazo de 1,174 (inflación esperada), 0,656 (brecha) y 1,2 (Fed Funds): los signos coinciden, pero la respuesta a la inflación esperada es mayor y la respuesta a la Fed es menor. Dos razones posibles:

- Se usa la brecha de expectativas de la EEE, que en Chile se desvía poco de la meta.
- La muestra incluye el ciclo 2021–2023, cuando la TPM subió de 0,5 % a 11,25 %.

## 2. Evaluación fuera de muestra a un mes

Se evaluaron 21 pronósticos mensuales entre enero de 2025 y septiembre de 2026, con coeficientes estimados hasta diciembre de 2024. Se compararon con un modelo ingenuo, que usa la TPM del mes anterior.

| Modelo | MAE | RMSE |
|---|---:|---:|
| Regla de Taylor | 0,1086 | 0,1357 |
| Modelo ingenuo | 0,0238 | 0,0772 |
| ARIMA(2,1,0), como referencia | 0,048 | 0,089 |

El modelo ingenuo obtuvo los menores errores. A un mes, la TPM casi no cambia, por lo que es muy difícil superar la regla de "la tasa se mantiene".

## 3. Validación temporal

Se repitió la evaluación con cuatro cortes de entrenamiento (diciembre de 2021, 2022, 2023 y 2024), pronosticando los 12 meses siguientes a cada corte.

| Corte | MAE Taylor | RMSE Taylor | MAE ingenuo | RMSE ingenuo |
|---|---:|---:|---:|---:|
| 2021-12 | 0,478 | 0,575 | 0,604 | 0,839 |
| 2022-12 | 0,249 | 0,320 | 0,250 | 0,445 |
| 2023-12 | 0,324 | 0,378 | 0,271 | 0,415 |
| 2024-12 | 0,130 | 0,161 | 0,042 | 0,102 |

La Regla de Taylor obtiene un menor RMSE que el modelo ingenuo en los cortes de 2021, 2022 y 2023, períodos de grandes movimientos de la TPM. En 2024, con la tasa casi estable, el modelo ingenuo es mejor. La regla aporta más cuando la política monetaria está en movimiento.

## 4. Interpretación del gráfico

El gráfico `salidas/graficos/comparacion_tpm.png` muestra que ambos modelos siguen la trayectoria de la TPM. La Regla de Taylor presenta mayores diferencias en algunos meses, coherentes con sus mayores MAE y RMSE en el período 2025–2026.

## 5. Limitaciones

- Las evaluaciones mantienen constantes las variables explicativas en su último valor, no sus valores futuros. Esto perjudica a la regla en horizontes largos.
- El período 2025–2026 cubre un solo ciclo de política monetaria (recortes graduales), con pocos meses de cambio.
- La comparación con los demás modelos a 6, 12 y 24 meses está en `salidas/resultados/comparacion_modelos_resumen.csv` y en `analisis_proyecciones.md`.