import threading
import tkinter as tk
import os
import asyncio
import json
import base64
import websockets

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

from audio import AudioLoop
from avatar import VTuberWindow


class VTuberAILiveApp:

    def __init__(self, root):
        # NOTA: Asegúrate de añadir OPENAI_API_KEY en tu archivo .env
        self.api_key = os.getenv("OPENAI_API_KEY")

        base_dir = os.path.dirname(__file__)
        ruta_conocimiento = os.path.join(base_dir, "datos", "conocimiento.txt")
        conocimiento = ""
        
        if os.path.exists(ruta_conocimiento):
            with open(ruta_conocimiento, "r", encoding="utf-8") as f:
                conocimiento = f.read()

        self.prompt_sistema = f"""Eres una inteligencia artificial llamada Joly.

Personalidad:
Amigable, natural, inteligente, curiosa, algo geek, le gusta la ciencia y tecnología.

Reglas:
1. Responde de forma conversacional.
2. Máximo 4 oraciones.
3. No inventes información falsa.
4. Usa el conocimiento base proporcionado abajo.
5. Evita repetir frases.
6. Habla en español.
7. Mantén respuestas fluidas y naturales.
8. No utilices frases robóticas o clichés de IA.
9. No utilices emojis en tus respuestas habladas.

=== CONOCIMIENTO BASE ===
{conocimiento}
"""

        self.avatar_gui = VTuberWindow(
            root,
            on_send_text_callback=self.recibir_texto_escrito
        )

        self.loop = asyncio.new_event_loop()
        self.websocket = None

        self.audio_loop = AudioLoop(
            callback_talking=lambda: self.avatar_gui.root.after(0, self.avatar_gui.set_talking_state, True),
            callback_idle=lambda: self.avatar_gui.root.after(0, self.avatar_gui.set_talking_state, False)
        )

        threading.Thread(target=self.run_asyncio_loop, daemon=True).start()

    def recibir_texto_escrito(self, texto):
        self.avatar_gui.append_message("Tú", texto)
        if self.websocket:
            msg = {
                "type": "conversation.item.create",
                "item": {
                    "type": "message",
                    "role": "user",
                    "content": [{"type": "input_text", "text": texto}]
                }
            }
            asyncio.run_coroutine_threadsafe(
                self.websocket.send(json.dumps(msg)),
                self.loop
            )
            # Pide a la IA que responda al mensaje escrito
            asyncio.run_coroutine_threadsafe(
                self.websocket.send(json.dumps({"type": "response.create"})),
                self.loop
            )

    def run_asyncio_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.live_connect_loop())

    async def live_connect_loop(self):
        ws_url = "wss://api.openai.com/v1/realtime?model=gpt-realtime"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        while True:
            print("🔄 Conectando a OpenAI Realtime API (WebSockets)...")
            try:
                # Disable ping_interval to avoid aggressive timeouts, or increase it
                async with websockets.connect(ws_url, additional_headers=headers, ping_interval=30, ping_timeout=120) as websocket:
                    self.websocket = websocket
                    print("✅ Conectado y escuchando (baja latencia - OpenAI).")
                    
                    # 1. Configuración inicial
                    config_message = {
                        "type": "session.update",
                        "session": {
                            "type": "realtime",
                            "instructions": self.prompt_sistema,
                            "audio": {
                                "input": {
                                    "format": {"type": "audio/pcm", "rate": 24000},
                                    "turn_detection": {
                                        "type": "server_vad",
                                        "threshold": 0.5,
                                        "prefix_padding_ms": 300,
                                        "silence_duration_ms": 600
                                    }
                                },
                                "output": {
                                    "format": {"type": "audio/pcm", "rate": 24000},
                                    "voice": "marin"
                                }
                            }
                        }
                    }
                    await websocket.send(json.dumps(config_message))
                    
                    # Esperar el session.created o setupComplete
                    await websocket.recv()

                    async def send_audio():
                        while True:
                            try:
                                # Usamos run_in_executor para no bloquear el asyncio loop porque la cola ahora es queue.Queue (hilos seguros)
                                chunk = await self.loop.run_in_executor(None, self.audio_loop.audio_in_queue.get)
                                
                                # El audio_loop ya aplica silencios internamente si la IA está hablando,
                                # pero si se escapa algo, lo mandamos.
                                encoded_data = base64.b64encode(chunk).decode('utf-8')
                                
                                audio_message = {
                                    "type": "input_audio_buffer.append",
                                    "audio": encoded_data
                                }
                                await websocket.send(json.dumps(audio_message))
                            except asyncio.CancelledError:
                                break
                            except Exception as e:
                                print("Error enviando audio:", e)
                                break

                    async def receive_responses():
                        # Acumulador para la respuesta actual
                        current_response_audio = bytearray()
                        
                        try:
                            async for message in websocket:
                                response = json.loads(message)
                                event_type = response.get("type")
                                
                                if event_type == "error":
                                    err_msg = response.get("error", {}).get("message", "Error desconocido")
                                    print("⚠️ ERROR API:", err_msg)
                                
                                # Acumular los deltas de audio de OpenAI (ahora es "response.audio.delta")
                                elif event_type == "response.output_audio.delta" or event_type == "response.audio.delta":
                                    audio_b64 = response.get("delta")
                                    if audio_b64:
                                        audio_bytes = base64.b64decode(audio_b64)
                                        current_response_audio.extend(audio_bytes)
                                        
                                # Cuando la IA termina de hablar, reproducimos TODA la oración junta vía Pygame
                                elif event_type == "response.output_audio.done" or event_type == "response.audio.done":
                                    if len(current_response_audio) > 0:
                                        self.audio_loop.play_full_audio(bytes(current_response_audio))
                                        current_response_audio.clear()
                                        
                                elif event_type == "conversation.item.input_audio_transcription.completed":
                                    texto_usuario = response.get("transcript", "")
                                    if texto_usuario.strip():
                                        self.avatar_gui.root.after(0, self.avatar_gui.append_message, "Tú (voz)", texto_usuario)
                                        
                                elif event_type == "response.output_audio_transcript.done" or event_type == "response.audio_transcript.done":
                                    texto_ia = response.get("transcript", "")
                                    if texto_ia.strip():
                                        self.avatar_gui.root.after(0, self.avatar_gui.append_message, "Joly", texto_ia)
                                        
                                elif event_type == "input_audio_buffer.speech_started":
                                    # Interrupciones (VAD) detectadas por OpenAI
                                    self.audio_loop.stop_playback()
                                    current_response_audio.clear()
                                    
                        except asyncio.CancelledError:
                            pass
                        except Exception as e:
                            print("Error recibiendo datos:", e)

                    send_task = asyncio.create_task(send_audio())
                    receive_task = asyncio.create_task(receive_responses())

                    done, pending = await asyncio.wait(
                        [send_task, receive_task],
                        return_when=asyncio.FIRST_COMPLETED
                    )
                    
                    for task in pending:
                        task.cancel()
                        
            except Exception as e:
                print(f"⚠️ Conexión perdida o error: {e}. Reconectando en 2 segundos...")
                await asyncio.sleep(2)

    def on_closing(self):
        self.audio_loop.close()
        self.avatar_gui.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = VTuberAILiveApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
