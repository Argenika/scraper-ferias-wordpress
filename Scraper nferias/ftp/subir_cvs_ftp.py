from ftplib import FTP 
# -----------------------------
# CONFIGURACIÓN FTP
# -----------------------------
# config_example.py
FTP_USER = "usuario_ejemplo"
FTP_PASS = "contraseña_ejemplo"
FTP_HOST = "ftp.ejemplo.com"

# Archivo local que queremos subir
import os

EXPORT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Exports")
LOCAL_FILE = os.path.join(EXPORT_FOLDER, "ultimo.csv")

# Carpeta y nombre en el servidor
REMOTE_FILE = "/csv/ultimo.csv"  # <-- crea esta carpeta en tu servidor vía FileZilla

# -----------------------------
# SUBIR CSV
# -----------------------------
try:
    ftp = FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    print("Conexión FTP exitosa.")

    with open(LOCAL_FILE, "rb") as f:
        ftp.storbinary(f"STOR {REMOTE_FILE}", f)

    ftp.quit()
    print(f"Archivo subido correctamente a FTP como: {REMOTE_FILE}")

except Exception as e:
    print("Error subiendo archivo FTP:", e)

