#  Scraper de Ferias para WordPress

Proyecto desarrollado durante las prácticas profesionales en **Andreoli Studio** (Valencia).
Automatiza la recolección, procesamiento y publicación de ferias sectoriales en WordPress.

> Código privado por acuerdo con la empresa. Este README documenta la arquitectura y resultados del proyecto.

---

## Objetivo

Automatizar completamente el proceso de obtención y publicación de ferias, eliminando trabajo manual diario y evitando duplicados en la base de datos.

---

## Flujo del proyecto
1. **Scraper Python** — extrae ferias de la web con Selenium + BeautifulSoup
2. **Procesamiento** — limpieza y estructuración de datos con Pandas → genera CSV
3. **Subida FTP** — envía el CSV automáticamente al servidor
4. **WordPress** — snippet PHP importa el CSV sin duplicar entradas existentes
5. **Notificación** — informa del número de ferias nuevas creadas cada ejecución

---

## Tecnologías

| Tecnología | Uso |
|---|---|
| Python 3 | Lenguaje principal |
| Selenium | Navegación y extracción web dinámica |
| BeautifulSoup | Parseo HTML |
| Pandas | Procesamiento y limpieza de datos |
| FTP (ftplib) | Transferencia automática de archivos |
| PHP | Snippet de importación en WordPress |
| WordPress Cron | Automatización de la importación diaria |

---

##  Estructura del proyecto
---

##  Instrucciones de uso

1. Clona el repositorio
2. Instala dependencias:
```bash
pip install -r requirements.txt
```
3. Crea tu archivo de configuración:
```bash
cp config_example.py config.py
# Edita config.py con tus credenciales FTP
```
4. Ejecuta el scraper:
```bash
python scraper/scraper_nferias.py
```

---

##  Desarrollado por

**Angelina Lepeshko** — [github.com/Argenika](https://github.com/Argenika) · [LinkedIn](https://www.linkedin.com/in/angelina-lepeshko-b9a410329/)
