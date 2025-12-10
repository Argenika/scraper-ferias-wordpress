@echo off
REM Entrar en la carpeta principal
cd C:\Users\hello\Desktop\TRABAJOS\ANGELA\Scraper_nferias

REM Activar el entorno virtual
call venv\Scripts\activate.bat

REM Ejecutar el scraper
python scraper\scraper_nferias.py

REM Subir CSV al FTP
python ftp\subir_cvs_ftp.py

REM (Opcional) Subir a WordPress
python wordpress\scraper_wordpress.py

pause
