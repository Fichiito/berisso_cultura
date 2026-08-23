import requests

url = "https://berissociudad.com.ar/seccion.php?s=2&ss=5&t=Cultura"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(url, headers=headers)
response.encoding = "utf-8"

with open("pagina_cultura.html", "w", encoding="utf-8") as f:
    f.write(response.text)

print("Guardado. Tamaño:", len(response.text), "caracteres")