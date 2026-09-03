# La TPM en Chile: monitor de coyuntura y proyección con una regla de política monetaria
 
**Proyecto del curso Ciencia de Datos para la Economía — Facultad de Administración y Economía, Universidad Diego Portales.**
 
**Profesor:** Luis Cuevas

**Integrantes:** Daniel Cornejo, Catarí Garrido, Laura Ruiz, Francisca Silva
 
---
 
## Contexto y motivación
 
La Tasa de Política Monetaria (TPM) es uno de los principales instrumentos que utiliza el Banco Central de Chile (BCCh) para conducir la política monetaria y cumplir su objetivo de estabilidad de precios. A través de sus modificaciones, el Banco Central influye sobre las tasas de interés del sistema financiero y, en consecuencia, sobre las decisiones de consumo, ahorro e inversión de los agentes económicos, afectando la actividad económica y la inflación (Banco Central de Chile, s.f.).
 
En los últimos años la economía chilena ha enfrentado fluctuaciones importantes en inflación y actividad, lo que ha exigido ajustes significativos de la TPM. Este proyecto hace un seguimiento de la coyuntura macroeconómica chilena y proyecta la trayectoria de la TPM, combinando el monitoreo de sus principales determinantes con una regla de política monetaria estimada con datos chilenos.
 
## Objetivo y pregunta de investigación
 
**Variable objetivo:** TPM (Tasa de Política Monetaria).
 
**Pregunta que guía el trabajo:**
 
> ¿Cuál es la trayectoria esperada de la TPM en Chile durante los próximos 6 a 24 meses, según la evolución de sus principales determinantes macroeconómicos y una regla de política monetaria estimada con datos chilenos?
 
Para responderla, el proyecto:
 
1. Construye un monitor de coyuntura con las principales series macroeconómicas chilenas y externas.
2. Estima una regla de Taylor para Chile y contrasta la TPM que predice la regla con la TPM efectivamente observada.
3. Identifica los períodos en que la política monetaria se apartó de lo que la regla sugería y discute posibles razones económicas de esas desviaciones.
4. Proyecta la trayectoria esperada de la TPM a 6-24 meses.
## Metodología
 
### Regla de Taylor
 
Se estima una regla de Taylor basada en inflación del IPC, en la versión para economías pequeñas y abiertas de Galí y Monacelli (2005), aplicada a Chile por Caputo y Herrera (2013):
 
```
i_t = r̄ + φ_π^CPI · E_t(π_t+1) + φ_y^CPI · x_t
```
 
Donde:
- `i_t`: TPM (variable a explicar).
- `r̄`: tasa natural de interés real.
- `E_t(π_t+1)`: inflación esperada del IPC.
- `φ_π^CPI`, `φ_y^CPI`: coeficientes de respuesta de la TPM a la inflación esperada y a la brecha de actividad, respectivamente.
- `x_t`: brecha de actividad, construida aplicando el filtro de Hodrick y Prescott (1997) al Imacec, siguiendo la metodología de brecha de producto de Caputo y Herrera (2013).
Como referencia empírica, Caputo y Herrera (2013) estiman para un panel de economías emergentes con metas de inflación (donde Chile se encuadra) una respuesta de largo plazo a la inflación esperada levemente superior a 1 (1,174) —consistente con el principio de Taylor—, una respuesta positiva y menor a la brecha de producto (0,656), una respuesta significativa al Fed Funds Rate (1,2 en el largo plazo) y un componente inercial alto en la tasa (≈21,7 %). En la misma línea, Apablaza y Ortiz (2024), con datos chilenos hasta enero de 2024, confirman que la inercia es el componente que más incide en la evolución de la TPM y que cada punto porcentual de desviación en las expectativas de inflación a 11 meses genera un ajuste de 27 puntos base en la tasa.
 
### Canales de transmisión
 
Más allá de la regla como ecuación, el análisis busca entender los canales por los que los movimientos de la TPM se transmiten al resto de la economía (Banco Central de Chile, 2020):
 
- **Canal de tasas de interés de mercado:** la TPM se traspasa a las tasas de bancos comerciales (BCU, BCP, PDBC), afectando el crédito y las tasas de largo plazo.
- **Canal cambiario:** cambios en la tasa doméstica alteran las expectativas de tipo de cambio; cuando el peso se deprecia, suben los precios relativos de los bienes transables.
- **Canal de demanda:** modifica las decisiones de consumo e inversión y, con ello, el Imacec y el mercado laboral.
- **Canal de valorización de activos:** se transmite a través de los precios de bonos, acciones y viviendas.
- **Canal de expectativas:** descrito por el BCCh como "fundamental"; los anuncios de política monetaria anclan (o no) las expectativas de inflación (EEE, EOF), afectando la fijación de precios y salarios.
## Estructura del repositorio
 
```
Proyecto_Economia/
├── extraccion/     # scripts que descargan las series desde las APIs (BCCh y FRED)
├── base_datos/     # datos descargados y datos ya procesados
├── sql/            # esquema y consultas de la base de datos
├── notebooks/      # análisis exploratorio, estimación de la regla de Taylor y proyección
├── dashboard/       # visualización del monitor de coyuntura (Streamlit)
├── requirements.txt # dependencias de Python
└── README.md
```
 
## Datos
 
Se utilizan 13 series económicas, todas obtenibles de forma programática vía API. La fuente principal es la Base de Datos Estadísticos (BDE) del Banco Central de Chile, que provee acceso mediante el servicio SieteRestWS a series de política monetaria, precios, actividad, tipo de cambio, expectativas económicas, tasas de interés y mercado laboral. Como fuente complementaria para indicadores externos se usa la API de FRED (Federal Reserve Economic Data, Banco de la Reserva Federal de St. Louis).
 
La selección cubre la variable objetivo (TPM), sus determinantes según la regla de Taylor (brecha de inflación e IPC subyacente, brecha de actividad vía Imacec) y los indicadores de contexto (tipo de cambio, empleo, salarios, expectativas y entorno externo).
 
| # | Serie | Fuente | Frecuencia |
|---|---|---|---|
| 1 | TPM (Tasa de Política Monetaria) | BCCh — BDE | Diaria |
| 2 | IPC (Índice de Precios al Consumidor) | BCCh/INE — BDE | Mensual |
| 3 | IPC SAE (subyacente, sin alimentos ni energía) | BCCh/INE — BDE | Mensual |
| 4 | Imacec (Índice Mensual de Actividad Económica) | BCCh — BDE | Mensual |
| 5 | Tipo de cambio nominal (dólar observado) | BCCh — BDE | Diaria/Mensual |
| 6 | Expectativas de inflación (EEE) | BCCh — BDE | Mensual |
| 7 | Expectativas de inflación (EOF) | BCCh — BDE | Quincenal |
| 8 | Tasas de interés BCU / BCP / PDBC | BCCh — BDE | Diaria/Mensual |
| 9 | Tasa de desempleo nacional | BCCh/INE — BDE (ENE) | Mensual |
| 10 | Salarios nominales (Índice de Remuneraciones) | BCCh/INE — BDE | Mensual |
| 11 | Precio del cobre | FRED (IMF, "Global price of copper") | Mensual |
| 12 | Fed Funds Rate | FRED | Diaria/Mensual |
| 13 | Índice de precios/actividad de EE. UU. | FRED | Mensual |
 
## Cómo reproducir el análisis
 
Se necesita Python 3.10 o superior, una cuenta gratuita en la BDE del Banco Central (https://si3.bcentral.cl/Siete/) y una API key gratuita de FRED (https://fred.stlouisfed.org/docs/api/api_key.html).
 
1. Clonar el repositorio e instalar las dependencias:
```bash
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
 
Este archivo no se sube al repositorio; está incluido en el `.gitignore`.
 
3. Descargar las series y armar la base de datos:
```bash
python extraccion/descarga_bcch.py
python extraccion/descarga_fred.py
python extraccion/construir_base.py
```
 
4. Correr los notebooks de `notebooks/` en orden (exploración → construcción de la brecha de actividad con el filtro HP → estimación de la regla de Taylor → proyección).
5. Levantar el dashboard del monitor de coyuntura:
```bash
streamlit run dashboard/app.py
```
 
## Hitos del proyecto
 
| Hito | Fecha | Entregable |
|---|---|---|
| Hito 1: Propuesta | Semana 4 | Documento breve (2 páginas) con la variable objetivo asignada, la pregunta de proyección, las series y fuentes tentativas, los mecanismos económicos que se explorarán y el enlace al repositorio de GitHub ya creado. **Entregado** (ver `Entregable 1 - Ciencia de datos para la economía.pdf`). |
 
## Referencias
 
- Apablaza, V., & Ortiz, J. (2024). *Determinantes de la tasa de política monetaria en Chile*. Documento de Trabajo N°30. Observatorio del Contexto Económico, Universidad Diego Portales. https://ocec.udp.cl/cms/wp-content/uploads/2024/03/DT30.pdf
- Banco Central de Chile. (s.f.). *Política monetaria*. https://www.bcentral.cl
- Banco Central de Chile. (2020). *La política monetaria del Banco Central de Chile en el marco de metas de inflación*. Santiago: Banco Central de Chile. https://www.bcentral.cl/documents/33528/133301/PoliticaMonetariaBcchMarcoMetasInflacion2020.pdf
- Caputo, R., & Herrera, L. O. (2013). *Efficient CPI-based Taylor rules in small open economies*. Documento de Trabajo N°694. Banco Central de Chile.
- Galí, J., & Monacelli, T. (2005). Monetary policy and exchange rate volatility in a small open economy. *The Review of Economic Studies*, 72(3), 707–734.
- Hodrick, R. J., & Prescott, E. C. (1997). Postwar U.S. business cycles: An empirical investigation. *Journal of Money, Credit and Banking*, 29(1), 1–16.
