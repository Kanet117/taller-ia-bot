import io
from PIL import Image
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os
import base64
from config import SYSTEM_PROMPT

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

_latest_generated_image = None

def generar_imagen_con_ia(prompt: str) -> str:
    """Generates an image using Imagen based on a prompt and captures the base64 image in a global variable."""
    global _latest_generated_image
    try:
        result = client.models.generate_images(
            model='imagen-4.0-generate-001',
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
            )
        )
        if result.generated_images:
            generated_image = result.generated_images[0]
            # Convert image bytes to base64
            image_bytes = generated_image.image.image_bytes
            
            # Compress the image
            image = Image.open(io.BytesIO(image_bytes))
            image.thumbnail((512, 512))
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=80)
            compressed_bytes = buffer.getvalue()
            
            base64_str = base64.b64encode(compressed_bytes).decode('utf-8')
            _latest_generated_image = base64_str
            return "Imagen generada con éxito."
    except Exception as e:
        print(f"Error generando la imagen: {e}")
        return f"Error generando la imagen: {e}"
    return "No se pudo generar la imagen."

async def generar_respuesta_fastapi(text: str = None, files: list = None, voice: str = "Aoede", history: list = None):
    global _latest_generated_image
    _latest_generated_image = None
    
    contents = []
    
    if files:
        for file_content, mime_type in files:
            if file_content and mime_type:
                contents.append(
                    types.Part.from_bytes(
                        data=file_content,
                        mime_type=mime_type,
                    )
                )
    if text:
        contents.append(text)

    if not contents:
        return "No input provided.", None, None

    chat_history = []
    if history:
        for msg in history:
            role = msg.get("role")
            parts = [types.Part.from_text(text=p) for p in msg.get("parts", []) if p]
            if parts:
                chat_history.append(types.Content(role=role, parts=parts))

    valid_history = []
    expected_role = "user"
    for msg in chat_history:
        if msg.role == expected_role:
            valid_history.append(msg)
            expected_role = "model" if expected_role == "user" else "user"
            
    if valid_history and valid_history[-1].role == "user":
        valid_history.pop()
        
    chat_history = valid_history

    chat = client.aio.chats.create(
        model='gemini-2.5-flash',
        history=chat_history,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            tools=[generar_imagen_con_ia],
        )
    )
    
    response_text_model = await chat.send_message(contents)
    
    text_response = ""
    if response_text_model.text:
        text_response = response_text_model.text

    audio_base64 = None
    if text_response:
        try:
            audio_response = await client.aio.models.generate_content(
                model='gemini-3.1-flash-tts-preview',
                contents=text_response,
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                voice_name=voice
                            )
                        )
                    )
                )
            )
            if audio_response.candidates and audio_response.candidates[0].content and audio_response.candidates[0].content.parts:
                for part in audio_response.candidates[0].content.parts:
                    if part.inline_data:
                        audio_base64 = base64.b64encode(part.inline_data.data).decode('utf-8')
        except Exception as e:
            print(f"Error generating audio: {e}")
                
    return text_response, audio_base64, _latest_generated_image
