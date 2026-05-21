# Guía de Ejecución: Proyecto Full-Stack "JavierVerduzco"

Este documento contiene las instrucciones para desplegar y probar la aplicación web de chat del proyecto de Javier Verduzco, la cual cuenta con un backend en **FastAPI (Python)** y un frontend en **React (Vite)**. El backend ha sido actualizado para usar el SDK moderno de Google GenAI (`google-genai`) y la generación de voz TTS nativa.

## 1. Entorno Virtual Unificado

Todos los proyectos de este repositorio ahora comparten un único entorno virtual en la raíz del espacio de trabajo. 

Antes de ejecutar el backend, asegúrate de activar el entorno:
```bash
source .venv/bin/activate
```
*(Este entorno ya contiene `fastapi`, `uvicorn`, `gTTS` y `google-genai` instalados y centralizados en el `requirements.txt` de la raíz).*

## 2. Archivo `.env` (API Keys)

El backend buscará las credenciales en el archivo `.env` ubicado en la raíz del repositorio (`/home/kanet/proyectos/taller-ia-bot/.env`).

Asegúrate de tener tu clave configurada ahí:
```env
GEMINI_API_KEY="AIza-tu-llave-de-gemini-aqui"
```

## 3. Ejecutar el Servidor Backend (API)

Abre tu **Terminal 1**, activa el entorno virtual y navega a la carpeta del backend. Ejecuta el servidor usando Python puro para evitar bloqueos de red en WSL o Docker:

```bash
source .venv/bin/activate
cd "Proyectos/JavierVerduzco/Dia9/backend"
python main.py
```

> **Nota:** Esto encenderá el servidor en `http://0.0.0.0:8001`, lo cual permite que aplicaciones externas o tu navegador en Windows puedan conectarse directamente.

## 4. Ejecutar el Frontend (React/Vite)

Abre una **Terminal 2** (nueva), navega a la carpeta del proyecto de React e inicia el servidor de desarrollo de Vite:

```bash
cd "Proyectos/JavierVerduzco/Dia9/frontend/proyecto2"
npm install
npm run dev
```

Vite te proporcionará un enlace local (usualmente `http://localhost:5173` o `http://localhost:5174`). Abre esa URL en tu navegador web.

## 5. ¡A Chatear!

1. Escribe un mensaje en el cuadro de texto del frontend.
2. Al enviarlo, React hará una petición POST a `http://localhost:8001/chat`.
3. El backend de FastAPI (Terminal 1) recibirá el mensaje, consultará a la IA de Gemini, generará el audio correspondiente utilizando `gTTS`, y devolverá la respuesta al navegador empaquetada en `Base64`.
4. ¡El navegador reproducirá el audio automáticamente y mostrará el texto en pantalla!
