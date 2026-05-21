import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk, ImageDraw
import time
import math
import os


class VTuberWindow:
    def __init__(self, root, on_send_text_callback=None):
        self.root = root
        self.root.title("AI - Live Chat Mode")

        self.on_send_text = on_send_text_callback

        # =========================================================
        # CONFIGURACIÓN GENERAL
        # =========================================================

        self.w_avatar = 1000
        self.w_chat = 400
        self.h = 1000

        self.root.geometry(f"{self.w_avatar + self.w_chat}x{self.h}")

        # =========================================================
        # PALETA DE COLORES
        # =========================================================

        self.paleta = [
            "#FFB6C1",
            "#E6E6FA",
            "#89CFF0",
            "#B5EAD7",
            "#FDFD96",
            "#FFD1DC"
        ]

        self.color_idx_1 = 0
        self.color_idx_2 = 1

        self.transicion_factor = 0.0
        self.velocidad_fading = 0.05

        # =========================================================
        # CONTENEDORES PRINCIPALES
        # =========================================================

        # Frame avatar
        self.avatar_frame = tk.Frame(
            root,
            width=self.w_avatar,
            height=self.h
        )

        self.avatar_frame.pack(
            side="left",
            fill="both",
            expand=True
        )

        # Frame chat
        self.chat_frame = tk.Frame(
            root,
            width=self.w_chat,
            height=self.h,
            bg="#1e1e2e"
        )

        self.chat_frame.pack(
            side="right",
            fill="both",
            expand=False
        )

        # =========================================================
        # CANVAS PRINCIPAL
        # =========================================================

        self.canvas = tk.Canvas(
            self.avatar_frame,
            highlightthickness=0
        )

        self.canvas.pack(
            fill="both",
            expand=True
        )

        # =========================================================
        # CHAT PANEL
        # =========================================================

        self.chat_log = scrolledtext.ScrolledText(
            self.chat_frame,
            wrap=tk.WORD,
            bg="#252538",
            fg="#f8f8f2",
            font=("Arial", 10),
            state="disabled"
        )

        self.chat_log.pack(
            padx=10,
            pady=10,
            fill="both",
            expand=True
        )

        # =========================================================
        # INPUT FRAME
        # =========================================================

        self.input_frame = tk.Frame(
            self.chat_frame,
            bg="#1e1e2e"
        )

        self.input_frame.pack(
            padx=10,
            pady=(0, 10),
            fill="x"
        )

        # Entrada texto
        self.entry = tk.Entry(
            self.input_frame,
            bg="#252538",
            fg="#f8f8f2",
            insertbackground="white",
            font=("Arial", 11),
            highlightthickness=0
        )

        self.entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=4
        )

        self.entry.bind("<Return>", self._al_enviar)

        # Botón enviar
        self.btn_enviar = tk.Button(
            self.input_frame,
            text="Enviar",
            bg="#ffb6c1",
            fg="#1e1e2e",
            font=("Arial", 9, "bold"),
            relief="flat",
            command=self._al_enviar
        )

        self.btn_enviar.pack(
            side="right",
            padx=(5, 0)
        )

        # =========================================================
        # CARGA DE ASSETS
        # =========================================================

        img_size = (800, 800)

        self.partes_pil = {
            "idle": self._cargar_pil(
                "assets/idle.png",
                img_size
            ),

            "talking": self._cargar_pil(
                "assets/talking.png",
                img_size
            )
        }

        self.tk_images = {
            k: ImageTk.PhotoImage(v)
            for k, v in self.partes_pil.items()
        }

        # =========================================================
        # VARIABLES DE ESTADO
        # =========================================================

        self.is_talking = False
        self.boca_actual_es_abierta = False

        self.start_time = time.time()

        # =========================================================
        # FONDO
        # =========================================================

        self.tk_fondo = None

        self.id_fondo = self.canvas.create_image(
            0,
            0,
            anchor="nw"
        )

        # =========================================================
        # AVATAR
        # =========================================================

        self.id_avatar = self.canvas.create_image(
            0,
            0,
            image=self.tk_images["idle"],
            anchor="center"
        )

        # =========================================================
        # EVENTOS
        # =========================================================

        self.canvas.bind(
            "<Configure>",
            self._centrar_avatar
        )

        # =========================================================
        # BUCLES
        # =========================================================

        self.bucle_fondo_degradado()
        self.bucle_movimiento_fluido()
        self.bucle_hablar()

    # =============================================================
    # CARGA DE IMÁGENES
    # =============================================================

    def _cargar_pil(self, ruta, size):

        ruta_absoluta = os.path.join(
            os.path.dirname(__file__),
            ruta
        )

        try:
            return Image.open(ruta_absoluta)\
                .convert("RGBA")\
                .resize(size, Image.Resampling.LANCZOS)

        except FileNotFoundError:
            print(f"❌ Falta el archivo: {ruta_absoluta}")
            exit()

    # =============================================================
    # UTILIDADES COLOR
    # =============================================================

    def _hex_a_rgb(self, hex_str):

        return tuple(
            int(hex_str.lstrip('#')[i:i+2], 16)
            for i in (0, 2, 4)
        )

    def _rgb_a_hex(self, rgb):

        return '#%02x%02x%02x' % rgb

    def _interpolación_color(self, c1, c2, f):

        r1, g1, b1 = self._hex_a_rgb(c1)
        r2, g2, b2 = self._hex_a_rgb(c2)

        return self._rgb_a_hex((
            int(r1 + (r2 - r1) * f),
            int(g1 + (g2 - g1) * f),
            int(b1 + (b2 - b1) * f)
        ))

    # =============================================================
    # CENTRAR AVATAR
    # =============================================================

    def _centrar_avatar(self, event=None):

        x = self.canvas.winfo_width() / 2
        y = self.canvas.winfo_height() / 2

        self.canvas.coords(
            self.id_avatar,
            x,
            y
        )

    # =============================================================
    # APPEND CHAT
    # =============================================================

    def append_message(self, remitente, mensaje):

        self.chat_log.config(state="normal")

        self.chat_log.insert(
            tk.END,
            f"💬 {remitente}: {mensaje}\n\n"
        )

        self.chat_log.config(state="disabled")

        self.chat_log.see(tk.END)

    # =============================================================
    # ENVIAR TEXTO
    # =============================================================

    def _al_enviar(self, event=None):

        texto = self.entry.get().strip()

        if texto and self.on_send_text:

            self.entry.delete(0, tk.END)

            self.on_send_text(texto)

    # =============================================================
    # TALKING STATE
    # =============================================================

    def set_talking_state(self, talking):

        self.is_talking = talking

        if not talking:

            self.canvas.itemconfig(
                self.id_avatar,
                image=self.tk_images["idle"]
            )

            self.boca_actual_es_abierta = False

    # =============================================================
    # FONDO DEGRADADO DINÁMICO
    # =============================================================

    def bucle_fondo_degradado(self):

        self.transicion_factor += self.velocidad_fading

        if self.transicion_factor >= 1.0:

            self.transicion_factor = 0.0

            self.color_idx_1 = self.color_idx_2

            self.color_idx_2 = (
                self.color_idx_2 + 1
            ) % len(self.paleta)

        osc = (
            math.sin(time.time() * 0.5) + 1
        ) / 2

        c_top = self._interpolación_color(
            self.paleta[self.color_idx_1],
            self.paleta[self.color_idx_2],
            self.transicion_factor * 0.8
        )

        c_bot = self._interpolación_color(
            self.paleta[self.color_idx_2],
            self.paleta[self.color_idx_1],
            (1 - self.transicion_factor) * osc
        )

        rgb_t = self._hex_a_rgb(c_top)
        rgb_b = self._hex_a_rgb(c_bot)

        grad_pil = Image.new("RGB", (1, 64))

        draw = ImageDraw.Draw(grad_pil)

        for y in range(64):

            fy = y / 63.0

            color = (
                int(rgb_t[0] + (rgb_b[0] - rgb_t[0]) * fy),
                int(rgb_t[1] + (rgb_b[1] - rgb_t[1]) * fy),
                int(rgb_t[2] + (rgb_b[2] - rgb_t[2]) * fy)
            )

            draw.point((0, y), color)

        # Tamaño REAL del canvas
        canvas_width = max(
            self.canvas.winfo_width(),
            1
        )

        canvas_height = max(
            self.canvas.winfo_height(),
            1
        )

        self.tk_fondo = ImageTk.PhotoImage(
            grad_pil.resize(
                (canvas_width, canvas_height),
                Image.Resampling.BILINEAR
            )
        )

        self.canvas.itemconfig(
            self.id_fondo,
            image=self.tk_fondo
        )

        self.root.after(
            50,
            self.bucle_fondo_degradado
        )

    # =============================================================
    # MOVIMIENTO FLUIDO
    # =============================================================

    def bucle_movimiento_fluido(self):

        dy = 5 * math.sin(
            2.0 * (time.time() - self.start_time)
        )

        x = self.canvas.winfo_width() / 2

        y = (
            self.canvas.winfo_height() / 2
        ) + dy

        self.canvas.coords(
            self.id_avatar,
            x,
            y
        )

        self.root.after(
            16,
            self.bucle_movimiento_fluido
        )

    # =============================================================
    # ANIMACIÓN HABLAR
    # =============================================================

    def bucle_hablar(self):

        if self.is_talking:

            img = (
                self.tk_images["idle"]
                if self.boca_actual_es_abierta
                else self.tk_images["talking"]
            )

            self.canvas.itemconfig(
                self.id_avatar,
                image=img
            )

            self.boca_actual_es_abierta = \
                not self.boca_actual_es_abierta

            self.root.after(
                180,
                self.bucle_hablar
            )

        else:

            self.root.after(
                100,
                self.bucle_hablar
            )