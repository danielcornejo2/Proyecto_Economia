
-- 1) JOIN: cada observación con el nombre de su serie y su tema.
SELECT t.tema,
       s.nombre,
       s.unidad,
       s.frecuencia,
       o.fecha,
       o.valor
FROM observaciones AS o
JOIN series AS s ON s.id_serie = o.id_serie
JOIN temas  AS t ON t.id_tema  = s.id_tema
ORDER BY t.tema, s.nombre, o.fecha;

-- 2) GROUP BY: lleva todas las series a frecuencia mensual. Las diarias (TPM, dólar, tasas) se promedian dentro del mes. 
--Las que ya son mensuales quedan igual, porque el promedio de  un solo dato es ese dato. n_obs permite detectar meses incompletos.
SELECT s.nombre,
       s.frecuencia,
       strftime('%Y-%m', o.fecha) AS mes,
       AVG(o.valor)               AS valor_mensual,
       COUNT(o.valor)             AS n_obs
FROM observaciones AS o
JOIN series AS s ON s.id_serie = o.id_serie
GROUP BY s.nombre, s.frecuencia, mes
ORDER BY s.nombre, mes;

-- 3) FUNCIÓN DE VENTANA: variación en 12 meses, calculada dentro de cada serie (PARTITION BY) sobre las series ya mensuales.
--    La transformación depende de la unidad: - Serie en índice o nivel  -> variación porcentual.
--                                            - Serie que ya es una tasa -> diferencia en puntosporcentuales. Calcular el cambio % de 
--una tasa que pasa de 5% a 6% daría "+20%", que no significa nada. Lo correcto es decir que subió 1 punto porcentual.
WITH mensual AS (
    SELECT o.id_serie,
           strftime('%Y-%m', o.fecha) AS mes,
           AVG(o.valor)               AS valor
    FROM observaciones AS o
    GROUP BY o.id_serie, mes
)
SELECT s.nombre,
       s.unidad,
       m.mes,
       ROUND(m.valor, 2) AS valor,
       ROUND(LAG(m.valor, 12) OVER (PARTITION BY m.id_serie ORDER BY m.mes), 2) AS valor_hace_12m,
       ROUND(
           CASE
               WHEN s.unidad = 'tasa'
                   THEN m.valor - LAG(m.valor, 12) OVER (PARTITION BY m.id_serie ORDER BY m.mes)
               ELSE 100.0 * (m.valor / LAG(m.valor, 12) OVER (PARTITION BY m.id_serie ORDER BY m.mes) - 1)
           END, 2)        AS variacion_12m,
       CASE WHEN s.unidad = 'tasa' THEN 'puntos porcentuales' ELSE '%' END AS unidad_variacion
FROM mensual AS m
JOIN series AS s ON s.id_serie = m.id_serie
ORDER BY s.nombre, m.mes;
