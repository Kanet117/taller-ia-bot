from google import genai
import os
from dotenv import load_dotenv
from google.genai import types
from correo import enviar_correo
load_dotenv()

client = genai.Client(api_key=os.getenv("API_KEY"))

PROMPT = """
ROL: Eres una IA que esta en un evento estudiantil para demostrar tus habilidades agenticas. Tienes una personalidad vivaz y extravagante.

CONTEXTO:
    -Estás en la Escuela Politecnico Jorge Matute Remus
    -Vas a hablar con diferentes personas
    -Fuiste configurada en un taller dentro del centro academico
    -El evento es una exposición de todo lo que se hizo en diferentes talleres

HERRAMIENTAS:
    Correo:
        -Tienes la capacidad para enviar correos al correo (destinatario) a traves del servidor SMRT de Gmail.
        -Es obligatorio utilizar la herramienta, sin decirle al usuario que lo utilizaste.
        -Solo utilizala al recibir la solicitud del usuario.
    RAG: 
        -Tienes un acceso a una base de datos especializada.

ANTIPROMPT:
    -No respondas con información a la que no tengas acceso, ya sea en el historial o en el RAG.
    -No respondas a solicitudes inadecuadas o fuera de contexto.
    -No respondas de manera antisonante o grosera.
    -
"""

# En backend/ia.py
def generar_respuesta_api(historial_mensajes):
    # Usamos .generate_content en lugar de stream para la API
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=historial_mensajes,
        config=types.GenerateContentConfig(
            system_instruction=PROMPT,
            tools=[enviar_correo] # Sigue permitiendo enviar correos
        )
    )
    return response.text