import requests
from bs4 import BeautifulSoup
import re
import psycopg2
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

url = "https://teatrocerca.com.ar/sala/cine-teatro-victoria"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

meses = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
}

def convertir_fecha(fecha_str, hora_str=None):
    if not fecha_str:
        return None
    match = re.search(r"(\d{1,2}) de (\w+)", fecha_str.lower())
    if not match:
        return None
    dia = int(match.group(1))
    mes = meses.get(match.group(2))
    if not mes:
        return None
    anio = 2026
    hora, minuto = 0, 0
    if hora_str:
        try:
            hora, minuto = map(int, hora_str.split(":"))
        except:
            pass
    return datetime(anio, mes, dia, hora, minuto)

# --- Scraping ---
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

eventos = []
obras = soup.select("h3")
for obra in obras:
    titulo = obra.get_text(strip=True)
    bloque = obra.find_parent()
    texto_completo = bloque.get_text(" ", strip=True) if bloque else ""

    fecha_match = re.search(r"(\d{1,2} de \w+)", texto_completo)
    fecha = fecha_match.group(1) if fecha_match else None

    hora_match = re.search(r"(\d{1,2}:\d{2})", texto_completo)
    hora = hora_match.group(1) if hora_match else None

    precio_match = re.search(r"Desde \$ ?([\d.]+)", texto_completo)
    precio = f"Desde ${precio_match.group(1)}" if precio_match else None

    imagen_tag = bloque.find("img") if bloque else None
    print(imagen_tag)
    imagen_url = imagen_tag["src"] if imagen_tag and imagen_tag.get("src") else None

    fecha_hora = convertir_fecha(fecha, hora)

    eventos.append({
        "titulo": titulo,
        "fecha_hora": fecha_hora,
        "lugar": "Cine Teatro Victoria",
        "categoria": "Teatro",
        "precio": precio,
        "link_fuente": url,
        "imagen_url": imagen_url,
    })

conexion = psycopg2.connect(
    host="localhost",
    port="5432",
    database="berisso_cultura",
    user="postgres",
    password=os.getenv("DB_PASSWORD")
)
cursor = conexion.cursor()

insertados = 0

for e in eventos:
    cursor.execute("""
         INSERT INTO eventos (titulo, fecha_hora, lugar, categoria, precio, link_fuente, imagen_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (titulo, fecha_hora, lugar)
        DO UPDATE SET
            precio = EXCLUDED.precio,
            actualizado_en = NOW()
    """, (e["titulo"], e["fecha_hora"], e["lugar"], e["categoria"], e["precio"], e["link_fuente"], e["imagen_url"]))
    insertados += 1

conexion.commit()
cursor.close()
conexion.close()

print(f"Se procesaron {insertados} eventos")