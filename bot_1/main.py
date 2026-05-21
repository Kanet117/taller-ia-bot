from google import genai
from dotenv import load_dotenv
import os
from bot_2.ia import generar_respuesta
import bot_2.historial as historial

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

while True:
    print("\n")
    texto = input("Tu: ")
    if texto.lower() == "restart":
        historial.limpiar_historial()
    else:
        historial.añadir_mensaje(texto, "user")
        respuesta = generar_respuesta(historial.historial)
        historial.añadir_mensaje(texto, "model")