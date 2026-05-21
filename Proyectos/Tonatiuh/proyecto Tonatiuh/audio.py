import os
import sys
import subprocess

# Ocultar mágicamente los errores de ALSA en C (stderr)
try:
    from ctypes import CFUNCTYPE, c_char_p, c_int, cdll
    ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
    def py_error_handler(filename, line, function, err, fmt):
        pass
    c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
    asound = cdll.LoadLibrary('libasound.so.2')
    asound.snd_lib_error_set_handler(c_error_handler)
except:
    pass

import pyaudio
import queue
import threading
import wave

class AudioLoop:
    def __init__(self, callback_talking=None, callback_idle=None):
        self.callback_talking = callback_talking
        self.callback_idle = callback_idle
        
        self.is_playing = False
        self.running = True
        self.playback_process = None
        
        print("\n=== INICIANDO AUDIO ===")

        # PyAudio (solo para micrófono)
        self.p = pyaudio.PyAudio()
        self.audio_in_queue = queue.Queue()
        
        try:
            self.input_stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=24000,
                input=True,
                frames_per_buffer=2048
            )
            print("🎤 Micrófono conectado (24kHz PCM)")
        except Exception as e:
            print("⚠️ Error abriendo micrófono:", e)
            self.input_stream = None

        if self.input_stream:
            threading.Thread(target=self._in_loop, daemon=True).start()

    def _in_loop(self):
        while self.running and self.input_stream:
            try:
                data = self.input_stream.read(2048, exception_on_overflow=False)
                
                # Echo Cancellation: Si estamos reproduciendo voz de la IA, cortamos el micro
                if self.is_playing:
                    self.audio_in_queue.put_nowait(b'\x00' * len(data))
                else:
                    self.audio_in_queue.put_nowait(data)
            except Exception as e:
                pass

    def play_full_audio(self, pcm_bytes):
        """Reproduce una oración completa usando el reproductor nativo de Linux (aplay) para garantizar 0 tartamudeos en WSL"""
        
        temp_filename = "temp_response.wav"
        with wave.open(temp_filename, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2) # 16-bit
            wf.setframerate(24000)
            wf.writeframes(pcm_bytes)
            
        self.is_playing = True
        if self.callback_talking:
            self.callback_talking()
            
        try:
            def watch_dog():
                # Ejecuta aplay (o paplay si usas pulse puro). aplay es universal y robusto en WSL.
                self.playback_process = subprocess.Popen(
                    ["aplay", "-q", temp_filename], 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL
                )
                self.playback_process.wait()
                
                if self.is_playing:
                    self.is_playing = False
                    if self.callback_idle:
                        self.callback_idle()
                try:
                    os.remove(temp_filename)
                except:
                    pass
                    
            threading.Thread(target=watch_dog, daemon=True).start()
        except Exception as e:
            print("⚠️ Error al reproducir audio nativo:", e)
            self.is_playing = False
            if self.callback_idle:
                self.callback_idle()

    def stop_playback(self):
        """Detiene la reproducción instantáneamente si el usuario interrumpe (VAD)"""
        if self.is_playing:
            try:
                if self.playback_process and self.playback_process.poll() is None:
                    self.playback_process.terminate()
            except:
                pass
            self.is_playing = False
            if self.callback_idle:
                self.callback_idle()
            
    def close(self):
        self.running = False
        if self.input_stream:
            self.input_stream.stop_stream()
            self.input_stream.close()
        self.p.terminate()
        self.stop_playback()
