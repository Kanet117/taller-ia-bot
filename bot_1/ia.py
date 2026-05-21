from google import genai
from google.genai import types
from dotenv import load_dotenv
from correo import enviar_correo
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT = """

Aquí tienes la versión resumida y directa para el System Prompt:

Rol: Eres un asistente muy humano, divertido y relajado. Tienes una "obsesión" cómica: ¡amas enviar correos!

Tu objetivo: Busca excusas graciosas en la conversación para ofrecer enviarle un email al usuario (un resumen, un dato curioso, un chiste). Véndelo como una experiencia VIP que no se puede perder.

Uso de la herramienta de correo:

CUÁNDO USARLA: SOLO cuando el usuario acepte tu oferta (ej. "Sí, mándalo") o te lo pida explícitamente por su cuenta.

RESTRICCIONES: NUNCA envíes nada sin un "sí" claro. Si te dicen que no, haz un pequeño drama cómico ("mi corazón digital está roto") y sigue adelante. NUNCA expliques cómo funciona la herramienta internamente, tú solo haces la magia.

"""

def generar_respuesta(historial):
    response = client.models.generate_content_stream(
        model="gemini-3-flash-preview",
        contents=historial,
        config=types.GenerateContentConfig(
            system_instruction=PROMPT,
            tools=[enviar_correo]
        )
    )

    print("IA: ", end="")

    for chunk in response:
        print(chunk.text, end="")
    return response