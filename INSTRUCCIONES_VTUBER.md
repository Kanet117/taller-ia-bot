# Guía de Ejecución: Proyecto VTuber "Tonatiuh"

Este documento contiene las instrucciones necesarias para levantar, configurar y depurar el proyecto del VTuber Joly, el cual ha sido migrado exitosamente a la API de **OpenAI Realtime** para ofrecer voz bidireccional de bajísima latencia.

## 1. Requisitos Previos (Entorno del Sistema)

Si estás ejecutando esto en Linux o WSL (Windows Subsystem for Linux), necesitas tener instaladas las librerías nativas de audio para que PyAudio y Pygame Mixer puedan interactuar con el hardware (micrófono y altavoces):

```bash
sudo apt-get update
sudo apt-get install -y portaudio19-dev python3-pyaudio alsa-utils pulseaudio
```

## 2. Entorno Virtual Unificado

Todos los proyectos del repositorio ahora comparten un único entorno virtual en la raíz del espacio de trabajo. 

Para activarlo, desde la raíz ejecuta:
```bash
source .venv/bin/activate
```

*(Si el entorno `.venv` no existe o faltan dependencias, puedes instalar todo con `pip install -r requirements.txt` estando en la raíz).*

## 3. Configuración de API Keys (.env)

El proyecto depende del archivo `.env` ubicado en la raíz del repositorio. Asegúrate de que este archivo exista y contenga tus llaves.
El VTuber Tonatiuh utiliza específicamente **OpenAI**. 

Ejemplo de `.env`:
```env
OPENAI_API_KEY="sk-proj-tu-llave-de-openai-aqui"
GEMINI_API_KEY="AIza-tu-llave-de-gemini-aqui"
```

## 4. Ejecución del VTuber

Una vez que el entorno virtual esté activado y el archivo `.env` configurado, navega a la carpeta del proyecto y ejecuta el archivo principal:

```bash
cd "Proyectos/Tonatiuh/proyecto Tonatiuh"
python main.py
```

### ¿Qué esperar al iniciar?
1. Verás mensajes en la terminal confirmando la detección del micrófono (a 24kHz) y el altavoz (a 48kHz para evitar problemas de PulseAudio en WSL).
2. Se conectará a `wss://api.openai.com/v1/realtime` y notificará `Conectado y escuchando`.
3. Se abrirá la interfaz gráfica (Tkinter) con el avatar de Joly. 
4. **Interacción:** Háblale por el micrófono o escríbele por la caja de texto inferior. Joly te contestará con voz nativa en tiempo real y la boca de su avatar se sincronizará automáticamente.

## 5. Detalles de la Arquitectura Interna

Si en el futuro necesitas modificar o hacer mantenimiento al código, ten en cuenta las siguientes decisiones de diseño:

- **WebSockets de OpenAI:** La comunicación se maneja manualmente usando la librería `websockets`. El modelo configurado es `gpt-realtime` (GA) que no requiere la antigua cabecera Beta.
- **Audio de Salida (WSL Safe):** PyAudio presenta problemas conocidos de fragmentación y "ALSA underruns" al reproducir audio bajo WSL. Por ello, el proyecto utiliza un enfoque híbrido: 
  - **Micrófono:** Capturado velozmente por hilos en PyAudio.
  - **Altavoces:** Las respuestas generadas por OpenAI se acumulan, se guardan en un archivo `.wav` en memoria, y se reproducen en calidad máxima usando `pygame.mixer` a 48kHz, lo que erradica por completo los tartamudeos (stuttering).
- **VAD (Voice Activity Detection):** Está configurado desde el servidor de OpenAI (`server_vad`). Si el usuario interrumpe a la IA, el servidor manda una señal de cancelación y el audio de Pygame se detiene instantáneamente (`pygame.mixer.music.stop()`).
- **Eliminación de Eco:** Cuando Joly está hablando, el hilo del micrófono inyecta bytes nulos (`\x00`) en la cola de entrada para ensordecer temporalmente a la IA y evitar que se quede atrapada en un bucle infinito escuchando su propia voz.