import tkinter as tk
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from main import VTuberAIApp

root = tk.Tk()
app = VTuberAIApp(root)
# simulate input
app.recibir_texto_escrito("hola")

# We run mainloop for 5 seconds to let the threads execute, then quit
root.after(5000, root.quit)
root.mainloop()
