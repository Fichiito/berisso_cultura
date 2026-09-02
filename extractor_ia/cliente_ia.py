import json
from google import genai
from extractor_ia.config import AI_API_KEY, AI_MODEL

cliente = genai.Client(api_key=AI_API_KEY)

PROMPT_EXTRAER = """Sos un asistente que analiza textos de noticias/artículos culturales de Berisso, Argentina, y determina cuáles describen un EVENTO CONCRETO Y PRÓXIMO (con fecha específica, no una fiesta genérica sin fecha ni una nota vieja).

Hoy es {fecha_hoy}.

Para cada texto, determiná si es un evento concreto y futuro. Si no lo es (sin fecha, fecha pasada, nota genérica), el elemento del array debe ser: {{"es_evento": false}}

Si SÍ es un evento concreto y futuro, el elemento debe ser:
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

Respondé EXACTAMENTE con un array JSON con exactamente {cantidad} elementos, uno por cada texto, en el mismo orden. Sin texto extra, sin explicaciones.

Textos a analizar:
{textos}
"""


def extraer_eventos(items, fecha_hoy):
    """
    Le manda múltiples textos a la IA en una sola llamada y devuelve
    una lista de resultados (dict con evento o None por cada item).
    """
    if not items:
        return []

    textos_formateados = ""
    for i, item in enumerate(items):
        texto_corto = item["texto"][:2000]
        textos_formateados += f"\n--- TEXTO {i+1} ---\n{texto_corto}\n"

    prompt = PROMPT_EXTRAER.format(
        fecha_hoy=fecha_hoy,
        cantidad=len(items),
        textos=textos_formateados
    )

    try:
        respuesta = cliente.models.generate_content(
            model=AI_MODEL,
            contents=prompt
        )
        texto_respuesta = respuesta.text.strip()
        texto_respuesta = texto_respuesta.replace("```json", "").replace("```", "").strip()

        resultados = json.loads(texto_respuesta)

        if not isinstance(resultados, list):
            print("La IA no devolvió un array:", str(resultados)[:200])
            return [None] * len(items)

        if len(resultados) != len(items):
            print(f"WARNING: Se esperaban {len(items)} resultados, se obtuvieron {len(resultados)}")
            while len(resultados) < len(items):
                resultados.append(None)

        eventos = []
        for resultado in resultados:
            if isinstance(resultado, dict) and resultado.get("es_evento"):
                eventos.append(resultado)
            else:
                eventos.append(None)

        return eventos

    except json.JSONDecodeError:
        print("La IA no devolvió un JSON válido:", texto_respuesta[:200])
        return [None] * len(items)
    except Exception as e:
        print(f"Error consultando la IA: {e}")
        return [None] * len(items)