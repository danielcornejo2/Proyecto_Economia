
-- 1) JOIN: cada observación con el nombre de su serie y su tema.
SELECT t.tema,
       s.nombre,
       s.tipo,
       s.unidad,
       s.frecuencia,
       o.fecha,
       o.valor
FROM observaciones AS o
JOIN series AS s ON s.id_serie = o.id_serie
JOIN temas  AS t ON t.id_tema  = s.id_tema
ORDER BY t.tema, s.nombre, o.fecha;

-- 2) GROUP BY: agrupa por serie y mes las observaciones ya mensualizadas
-- por los scripts de extracción. AVG calcula el promedio de los valores
-- disponibles y COUNT cuenta las observaciones no nulas de cada mes.
-- La frecuencia indicada corresponde a la frecuencia original de la API.
SELECT s.nombre,
       s.frecuencia,
       strftime('%Y-%m', o.fecha) AS mes,
       AVG(o.valor)               AS valor_mensual,
       COUNT(o.valor)             AS n_obs
FROM observaciones AS o
JOIN series AS s ON s.id_serie = o.id_serie
GROUP BY s.nombre, s.frecuencia, mes
ORDER BY s.nombre, mes;

-- 3) FUNCIÓN DE VENTANA: variación en 12 meses, calculada dentro de cada serie (partitionby) sobre las series ya mensuales.
--La transformación depende del TIPO de serie:
-- - indice / nivel -> variación porcentual contra 12 meses atrás
-- - tasa           -> diferencia en puntos porcentuales. Calcular el cambio % de una tasa que pasa de 5% a 6%
--                     daría "+20%", que no significa nada
--  - variacion     -> la serie YA es la variación mensual (IPC e IPC SAE), así que la inflación anual es el
--                     producto compuesto de los últimos 12 meses, no una variación sobre la variación
WITH mensual AS (
    SELECT o.id_serie,
           strftime('%Y-%m', o.fecha) AS mes,
           AVG(o.valor)               AS valor
    FROM observaciones AS o
    GROUP BY o.id_serie, mes
)
SELECT s.nombre,
       s.tipo,
       m.mes,
       ROUND(m.valor, 2) AS valor,
       ROUND(
           CASE s.tipo
               WHEN 'tasa'      THEN m.valor - LAG(m.valor, 12) OVER w
               WHEN 'variacion' THEN CASE WHEN COUNT(*) OVER w12 = 12
                                          THEN 100.0 * (EXP(SUM(LN(1 + m.valor/100.0)) OVER w12) - 1)
                                     END
               ELSE 100.0 * (m.valor / LAG(m.valor, 12) OVER w - 1)
           END, 2) AS variacion_12m,
       CASE s.tipo WHEN 'tasa' THEN 'puntos porcentuales' ELSE '%' END AS unidad_variacion
FROM mensual AS m
JOIN series AS s ON s.id_serie = m.id_serie
WINDOW w   AS (PARTITION BY m.id_serie ORDER BY m.mes),
       w12 AS (PARTITION BY m.id_serie ORDER BY m.mes ROWS BETWEEN 11 PRECEDING AND CURRENT ROW)
ORDER BY s.nombre, m.mes;