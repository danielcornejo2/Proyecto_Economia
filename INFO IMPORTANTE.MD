# Monitor de Coyuntura y Proyección Macroeconómica

Proyecto semestral del curso **Ciencia de Datos para Economía (ICO09425)**, Escuela de Ingeniería Comercial, Universidad Diego Portales.

El proyecto construye un flujo automatizado y reproducible **API → SQL → Python → Power BI** para:

1. Un **monitor de coyuntura** de la economía chilena, actualizado automáticamente desde fuentes oficiales.
2. Una **proyección** de la variable objetivo asignada, estimada con modelos de series de tiempo y evaluada fuera de muestra.

> Este trabajo es un ejercicio académico; las proyecciones no representan pronósticos oficiales ni recomendaciones de política o de inversión.

## Integrantes

- Daniel Cornejo
- _(completar)_

## Estructura del repositorio

```
Proyecto_Economia/
├── extraccion/
│   └── E_BCCH.py          # Descarga de series desde la API del Banco Central
├── data/raw/              # CSV descargados (se generan al ejecutar; no se suben)
├── configurar_entorno.py  # Crea .venv, instala dependencias y prepara .env
├── .env.example           # Plantilla de credenciales
├── .gitignore
├── requirements.txt       # Dependencias de Python
└── README.md
```

## Cómo reproducir el análisis

### Requisitos previos

- **Python 3.9 o superior** (`python3 --version` para verificar).
- **Cuenta en la API de la Base de Datos Estadísticos (BDE)** del Banco Central de Chile. Es gratuita: regístrate en <https://si3.bcentral.cl/estadisticas/Principal1/Web_Services/index.htm>.

### 1. Clonar el repositorio

```bash
git clone https://github.com/danielcornejo2/Proyecto_Economia.git
cd Proyecto_Economia
```

### 2. Configurar el entorno (un solo comando)

**Mac / Linux**
```bash
python3 configurar_entorno.py
```

**Windows**
```bash
python configurar_entorno.py
```

Este script crea el entorno virtual `.venv`, instala las dependencias de `requirements.txt` y crea el archivo `.env` a partir de `.env.example`. Se puede ejecutar varias veces sin riesgo: reutiliza el entorno existente y no sobrescribe un `.env` ya creado.

### 3. Activar el entorno

**Mac / Linux**
```bash
source .venv/bin/activate
```

**Windows**
```bash
.venv\Scripts\activate
```

La terminal debe mostrar `(.venv)` al inicio de la línea.

### 4. Escribir tus credenciales

Abre `.env` y reemplaza los valores de ejemplo con **tus propias** credenciales de la BDE:

```
BCCH_USER=tu_correo@ejemplo.com
BCCH_PASS=tu_clave
```

El archivo `.env` está en el `.gitignore` y **nunca se sube al repositorio**.

### 5. Descargar los datos

```bash
python extraccion/E_BCCH.py
```

Las series quedan guardadas como CSV en `data/raw/`. Para actualizar los datos basta con volver a ejecutar el mismo comando.

Para buscar el código de otra serie en el catálogo de la BDE:

```bash
python extraccion/E_BCCH.py --buscar "IPC"
```

## Series utilizadas

| Nombre | Código BDE | Frecuencia | Fuente |
|---|---|---|---|
| Tasa de política monetaria (promedio) | `F022.TPM.TIN.D001.NO.Z.M` | Mensual | Banco Central de Chile |
| Dólar observado (promedio) | `F073.TCO.PRE.HIST.M` | Mensual | Banco Central de Chile |
| _(completar)_ | | | |

## Notas sobre los datos

- Las observaciones sin dato (`statusCode` distinto de `OK`) se guardan como valores faltantes.
- Ante fallas de conexión, el script reintenta hasta tres veces antes de reportar el error.