##esto es para que compartan

import os
import hashlib
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

IMAGENES_DIR = os.path.join("frontend", "img", "eventos")
os.makedirs(IMAGENES_DIR, exist_ok=True)


def descargar_imagen(url_imagen, titulo, base_url=""):
    """
    Descarga una imagen desde una URL y la guarda en frontend/img/eventos/.
    Devuelve la ruta relativa para usar en el frontend, o None si falla.
    """
    if not url_imagen:
        return None
    try:
        if url_imagen.startswith("/"):
            url_imagen = base_url + url_imagen
        resp = requests.get(url_imagen, headers=headers, timeout=10)
        resp.raise_for_status()
        ext = os.path.splitext(url_imagen.split("?")[0])[1] or ".jpg"
        nombre_hash = hashlib.md5(url_imagen.encode()).hexdigest()[:12]
        nombre_archivo = f"{nombre_hash}{ext}"
        ruta = os.path.join(IMAGENES_DIR, nombre_archivo)
        with open(ruta, "wb") as f:
            f.write(resp.content)
        return os.path.join("img", "eventos", nombre_archivo).replace("\\", "/")
    except Exception as e:
        print(f"Error descargando imagen: {e}")
        return None