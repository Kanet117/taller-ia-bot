# Taller de Inteligencia Artificial

Este repositorio consolida los proyectos y prácticas desarrollados durante el taller de Inteligencia Artificial. Incluye múltiples bots y aplicaciones interactivas (Bot 9, Proyecto de Javier Verduzco y Proyecto de Tonatiuh), abarcando modelos de lenguaje (LLMs), visión por computadora y generación de interfaces web.

## Requisitos Previos

Para ejecutar los proyectos de este repositorio, necesitarás instalar las siguientes herramientas:

* **Python 3.8+**: Entorno de ejecución principal para el backend y los bots.
* **Node.js y npm**: Necesarios para instalar dependencias y ejecutar los frontends de los proyectos web (React/Vite).
* **Ollama**: Utilizado para correr modelos de IA de manera local (principalmente en el proyecto de Tonatiuh). **Nota:** Es normal recibir advertencias o errores de conexión si `ollama serve` no se encuentra en ejecución al probar los scripts.
  * Para ejecutar el proyecto de Tonatiuh correctamente, debes tener el servicio activo y el modelo `gemma3:1b` descargado:
    ```bash
    ollama serve
    # (En otra terminal ejecuta:)
    ollama pull gemma3:1b
    ```

## Instalación

1. **Crear y activar un entorno virtual (venv)** en la raíz del proyecto:
   * En Linux/macOS:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   * En Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

2. **Instalar dependencias de Python**:
   Asegúrate de que tu entorno virtual esté activado y ejecuta:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar variables de entorno**:
   Se requiere un archivo `.env` para almacenar credenciales como la clave de API de Gemini y contraseñas de aplicaciones. Crea este archivo a partir del ejemplo proporcionado:
   ```bash
   cp .env.example .env
   ```
   Abre el archivo `.env` con tu editor de texto favorito y reemplaza los valores de ejemplo con tus credenciales reales. **Nunca** subas tu archivo `.env` al control de versiones (ya está excluido en el `.gitignore`).

## Ejecución de los Proyectos

A continuación, las instrucciones para iniciar cada uno de los proyectos principales.

### 1. Bot 9
Este proyecto consta de una API backend en Python y una interfaz frontend en React (Vite).

* **Iniciar el Backend**:
  ```bash
  source venv/bin/activate
  cd bot_9/backend
  python main.py
  ```

* **Iniciar el Frontend**:
  Abre una **nueva terminal**, navega a la ruta del frontend, instala las dependencias e inicia el servidor de desarrollo:
  ```bash
  cd bot_9/frontend/Proyecto-2
  npm install
  npm run dev
  ```

### 2. Proyecto de Javier Verduzco
Aplicación full-stack que interactúa con la API de IA.

* **Iniciar el Backend**:
  ```bash
  source venv/bin/activate
  cd Proyectos/JavierVerduzco/Dia9/backend
  python main.py
  ```

* **Iniciar el Frontend**:
  En una **nueva terminal**, ingresa a la carpeta correspondiente, instala dependencias de Node e inicia la aplicación:
  ```bash
  cd Proyectos/JavierVerduzco/Dia9/frontend/proyecto2
  npm install
  npm run dev
  ```

### 3. Proyecto de Tonatiuh
Script conversacional interactivo que utiliza Ollama de forma local y bases de datos vectoriales.

1. Asegúrate de que el servidor de **Ollama** esté corriendo en segundo plano:
   ```bash
   ollama serve
   ```
2. Ejecuta el archivo principal:
   ```bash
   source venv/bin/activate
   cd "Proyectos/Tonatiuh/proyecto Tonatiuh"
   python main.py
   ```

## Estructura del Repositorio
* `bot_1/` y `bot_2/`: Ejercicios iniciales y bots básicos.
* `bot_9/`: Bot avanzado con arquitectura cliente-servidor (React + FastAPI/Flask).
* `Proyectos/`: Carpeta con los proyectos finales desarrollados por los participantes del taller.
* `.env.example`: Plantilla de credenciales.
* `requirements.txt`: Dependencias del entorno de Python.