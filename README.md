# Proyecto_Economia

Proyecto del curso Ciencia de datos para la economía, Facultad de Administración y Economía, Universidad Diego Portales.

Profesor: Luis Cuevas

Integrantes: Daniel Cornejo, Catarí Garrido, Laura Ruiz, Francisca Silva

## De qué se trata

Hacemos un seguimiento de la coyuntura macroeconómica chilena y proyectamos la Tasa de Política Monetaria (TPM) del Banco Central.

Variable objetivo: TPM.

Pregunta que guía el trabajo: ¿cuál es la trayectoria esperada de la TPM en Chile durante los próximos 6 a 24 meses, según la evolución de sus principales determinantes macroeconómicos y una regla de política monetaria estimada con datos chilenos?

Para responderla estimamos una regla de Taylor basada en inflación del IPC, siguiendo la versión de Caputo y Herrera (2013) para economías pequeñas y abiertas:

    i_t = r_t + φ_π · E_t(π_t+1) + φ_y · x_t

donde i_t es la TPM, r_t la tasa natural de interés real, E_t(π_t+1) la inflación esperada del IPC y x_t la brecha de actividad, que construimos aplicando el filtro de Hodrick-Prescott al Imacec. Después comparamos la TPM que predice la regla con la TPM que efectivamente se observó.

## Carpetas

- `extraccion/` — scripts que descargan las series desde las APIs
- `base_datos/` — datos descargados y datos ya procesados
- `sql/` — esquema y consultas de la base de datos
- `notebooks/` — análisis, estimación y proyección
- `dashboard/` — visualización del monitor de coyuntura

## Datos

Usamos 13 series, todas descargadas por API. La fuente principal es la Base de Datos Estadísticos del Banco Central de Chile (servicio SieteRestWS) y la complementaria es FRED, para los indicadores externos.

| # | Serie | Fuente | Frecuencia |
|---|---|---|---|
| 1 | TPM | BCCh | Diaria |
| 2 | IPC | BCCh/INE | Mensual |
| 3 | IPC SAE | BCCh/INE | Mensual |
| 4 | Imacec | BCCh | Mensual |
| 5 | Tipo de cambio nominal (dólar observado) | BCCh | Diaria/Mensual |
| 6 | Expectativas de inflación (EEE) | BCCh | Mensual |
| 7 | Expectativas de inflación (EOF) | BCCh | Quincenal |
| 8 | Tasas BCU / BCP / PDBC | BCCh | Diaria/Mensual |
| 9 | Tasa de desempleo | BCCh/INE | Mensual |
| 10 | Índice de remuneraciones | BCCh/INE | Mensual |
| 11 | Precio del cobre | FRED | Mensual |
| 12 | Fed Funds Rate | FRED | Diaria/Mensual |
| 13 | Índice de precios/actividad de EE.UU. | FRED | Mensual |

## Cómo reproducir el análisis

Se necesita Python 3.10 o superior, una cuenta en la BDE del Banco Central (https://si3.bcentral.cl/Siete/) y una API key de FRED (https://fred.stlouisfed.org/docs/api/api_key.html). Ambas son gratuitas.

1. Clonar el repositorio e instalar las dependencias:

```
git clone https://github.com/danielcornejo2/Proyecto_Economia.git
cd Proyecto_Economia
pip install -r requirements.txt
```

2. Crear un archivo `.env` en la raíz con las credenciales:

```
BCCH_USER=correo@ejemplo.cl
BCCH_PASS=contraseña
FRED_API_KEY=api_key
```

Este archivo no se sube al repositorio, está en el `.gitignore`.

3. Descargar las series y armar la base:

```
python extraccion/descarga_bcch.py
python extraccion/descarga_fred.py
python extraccion/construir_base.py
```

4. Correr los notebooks de `notebooks/` en orden.

5. Para ver el dashboard: `streamlit run dashboard/app.py`

## Referencias principales

- Caputo, R., y Herrera, L. O. (2013). Efficient CPI-based Taylor rules in small open economies. Documento de Trabajo N°694, Banco Central de Chile.
- Galí, J., y Monacelli, T. (2005). Monetary policy and exchange rate volatility in a small open economy. The Review of Economic Studies, 72(3), 707-734.
- Hodrick, R. J., y Prescott, E. C. (1997). Postwar U.S. business cycles: An empirical investigation. Journal of Money, Credit and Banking, 29(1), 1-16.
- Apablaza, V., y Ortiz, J. (2024). Determinantes de la tasa de política monetaria en Chile. Documento de Trabajo N°30, OCEC UDP.
- Banco Central de Chile (2020). La política monetaria del Banco Central de Chile en el marco de metas de inflación.
