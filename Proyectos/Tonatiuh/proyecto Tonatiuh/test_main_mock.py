import tkinter as tk
import os
import sys
import threading
import time

class MockTk:
    def after(self, ms, func, *args):
        func(*args)
        
tk.Tk = MockTk

import main
class MockVTuberWindow:
    def __init__(self, root, on_send_text_callback):
        self.root = root
        self.on_send_text_callback = on_send_text_callback
    def append_message(self, *args):
        print("append_message:", args)
    def set_talking_state(self, *args):
        pass

main.VTuberWindow = MockVTuberWindow

class MockAudioManager:
    def escuchar(self):
        return None
    def hablar(self, texto, callback_talking):
        pass
main.AudioManager = MockAudioManager

root = tk.Tk()
app = main.VTuberAIApp(root)
app.recibir_texto_escrito("hola")

print("Waiting for thread...")
time.sleep(15)
print("Done waiting.")
