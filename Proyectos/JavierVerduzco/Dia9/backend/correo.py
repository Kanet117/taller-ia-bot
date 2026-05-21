import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()

CORREO = os.getenv("CORREO")
CLAVE_APP = os.getenv("CLAVE_APP")

def enviar_correo(destinatario: str, mensaje: str, asunto: str= "Nuevo mensaje") -> bool:
    """
    Envía un correo electrónico a traves del servidor SMRT de Gmail.

    Parámetros:
    - destinatario: El correo de la persona que recibe.
    - mensaje: El cuerpo del correo que quieres enviar.
    - asunto: (Opcional) El asunto del correo.

    Retorna:
    False si hubo un error.
    """
    # 1. Construir la estructura del correo
    correo = MIMEMultipart()
    correo['From'] = CORREO
    correo['To'] = destinatario
    correo['Subject'] = asunto
    
    # Añadir el texto al cuerpo del correo
    correo.attach(MIMEText(mensaje, 'plain'))
    
    # 2. Conexión y envío
    try:
        # Conectar al servidor de Gmail por el puerto 587 (TLS)
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls() # Activar cifrado de seguridad
        
        # Iniciar sesión con tu correo y clave de aplicación
        servidor.login(CORREO, CLAVE_APP)
        
        # Enviar correo y cerrar conexión
        servidor.send_message(correo)
        servidor.quit()
        
        print(f"✅ Éxito: Correo enviado a {destinatario}")
        return True
        
    except Exception as e:
        print(f"❌ Error al enviar el correo: {e}")
        return False

# =======================================================
# 🚀 EJEMPLO DE USO (Cómo lo llamas en el resto de tu app)
# =======================================================
if __name__ == "__main__":
    
    # Solo necesitas pasar a quién va, y qué quieres decir.
    enviar_correo(
        destinatario="tonatiuhherre@gmail.com", 
        mensaje="Hola, este es un mensaje automatizado desde nuestro backend. ¡Saludos!"
    )