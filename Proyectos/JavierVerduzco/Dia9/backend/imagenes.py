from PIL import Image
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

image = Image.open()
response = client.models.generate_content(
    model="gemini-3-flash-preview",
    contents=[image, "Describe está imagen"]
)
print(response.text)