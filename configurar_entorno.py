"""
Configura el proyecto en un solo paso (Mac, Linux y Windows):

    1. Crea el entorno virtual .venv (si no existe).
    2. Instala las dependencias de requirements.txt dentro de ese entorno.
    3. Crea el archivo .env a partir de .env.example (si no existe).

Uso, desde la carpeta raíz del proyecto:
    Mac / Linux:  python3 configurar_entorno.py
    Windows:      python configurar_entorno.py

Solo usa la librería estándar de Python, así que funciona antes de instalar nada.
"""

import shutil
import subprocess
import sys
import venv
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CARPETA_VENV = RAIZ / ".venv"
REQUIREMENTS = RAIZ / "requirements.txt"
ENV = RAIZ / ".env"
ENV_EJEMPLO = RAIZ / ".env.example"
ES_WINDOWS = sys.platform.startswith("win")


def python_del_venv():
    """Ruta al ejecutable de Python dentro de .venv (cambia según el sistema operativo)."""
    if ES_WINDOWS:
        return CARPETA_VENV / "Scripts" / "python.exe"
    return CARPETA_VENV / "bin" / "python"


def crear_entorno():
    if python_del_venv().exists():
        print("[1/3] El entorno virtual .venv ya existe, se reutiliza.")
        return
    print("[1/3] Creando entorno virtual .venv ...")
    venv.create(CARPETA_VENV, with_pip=True)


def instalar_dependencias():
    print("[2/3] Instalando dependencias de requirements.txt ...")
    py = str(python_del_venv())
    # Se llama al pip del entorno virtual directamente: no hace falta activarlo.
    subprocess.run([py, "-m", "pip", "install", "--upgrade", "pip", "--quiet"], check=True)
    subprocess.run([py, "-m", "pip", "install", "-r", str(REQUIREMENTS), "--quiet"], check=True)


def preparar_env():
    if ENV.exists():
        print("[3/3] El archivo .env ya existe, no se modifica.")
        return False
    if not ENV_EJEMPLO.exists():
        print("[3/3] AVISO: no se encontró .env.example en la raíz del proyecto.")
        return False
    shutil.copy(ENV_EJEMPLO, ENV)
    print("[3/3] Se creó .env a partir de .env.example.")
    return True


def main():
    if sys.version_info < (3, 9):
        sys.exit("Se requiere Python 3.9 o superior.")

    crear_entorno()
    instalar_dependencias()
    env_nuevo = preparar_env()

    activar = ".venv\\Scripts\\activate" if ES_WINDOWS else "source .venv/bin/activate"
    print("\nListo. Próximos pasos:")
    if env_nuevo:
        print("  - Abre el archivo .env y escribe tu usuario y clave de la BDE del Banco Central.")
    print("  - En VS Code: Select Interpreter → .venv (la terminal se activará sola)")
    print(f"  - Fuera de VS Code:       {activar}")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError:
        sys.exit("\nERROR: falló la instalación de dependencias. Revisa tu conexión a internet "
                 "y que requirements.txt esté en la raíz del proyecto.")