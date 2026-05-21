from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import io
import base64
from gtts import gTTS
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

import ia as bot          # Para usar generar_respuesta_api
import historial as memoria # Para usar añadir_mensaje y el historial

app = FastAPI()

# PERMITIR QUE REACT SE CONECTE (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MensajeUsuario(BaseModel):
    texto: str
    imagen: Optional[str] = None

@app.post("/chat")
def chat(data: MensajeUsuario):
    try:
        if data.texto.lower() == "restart":
            memoria.limpiar_historial()
            return {"respuesta": "Historial reiniciado."}

        # 1. Guardar lo que dijo el usuario
        memoria.añadir_mensaje(data.texto, "user", data.imagen)
        
        # 2. Obtener respuesta de la IA
        respuesta_ia = bot.generar_respuesta_api(memoria.historial)
        
        # 3. Guardar lo que dijo la IA
        memoria.añadir_mensaje(respuesta_ia, "model")
        
        # 4. Generar audio a partir de la respuesta
        # Limpiar texto para que no lea asteriscos ni emojis
        import re
        texto_limpio = re.sub(r'[*_#`~]', '', respuesta_ia) # Eliminar caracteres markdown
        texto_limpio = re.sub(r'[^\w\s.,!?;:()¿¡-]', '', texto_limpio) # Eliminar emojis y otros simbolos
        
        # Generar TTS en español
        tts = gTTS(text=texto_limpio, lang='es')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        
        # Convertir a Base64 para enviar al frontend
        audio_b64 = base64.b64encode(audio_fp.read()).decode('utf-8')
        audio_data_uri = f"data:audio/mp3;base64,{audio_b64}"
        
        return {
            "respuesta": respuesta_ia,
            "audio": audio_data_uri
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
