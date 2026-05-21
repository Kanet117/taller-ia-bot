from typing import Optional
from google.genai import types
import base64

historial = []

def añadir_mensaje(text, role, imagen_b64=None):
    parts = []
    if text:
        parts.append(types.Part.from_text(text=text))
        
    if imagen_b64:
        try:
            # Formato esperado: data:image/jpeg;base64,/9j/4AA...
            header, b64_data = imagen_b64.split(",", 1)
            mime_type = header.split(";")[0].split(":")[1]
            image_bytes = base64.b64decode(b64_data)
            parts.append(types.Part.from_bytes(data=image_bytes, mime_type=mime_type))
        except Exception as e:
            print("Error al procesar la imagen:", e)
            
    historial.append(
        types.Content(role=role, parts=parts)
    )

def limpiar_historial():
    historial.clear()
