import speech_recognition as sr
try:
    import pyaudio
except ImportError:
    pyaudio = None
import subprocess
import time


class AudioManager:

    def __init__(self):

        self.recognizer = sr.Recognizer()

        self.microphone_index = self.buscar_microfono()

    def buscar_microfono(self):
        
        if pyaudio is None:
            print("⚠️ PyAudio no está instalado. El micrófono no funcionará.")
            return None

        p = pyaudio.PyAudio()

        print("\n=== DISPOSITIVOS DE AUDIO ===")

        for i in range(p.get_device_count()):

            info = p.get_device_info_by_index(i)

            print(i, info["name"])

            if info["maxInputChannels"] > 0:

                print(f"\n🎤 Micrófono seleccionado: {info['name']}")

                return i

        print("⚠️ No se encontró micrófono.")

        return None

    def escuchar(self):

        if self.microphone_index is None:

            time.sleep(2)

            return ""

        try:

            with sr.Microphone(
                device_index=self.microphone_index
            ) as source:

                print("🎤 Escuchando...")

                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=1
                )

                audio = self.recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=10
                )

            texto = self.recognizer.recognize_google(
                audio,
                language="es-ES"
            )

            print("🗣️", texto)

            return texto

        except sr.WaitTimeoutError:

            return ""

        except Exception as e:

            print("ERROR MIC:", e)

            return ""

    def hablar(self, texto, callback_talking=None):

        if callback_talking:
            callback_talking(True)

        try:

            subprocess.run([
                "espeak-ng",
                "-v",
                "es",
                "-s",
                "166",
                texto
            ])

        except Exception as e:

            print("ERROR TTS:", e)

        if callback_talking:
            callback_talking(False)