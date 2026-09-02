from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="frontend", static_url_path="")
CORS(app)


@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

def get_conexion():
    return psycopg2.connect(
        host="localhost",
        port="5432",
        database="berisso_cultura",
        user="postgres",
        password=os.getenv("DB_PASSWORD")
    )

@app.route("/api/eventos")
def eventos():
    conexion = get_conexion()
    cursor = conexion.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("""
         SELECT id, titulo, descripcion, fecha_hora, lugar, categoria, precio, link_fuente, imagen_url
        FROM eventos
        ORDER BY fecha_hora ASC
    """)
    filas = cursor.fetchall()
    cursor.close()
    conexion.close()

    # Convertir fecha_hora a texto para que se pueda enviar como JSON
    eventos = []
    for fila in filas:
        evento = dict(fila)
        if evento["fecha_hora"]:
            evento["fecha_hora"] = evento["fecha_hora"].isoformat()
        eventos.append(evento)

    return jsonify(eventos)

if __name__ == "__main__":
    app.run(debug=True, port=5000)