import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

conexion = psycopg2.connect(
    host="localhost",
    port="5432",
    database="berisso_cultura",
    user="postgres",
    password=os.getenv("DB_PASSWORD")
)

print("Conexión exitosa!")
conexion.close()