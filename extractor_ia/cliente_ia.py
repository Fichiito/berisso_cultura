import json
from google import genai
from extractor_ia.config import AI_API_KEY, AI_MODEL

cliente = genai.Client(api_key=AI_API_KEY)

PROMPT_BASE = """Sos un asistente que analiza texto de noticias/artículos culturales de Berisso, Argentina, y determina si describen un EVENTO CONCRETO Y PRÓXIMO (con fecha específica, no una fiesta genérica sin fecha ni una nota vieja).

Hoy es {fecha_hoy}. Si el texto no tiene fecha, o la fecha ya pasó, o es una nota genérica sin evento concreto, respondé:
{{"es_evento": false}}

Si SÍ es un evento concreto y futuro, respondé EXACTAMENTE en este formato JSON (sin texto extra, sin explicaciones):
{{
  "es_evento": true,
  "titulo": "...",
  "fecha": "YYYY-MM-DD",
  "hora": "HH:MM o null si no se menciona",
  "lugar": "...",
  "categoria": "una palabra: Teatro, Música, Fiestas, u Otro",
  "precio": "texto tal cual aparece, o null si no se menciona",
  "descripcion_corta": "máximo 20 palabras"
}}

Texto a analizar:
\"\"\"
{texto}
\"\"\"
"""

def extraer_evento(texto, fecha_hoy):
    """
    Le manda el texto a Gemini y devuelve un dict con el evento,
    o None si no es un evento o hubo algún error.
    """
    prompt = PROMPT_BASE.format(texto=texto[:4000], fecha_hoy=fecha_hoy)

    try:
        respuesta = cliente.models.generate_content(
            model=AI_MODEL,
            contents=prompt
        )
        texto_respuesta = respuesta.text.strip()
        texto_respuesta = texto_respuesta.replace("```json", "").replace("```", "").strip()

        datos = json.loads(texto_respuesta)

        if not datos.get("es_evento"):
            return None

        return datos

    except json.JSONDecodeError:
        print("La IA no devolvió un JSON válido:", texto_respuesta[:200])
        return None
    except Exception as e:
        print(f"Error consultando la IA: {e}")
        return None