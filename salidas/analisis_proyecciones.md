# Análisis de las proyecciones de la TPM

Cifras actualizadas con la TPM de fin de mes desde agosto de 2001 y con la base cortada al 30 de septiembre de 2026. Todas se reproducen con `python ejecutar_todo.py`. Las proyecciones y las métricas de evaluación también quedan guardadas en `data/base.db`, en las tablas `proyecciones_tpm` y `metricas_modelos`.

## 1. Metodología

Se proyectó la TPM de Chile a 24 meses con tres modelos:

- **Regla de Taylor** estimada con toda la muestra (TPM rezagada, brecha de inflación esperada, brecha de actividad y Fed Funds). La proyección es recursiva: cada valor proyectado se usa como la TPM rezagada del mes siguiente.
- **ARIMA(2,1,0)** de la TPM, elegido por AIC, con un intervalo de confianza de 80 %.
- **Caminata aleatoria** (modelo ingenuo): la TPM se mantiene en su último valor.

La última TPM observada (septiembre de 2026) es 4,50 %.

## 2. Escenarios

La Regla de Taylor se proyectó en cuatro escenarios para sus determinantes. Los tamaños de los shocks son ilustrativos.

| Escenario | Supuesto |
|---|---|
| Base | Determinantes constantes en su último valor |
| Convergencia | Expectativas vuelven a la meta de 3 % y la brecha de actividad se cierra en 12 meses |
| Riesgo al alza | Expectativas 1 pp sobre su nivel actual (por ejemplo, por una depreciación o un shock de petróleo) y la Fed sube 0,5 pp |
| Riesgo a la baja | Actividad 2 pp bajo su tendencia (recesión global), expectativas −0,5 pp y la Fed recorta 1 pp |

## 3. Resultados

| Modelo / escenario | 6 meses (mar-2027) | 12 meses (sep-2027) | 24 meses (sep-2028) |
|---|---:|---:|---:|
| Taylor: base | 4,21 % | 4,05 % | 3,90 % |
| Taylor: convergencia | 4,21 % | 4,04 % | 3,89 % |
| Taylor: riesgo al alza | 5,75 % | 6,47 % | 7,10 % |
| Taylor: riesgo a la baja | 3,07 % | 2,26 % | 1,54 % |
| ARIMA(2,1,0) | 4,50 % | 4,50 % | 4,50 % |
| Intervalo 80 % del ARIMA | 2,64 % a 6,36 % | 1,23 % a 7,77 % | 0,50 % a 9,72 % |
| Caminata aleatoria | 4,50 % | 4,50 % | 4,50 % |

El límite inferior del intervalo del ARIMA no baja de 0,5 %, el mínimo histórico de la TPM (2020).

## 4. Interpretación económica

- **Escenario base: recortes graduales.** Con las expectativas y la actividad actuales, la regla indica espacio para bajar la TPM de 4,50 % a cerca de 3,9 % en dos años. El escenario de convergencia da casi lo mismo, porque las brechas actuales ya están cerca de cero.
- **El ARIMA proyecta una tasa estable** (4,50 %). La TPM no se ha movido en los últimos meses y el modelo no detecta una tendencia que extrapolar.
- **El principal riesgo es la inflación esperada.** Como la regla responde con fuerza a las expectativas (efecto de largo plazo de 3,4), si se desanclan 1 pp la TPM debería subir a cerca de 7 % en dos años.
- **A la baja, una recesión global** llevaría la TPM a cerca de 1,5 %.
- El intervalo del ARIMA confirma que la incertidumbre a 24 meses es muy alta.

Estas trayectorias son proyecciones condicionadas del modelo, no decisiones anunciadas por el Banco Central.

## 5. Evaluación fuera de muestra a distintos horizontes

Se hicieron nueve ejercicios de pronóstico, con cortes en septiembre de cada año entre 2016 y 2024. En cada corte, cada modelo se estimó solo con los datos disponibles hasta esa fecha y pronosticó a 6, 12 y 24 meses. En la Regla de Taylor, las variables explicativas se mantienen en su valor del corte.

RMSE en puntos porcentuales de TPM; entre paréntesis, el R² OOS frente al modelo ingenuo (positivo = le gana):

| Horizonte | Ingenuo | Regla de Taylor | ARIMA(2,1,2) |
|---|---:|---:|---:|
| 6 meses | 2,036 | 1,828 (+0,19) | 1,427 (+0,51) |
| 12 meses | 3,467 | 3,594 (−0,07) | 2,968 (+0,27) |
| 24 meses | 5,008 | 6,648 (−0,76) | 4,967 (+0,02) |

El ARIMA de esta evaluación es (2,1,2), porque su orden se eligió solo con datos hasta septiembre de 2016.

### Interpretación

- **El ARIMA es el modelo con menor error a 6 y 12 meses** y le gana al modelo ingenuo en ambos horizontes.
- **La Regla de Taylor solo mejora al ingenuo a 6 meses.** A 12 y 24 meses pierde, principalmente porque sus determinantes se mantienen fijos en el valor del corte y no recogen los cambios posteriores en inflación y actividad (por ejemplo, el shock de 2021–2022).
- **A 24 meses ningún modelo supera con claridad al ingenuo.**

### Limitaciones de la evaluación

- Son nueve cortes por horizonte, con períodos de pronóstico que se superponen. Hay poca evidencia independiente y no se aplicó un test formal de significancia de las diferencias.
- Mantener constantes las variables explicativas es una simplificación. Un modelo que incorpore pronósticos de inflación, actividad y tasas internacionales podría mejorar el desempeño de la regla.
- El desempeño pasado no garantiza el desempeño futuro.

## 6. Conclusión

La Regla de Taylor es útil para explicar la TPM: sus coeficientes son significativos y coherentes con el principio de Taylor. También permite construir escenarios de riesgo. Como herramienta de pronóstico, en cambio, el ARIMA es más preciso a 6 y 12 meses.

La lectura conjunta sugiere una TPM entre 3,9 % y 4,5 % en el escenario central de los próximos dos años, con el desanclaje de las expectativas de inflación como principal riesgo al alza.