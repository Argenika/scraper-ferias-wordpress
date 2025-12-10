import os

# Carpeta base del proyecto
BASE = r"C:\Users\hello\Desktop\TRABAJOS\ANGELA\Scraper_nferias"

# Ruta al ejecutable de Python del entorno virtual
PYTHON = rf"{BASE}\venv\Scripts\python.exe"

# 1️⃣ Ejecutar scraper que genera los CSV
os.system(rf'{PYTHON} "{BASE}\scraper\scraper_nferias.py"')

# 2️⃣ Subir CSV al servidor FTP
os.system(rf'{PYTHON} "{BASE}\ftp\subir_cvs_ftp.py"')

# 3️⃣ Subir los eventos directamente a WordPress
# os.system(rf'{PYTHON} "{BASE}\wordpress\scraper_wordpress.py"')# comentada porque ya no se usa
