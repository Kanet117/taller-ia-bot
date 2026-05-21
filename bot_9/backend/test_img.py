import asyncio
from ia import generar_respuesta_fastapi
import logging

logging.basicConfig(level=logging.INFO)

async def main():
    text, audio = await generar_respuesta_fastapi(text="Genera una imagen de un gato en la luna.")
    print("RESPONSE TEXT:")
    print(text[:200])

asyncio.run(main())
