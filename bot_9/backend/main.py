from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from dotenv import load_dotenv
import os
import uvicorn
from ia import generar_respuesta_fastapi
from fastapi.responses import JSONResponse

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/chat")
async def chat_endpoint(
    text: Optional[str] = Form(None),
    voice: Optional[str] = Form("Aoede"),
    history: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    try:
        processed_files = []
        if files:
            for file in files:
                if file.filename:
                    file_content = await file.read()
                    mime_type = file.content_type
                    if file_content:
                        processed_files.append((file_content, mime_type))
            
        import json
        parsed_history = []
        if history:
            try:
                parsed_history = json.loads(history)
            except Exception as e:
                print(f"Error parsing history: {e}")

        response_text, audio_data, generated_image = await generar_respuesta_fastapi(text, processed_files, voice, parsed_history)
        return {"response": response_text, "audio": audio_data, "generated_image": generated_image}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
