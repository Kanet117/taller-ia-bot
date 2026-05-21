import os
from dotenv import load_dotenv, find_dotenv
from google import genai
from google.genai import types

load_dotenv(find_dotenv())

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

try:
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents="hola",
        config=types.GenerateContentConfig(
            system_instruction="Eres Joly."
        )
    )
    print(response.text)
except Exception as e:
    import traceback
    traceback.print_exc()
