from datetime import date
from extractor_ia.cliente_ia import extraer_evento

texto_prueba = """
El próximo viernes 11 de septiembre a las 21:00, en el Cine Teatro Victoria de Berisso,
se presentará el humorista Fede Cyrulnik con su nuevo show. Las entradas cuestan desde $35.000.
"""

resultado = extraer_evento(texto_prueba, date.today().isoformat())
print(resultado)