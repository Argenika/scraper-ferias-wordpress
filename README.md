# Scraper de ferias para WordPress

Este proyecto automatiza la recolección de información de ferias desde la web `nferias.com` y su publicación en WordPress.

## Objetivo

- Obtener ferias automáticamente desde la web.
- Generar CSV con la información.
- Subir CSV al servidor FTP.
- Importar ferias en WordPress sin duplicados.
- Notificar cuántas ferias nuevas se crearon cada día.

## Flujo del proyecto

1. **Scraper Python** (`scraper/scraper_nferias.py`) → obtiene ferias y genera CSV.
2. **Subida FTP** (`ftp/subir_cvs_ftp.py`) → envía el CSV al servidor.
3. **WordPress** → importa el CSV sin duplicar ferias existentes (snippet PHP).
4. **Notificación** → se puede enviar un mensaje indicando si se crearon ferias nuevas.

## Tecnologías

- Python 3
- Selenium
- BeautifulSoup
- Pandas
- FTP
- WordPress (snippets y cron)

## Instrucciones de uso

1. Crear un archivo `config.py` basado en `config_example.py` con tus credenciales de FTP.
2. Ejecutar el scraper:
   ```bash
   python scraper/scraper_nferias.py
