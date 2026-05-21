from google.genai import types

with open('/home/kanet/escuela/taller/bot_2/inauguracion.jpg', 'rb') as f:
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