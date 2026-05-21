from google.genai import types

import os

image_path = os.path.join(os.path.dirname(__file__), 'inauguracion.jpg')
with open(image_path, 'rb') as f:
      image_bytes = f.read()

historial = []

def añadir_mensaje(text, role):
    historial.append(
        {
            "role": role,
            "parts": [
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type="image/jpg"
                ),
                types.Part.from_text(
                     text=text
                )
            ]
        }
    )

def limpiar_historial():
    historial.clear()