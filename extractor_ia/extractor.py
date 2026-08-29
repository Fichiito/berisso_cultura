import requests
from bs4 import BeautifulSoup
from datetime import date, datetime
import psycopg2
import os
from dotenv import load_dotenv
import time

from extractor_ia.fuentes import FUENTES
from extractor_ia.cliente_ia import extraer_evento
from utilidades import descargar_imagen

load_dotenv()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}


def obtener_base(url):
    return "/".join(url.split("/")[:3])


def procesar_fuente_listado(fuente):
    """Fuentes tipo 'listado_noticias': hay que entrar a cada noticia a buscar el texto."""
    base = obtener_base(fuente["url"])
    response = requests.get(fuente["url"], headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")

    items = []
    for a in soup.select(fuente["selector_link"]):
        href = a.get("href")
        if not href:
            continue
        if href.startswith("/"):
            href = base + href

        imagen_url = None
        bloque_fila = a.find_parent("div", class_="row")
        if bloque_fila:
            img_tag = bloque_fila.find("img")
            if img_tag and img_tag.get("data-src"):
                imagen_url = img_tag["data-src"]
            elif img_tag and img_tag.get("src") and "blankphoto" not in img_tag["src"]:
                imagen_url = img_tag["src"]
            if imagen_url and imagen_url.startswith("/"):
                imagen_url = base + imagen_url

        try:
            resp_noticia = requests.get(href, headers=headers, timeout=15)
            soup_noticia = BeautifulSoup(resp_noticia.text, "html.parser")
            texto = soup_noticia.get_text(" ", strip=True)
        except Exception as e:
            print(f"  Error leyendo {href}: {e}")
            continue

        items.append({
            "texto": texto,
            "link": href,
            "imagen_url": imagen_url,
            "imagen_base": base,
        })

    return items


def procesar_fuente_cartelera(fuente):
    """Fuentes tipo 'cartelera': cada item ya trae su texto completo en la misma página."""
    base = obtener_base(fuente["url"])
    response = requests.get(fuente["url"], headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")

    items = []
    for card in soup.select(fuente["selector_item"]):
        texto = card.get_text(" ", strip=True)
        if fuente.get("lugar_fijo"):
            texto += f" Lugar: {fuente['lugar_fijo']}."

        imagen_tag = card.select_one(fuente["selector_imagen"]) if fuente.get("selector_imagen") else None
        imagen_url = imagen_tag["src"] if imagen_tag and imagen_tag.get("src") else None

        items.append({
            "texto": texto,
            "link": fuente["url"],
            "imagen_url": imagen_url,
            "imagen_base": base,
        })

    return items


def guardar_evento(datos, item):
    fecha_hora = None
    if datos.get("fecha"):
        try:
            hora_str = datos.get("hora") or "00:00"
            fecha_hora = datetime.strptime(
                f"{datos['fecha']} {hora_str}", "%Y-%m-%d %H:%M"
            )
        except ValueError:
            print(f"  Fecha/hora inválida: {datos.get('fecha')} {datos.get('hora')}")
            return

    imagen_local = None
    if item.get("imagen_url"):
        imagen_local = descargar_imagen(item["imagen_url"], datos["titulo"], base_url=item.get("imagen_base", ""))

    conexion = psycopg2.connect(
        host="localhost",
        port="5432",
        database="berisso_cultura",
        user="postgres",
        password=os.getenv("DB_PASSWORD")
    )
    cursor = conexion.cursor()

    cursor.execute("""
        INSERT INTO eventos (titulo, fecha_hora, lugar, categoria, precio, link_fuente, descripcion, imagen_url, aprobado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, false)
        ON CONFLICT (titulo, fecha_hora, lugar)
        DO UPDATE SET
            precio = EXCLUDED.precio,
            imagen_url = COALESCE(EXCLUDED.imagen_url, eventos.imagen_url),
            actualizado_en = NOW()
    """, (
        datos["titulo"],
        fecha_hora,
        datos.get("lugar"),
        datos.get("categoria", "Otro"),
        datos.get("precio"),
        item["link"],
        datos.get("descripcion_corta"),
        imagen_local,
    ))

    conexion.commit()
    cursor.close()
    conexion.close()


def ejecutar():
    fecha_hoy = date.today().isoformat()
    total_encontrados = 0

    for fuente in FUENTES:
        print(f"\nRevisando fuente ({fuente['tipo']}): {fuente['url']}")
        try:
            if fuente["tipo"] == "listado_noticias":
                items = procesar_fuente_listado(fuente)
            elif fuente["tipo"] == "cartelera":
                items = procesar_fuente_cartelera(fuente)
            else:
                print(f"  Tipo de fuente desconocido: {fuente['tipo']}")
                continue
        except Exception as e:
            print(f"Error accediendo a {fuente['url']}: {e}")
            continue

        print(f"  {len(items)} items encontrados")

        for item in items:
            resultado = extraer_evento(item["texto"], fecha_hoy)
            time.sleep(4)

            if resultado:
                print(f"  ✓ Evento encontrado: {resultado['titulo']} ({resultado['fecha']})")
                guardar_evento(resultado, item)
                total_encontrados += 1
            else:
                print(f"  · No es evento (o no se pudo interpretar)")

    print(f"\nTotal eventos nuevos/actualizados: {total_encontrados}")


if __name__ == "__main__":
    ejecutar()