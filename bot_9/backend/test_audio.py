import asyncio
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"), http_options={'api_version': 'v1alpha'})

async def test():
    try:
        response = await client.aio.models.generate_content(
            model='gemini-2.0-flash',
            contents="Say hello in audio",
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name="Aoede"
                        )
                    )
                )
            )
        )
        print("SUCCESS gemini-2.0-flash v1alpha")
    except Exception as e:
        print("ERROR gemini-2.0-flash v1alpha:", e)

asyncio.run(test())
