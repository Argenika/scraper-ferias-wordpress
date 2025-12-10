from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
from datetime import datetime
import time

# -----------------------------
# CONFIGURACIÓN
# -----------------------------
BASE_DOMAIN = "https://www.nferias.com"
BASE_URL = "https://www.nferias.com/espana/"
EXPORT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Exports")
os.makedirs(EXPORT_FOLDER, exist_ok=True)

csv_historico = os.path.join(EXPORT_FOLDER, "ferias_todas.csv")
csv_ultimo = os.path.join(EXPORT_FOLDER, "ultimo.csv")

HOY = datetime.today()

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
}


def convertir_fecha_a_timestamp(fecha_texto):
    """
    Convierte un texto de fecha en timestamp a las 9:00.
    Soporta:
      - '4 de diciembre 2025'
      - '18/11/2025'
      - 'Del 18 al 20 noviembre 2025' -> toma el primer día
    Devuelve None si no se puede convertir.
    """
    if not fecha_texto:
        return None
    fecha_texto = fecha_texto.lower().strip()

    # 1) Formato dd de mes yyyy
    partes = fecha_texto.split(" de ")
    if len(partes) == 3:
        try:
            dia = int(partes[0])
            mes = MESES.get(partes[1].strip())
            ano = int(partes[2])
            if mes:
                dt = datetime(ano, mes, dia, 9, 0)
                return int(dt.timestamp())
        except:
            pass

    # 2) Formato dd/mm/yyyy
    m = re.search(r"(\d{1,2})/(\d{1,2})/(20\d{2})", fecha_texto)
    if m:
        try:
            dia, mes, ano = int(m.group(1)), int(m.group(2)), int(m.group(3))
            dt = datetime(ano, mes, dia, 9, 0)
            return int(dt.timestamp())
        except:
            pass

    # 3) Rango tipo 'Del 18 al 20 noviembre 2025' -> tomar primer día
    m = re.search(r"(\d{1,2})", fecha_texto)
    if m:
        try:
            dia = int(m.group(1))
            for mes_nombre in MESES:
                if mes_nombre in fecha_texto:
                    mes = MESES[mes_nombre]
                    ano_match = re.search(r"(20\d{2})", fecha_texto)
                    if ano_match:
                        ano = int(ano_match.group(1))
                        dt = datetime(ano, mes, dia, 9, 0)
                        return int(dt.timestamp())
        except:
            pass

    # Si no se pudo determinar la fecha de inicio, devolvemos None
    return None


def parsear_fecha_inicio(texto):
    ano_match = re.search(r"(20\d{2})", texto)
    if not ano_match:
        return ""
    ano = int(ano_match.group(1))
    mes = None
    for m in MESES:
        if m in texto.lower():
            mes = MESES[m]
            mes_nombre = m
            break
    if not mes:
        return ""
    dias = re.findall(r"\b(\d{1,2})\b", texto)
    if not dias:
        return ""
    dia_inicio = int(dias[0])
    return f"{dia_inicio} de {mes_nombre} {ano}"

def extraer_fecha_fin(texto):
    """
    Detecta y devuelve un datetime de la fecha de fin si aparece en 'texto',
    soporta formatos como:
      - 'Del 18 al 20 noviembre 2025'
      - '18 - 20 noviembre 2025'
      - '18/11/2025 – 20/11/2025'
      - 'Finaliza: 20/11/2025'
    Devuelve None si no encuentra fecha de fin.
    """
    if not texto:
        return None
    texto = texto.lower()

    # 1) Rango con día - día mes año (ej. 'del 18 al 20 noviembre 2025' o '18 - 20 noviembre 2025')
    m = re.search(r"(\d{1,2})\D+(\d{1,2})\s+([a-záéíóú]+)\s+(20\d{2})", texto)
    if m:
        try:
            dia_fin = int(m.group(2))
            mes_nombre = m.group(3)
            ano = int(m.group(4))
            if mes_nombre in MESES:
                return datetime(ano, MESES[mes_nombre], dia_fin)
        except:
            pass

    # 2) Buscar fechas en formato dd/mm/yyyy y tomar la última como fecha de fin
    matches = re.findall(r"(\d{1,2}/\d{1,2}/\d{4})", texto)
    if matches:
        try:
            return datetime.strptime(matches[-1], "%d/%m/%Y")
        except:
            pass

    # 3) Otros formatos con 'finaliza' y dd/mm/yyyy (already covered by regex above),
    #    si se necesita más formatos se pueden añadir aquí.
    return None


# -----------------------------
# CONFIGURAR SELENIUM
# -----------------------------
options = Options()
options.add_argument("--headless")  # Ejecutar sin abrir ventana
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-extensions")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--blink-settings=imagesEnabled=false")  # No cargar imágenes


driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# -----------------------------
# SCRAPING LISTA DE FERIAS
# -----------------------------
urls_por_visitar = [BASE_URL]
visitadas = set()
all_eventos = []

pagina_actual = 1
MAX_PAGINAS = 21

while urls_por_visitar:
    url = urls_por_visitar.pop(0)
    if url in visitadas:
        continue
    visitadas.add(url)

    print(f"Scrapeando: {url}")
    driver.get(url)

    # Esperar que cargue la lista de ferias
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.card-body"))
    )

    soup = BeautifulSoup(driver.page_source, "html.parser")
    eventos_divs = soup.find_all("div", class_="card-body")
    print("Número de ferias en esta página:", len(eventos_divs))

    # -----------------------------
    # RECORRER CADA FERIA
    # -----------------------------
    for div in eventos_divs:
        nombre_tag = div.find("a", class_="text-dark medium font-l mb-1")
        if not nombre_tag:
            continue

        nombre = nombre_tag.get_text(strip=True)
        enlace_rel = nombre_tag["href"]
        enlace_evento = enlace_rel if enlace_rel.startswith("http") else BASE_DOMAIN + enlace_rel

        fecha_div = div.find("div", class_="mb-1")
        fecha_raw = fecha_div.get_text(" ", strip=True) if fecha_div else ""
        fecha = parsear_fecha_inicio(fecha_raw)

        # Abrir la página de la feria
        driver.get(enlace_evento)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "article"))
        )
        soup_evento = BeautifulSoup(driver.page_source, "html.parser")

        # --- Ciudad, enlace oficial, keywords ---
        lis = soup_evento.find_all("li")
        li_dict = {li.get_text(strip=True).split(":")[0]: li for li in lis}
        ciudad = li_dict.get("Ciudad", "").find("a").get_text(strip=True) if li_dict.get("Ciudad") else ""
        li_info = li_dict.get("Más info.", None)
        enlace_oficial = li_info.find("a")["href"].strip() if li_info and li_info.find("a") else ""
        li_sectores = next((li for li in lis if "Sectores" in li.get_text()), None)
        keywords = ", ".join([a.get_text(strip=True) for a in li_sectores.find_all("a")]) if li_sectores else ""

        # --- Descripción limpia ---
        articulo = soup_evento.find("article", class_="mb-4")
        descripcion = ""
        titulo_articulo = ""
        if articulo:
            h_title = articulo.find("p", class_="h2 nTitle")
            if h_title:
                titulo_articulo = h_title.get_text(" ", strip=True)
            header = articulo.find("header")
            if header:
                header.extract()
            for junk in articulo.select("[class*=google], .google-anno-skip, script, style, iframe"):
                junk.extract()
            descripcion = articulo.get_text(" ", strip=True)
            if titulo_articulo and descripcion.lower().startswith(titulo_articulo.lower()):
                descripcion = descripcion[len(titulo_articulo):].lstrip(" -:—\n\r\t ").strip()

        # --- Fecha de fin solo para filtrar ---
        fecha_fin = None
        for li in lis:
            ff = extraer_fecha_fin(li.get_text(" ", strip=True))
            if ff:
                fecha_fin = ff
                break
        if fecha_fin is None and articulo:
            fecha_fin = extraer_fecha_fin(articulo.get_text(" ", strip=True))

        # --- Guardar solo ferias actuales ---
        if fecha_fin is None or fecha_fin >= datetime.today():
            all_eventos.append([nombre, fecha, ciudad, enlace_oficial, keywords, descripcion])

    # -----------------------------
    # PAGINACIÓN
    # -----------------------------
    if pagina_actual >= MAX_PAGINAS:
        break

    next_link = soup.find("a", rel="next")
    if next_link and next_link.get("href"):
        href = next_link["href"]
        if not href.startswith("http"):
            href = BASE_DOMAIN + href
        urls_por_visitar.append(href)
        pagina_actual += 1
    else:
        break

# -----------------------------
# CERRAR DRIVER UNA VEZ TERMINADO
# -----------------------------
driver.quit()

# -----------------------------
# GUARDAR CSVs
# -----------------------------

# Añadir timestamps a cada fila de all_eventos
for i, evento in enumerate(all_eventos):
    fecha_texto = evento[1]  # columna "Fecha"
    timestamp = convertir_fecha_a_timestamp(fecha_texto)
    evento.append(timestamp)  # añadimos solo un timestamp



df_nuevos = pd.DataFrame(all_eventos, columns=[
    "Nombre", "Fecha", "Ciudad", "Enlace_oficial", "Keywords", "Descripcion", "timestamp"
])

# Guardar CSVs
df_nuevos.to_csv(csv_ultimo, index=False, encoding="utf-8")
df_nuevos.to_csv(csv_historico, index=False, encoding="utf-8")

print("\n=== RESULTADO FINAL ===")
print("Eventos totales encontrados:", len(df_nuevos))
print("CSV guardado en:", csv_ultimo)
