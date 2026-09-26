<div align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=Ollama&logoColor=white" />
  <img src="https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" />
</div>

<h1 align="center">🤖 J.A.R.V.I.S. - Asistente Personal con IA Local</h1>

<p align="center">
  Un asistente de escritorio flotante, inteligente y 100% privado impulsado por modelos de lenguaje locales (Ollama), diseñado para automatizar tu flujo de trabajo en Windows mediante comandos de voz.
</p>

<p align="center">
  Creado con ❤️ por <b>C7Dev_</b>
</p>

---

## 🌟 Características Principales

- **🔒 100% Privado y Local:** Integración nativa con **Ollama**. Todo el procesamiento de IA ocurre en tu propia máquina (sin enviar datos a la nube).
- **🎙️ Control por Voz:** Reconocimiento de voz en español para controlar tu PC ("abre Chrome", "escribe esto", "toma captura", etc.).
- **⚛️ Interfaz Flotante (Arc Reactor):** Un widget minimalista, transparente e interactivo que se sitúa sobre todas tus ventanas.
- **⌨️ Automatización del Teclado y Mouse:** Jarvis puede escribir textos por ti simulando pulsaciones reales de teclado, ideal para llenar formularios o escribir código.
- **🗣️ Personalidad Dinámica:** Respuestas casuales, directas y con variaciones para sentirse más humano y menos robótico.
- **🔊 Lee Textos Seleccionados:** Selecciona cualquier texto en la pantalla y pídele a Jarvis que te lo lea en voz alta.

## 🛠️ Tecnologías y Librerías

- **Python 3.x**
- **Ollama** (Backend de IA)
- `pyttsx3` (Síntesis de voz offline)
- `SpeechRecognition` (Reconocimiento de voz)
- `Tkinter` (Interfaz gráfica de usuario)
- `pyautogui` & `pyperclip` (Automatización de sistema y portapapeles)

## 🚀 Instalación y Uso

1. **Instalar dependencias:**
   ```bash
   pip install speechrecognition pyttsx3 pyautogui pyperclip Pillow requests
   ```
2. **Instalar Ollama:** 
   Descarga e instala [Ollama](https://ollama.com/) en tu sistema y descarga tu modelo favorito (ej: `gemma3:4b` o `llama3`).
3. **Ejecutar a Jarvis:**
   ```bash
   python jarvis.py
   ```

## 🎯 Comandos Soportados

| Comando / Frase (Ejemplos) | Acción |
| :--- | :--- |
| *"Abre Google Chrome"* | Inicia la aplicación solicitada. |
| *"Toma una captura"* | Guarda un screenshot en tu carpeta de Imágenes. |
| *"Escribe hola mundo"* | Jarvis teclea el texto donde esté el cursor. |
| *"Lee esto / Lee el texto"* | Copia el texto seleccionado y lo lee en voz alta. |
| *"Busca [tema] en Google"* | Abre el navegador y realiza la búsqueda. |
| *"Pausar / Silencio"* | Pone a Jarvis en modo espera. |
| *"Cualquier otra pregunta"* | La envía a Ollama y responde con inteligencia artificial. |

## 🛡️ Privacidad y Seguridad
Este proyecto fue diseñado con la privacidad como prioridad número uno.
- No hay telemetría.
- No hay recolección de datos.
- Las consultas al modelo de lenguaje se hacen de forma estrictamente local a través del puerto `11434`.
- *(Nota: El motor de voz a texto utiliza Google Speech API de forma temporal; se recomienda sustituir por `Vosk` para una privacidad absoluta fuera de línea).*

## 🤝 Contribuciones
¡Las contribuciones son bienvenidas! Si tienes ideas para mejorar la UI, agregar más integraciones (como Spotify, Discord API, o automatización de hogar inteligente), siéntete libre de hacer un fork y enviar un Pull Request.

---
<p align="center">
  <i>"A veces hay que correr antes de poder caminar." - Tony Stark</i>
</p>
