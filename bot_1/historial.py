historial = []

def añadir_mensaje(text, role):
    historial.append(
        {
            "role": role,
            "parts": [
                {
                    "text": text
                }
            ]
        }
    )

def limpiar_historial():
    historial.clear()