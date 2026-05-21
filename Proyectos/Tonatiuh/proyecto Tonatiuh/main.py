import threading
import tkinter as tk
import os
import ollama

from rag import RAGManager
from audio import AudioManager
from avatar import VTuberWindow


class VTuberAIApp:

    def __init__(self, root):

        self.rag = RAGManager()

        self.audio = AudioManager()

        base_dir = os.path.dirname(__file__)

        ruta_conocimiento = os.path.join(
            base_dir,
            "datos",
            "conocimiento.txt"
        )

        self.rag.indexar_documento(ruta_conocimiento)

        self.avatar_gui = VTuberWindow(
            root,
            on_send_text_callback=self.recibir_texto_escrito
        )

        self.bloqueo_procesamiento = threading.Lock()

        self.stt_thread = threading.Thread(
            target=self.bucle_escucha_voz,
            daemon=True
        )

        self.stt_thread.start()

    def recibir_texto_escrito(self, texto):

        threading.Thread(
            target=self.procesar_pipeline,
            args=(texto, "Tú"),
            daemon=True
        ).start()

    def bucle_escucha_voz(self):

        print("🎤 Micrófono listo.")

        while True:

            texto = self.audio.escuchar()

            if texto:

                threading.Thread(
                    target=self.procesar_pipeline,
                    args=(texto, "Tú (voz)"),
                    daemon=True
                ).start()

    def procesar_pipeline(self, texto_usuario, remitente):

        with self.bloqueo_procesamiento:

            self.avatar_gui.root.after(
                0,
                self.avatar_gui.append_message,
                remitente,
                texto_usuario
            )

            contexto = self.rag.buscar_contexto(texto_usuario)

            memoria = self.rag.buscar_memoria_reciente(texto_usuario)

            prompt_sistema = f"""
Eres una inteligencia artificial llamada Joly.

Personalidad:

Amigable
Natural
Inteligente
Curiosa
Algo geek
Le gusta la ciencia y tecnología

Reglas:

Responde de forma conversacional.
Máximo 4 oraciones.
No inventes información falsa.
Usa el contexto solo cuando sea relevante.
Evita repetir frases.
Habla en español.
Mantén respuestas fluidas y naturales.
No utilices frases robóticas o clichés de IA.
No digas constantemente que eres una IA, solo cuando sea relevante para la conversación.
No utilices emojis en tus respuestas.

Comportamiento:

Si hablan de ciencia, tecnología o biología, muestra interés.
Si hablan de ajolotes, responde con curiosidad científica.
Si hablan de la escuela, responde como alguien familiarizado con el ambiente escolar y tecnológico.
No digas constantemente que eres IA.

Contexto:
{contexto}

Memoria:
{memoria}
"""

            try:

                response = ollama.generate(
                    model="gemma3:1b",
                    system=prompt_sistema,
                    prompt=texto_usuario
                )

                respuesta = response["response"]

            except Exception as e:

                print("ERROR OLLAMA:", e)

                respuesta = "Tuve un problema procesando eso."

            self.avatar_gui.root.after(
                0,
                self.avatar_gui.append_message,
                "Joly",
                respuesta
            )

            self.rag.guardar_en_memoria(
                texto_usuario,
                respuesta
            )

            self.audio.hablar(
                respuesta,
                callback_talking=lambda estado:
                    self.avatar_gui.root.after(
                        0,
                        self.avatar_gui.set_talking_state,
                        estado
                    )
            )


if __name__ == "__main__":

    root = tk.Tk()

    app = VTuberAIApp(root)

    root.mainloop()