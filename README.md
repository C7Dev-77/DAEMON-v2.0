<div align="center">
  <img src="daemon_logo.png" width="180" alt="D.A.E.M.O.N. Cyber Logo" />
  <h1>⚡ D.A.E.M.O.N. V2.0</h1>
  <h3>Digital Automated Entity for Monitoring & Operations Network</h3>
  <p><i>Asistente Cibernético Personal Autónomo para Windows con Inteligencia Artificial Local y HUD Espectral 3D</i></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/Ollama-Local_AI-000000?style=for-the-badge&logo=Ollama&logoColor=white" alt="Ollama" />
    <img src="https://img.shields.io/badge/GUI-CustomTkinter-1f6feb?style=for-the-badge" alt="CustomTkinter" />
    <img src="https://img.shields.io/badge/HUD-Nebula_3D-9900FF?style=for-the-badge" alt="Nebula 3D HUD" />
    <img src="https://img.shields.io/badge/Windows-11_CoreAudio-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows" />
    <img src="https://img.shields.io/badge/License-MIT-success?style=for-the-badge" alt="License MIT" />
  </p>

  <p>Creado por <b><a href="https://github.com/C7Dev-77">Cristian Morales (C7Dev_)</a></b></p>
</div>

---

## 📖 Acerca del Proyecto

**D.A.E.M.O.N.** es un asistente virtual autónomo de escritorio de alto rendimiento diseñado para **Windows 10/11**. Combina automatización nativa del sistema operativo, visión, procesamiento de voz en tiempo real y capacidades cognitivas avanzadas gracias a su integración con modelos de lenguaje locales y en la nube.

Su arquitectura se compone de dos interfaces complementarias:
1. **HUD Flotante Espectral 3D (Nebulosa Galáctica):** Un widget interactivo, ligero y siempre visible con proyección de partículas en 3D (anillo orbital de 1400 partículas + núcleo esférico de plasma) que reacciona de forma dinámica a los estados de escucha, pensamiento y reposo.
2. **Dashboard Central Home:** Un entorno de control completo con estética oscura de alta tecnología desarrollado en `CustomTkinter`, con historial de chat interactivo, panel de configuración visual, gestión de modelos IA y selector de temas neón.

DAEMON opera con privacidad total: procesa el lenguaje de manera local a través de [Ollama](https://ollama.com/), garantizando que las conversaciones, la memoria persistente y las instrucciones nunca salgan del equipo.

---

## 🌟 Capacidades y Características

| Módulo | Capacidad | Descripción Técnica |
|---|---|---|
| 🧠 **Cerebro Cognitivo** | IA Local + Memoria Persistente | Conexión directa a Ollama (`gemma4:31b-cloud`, `llama3.2`, `phi3`, etc.) con inyección de contexto a largo plazo (`memoria_daemon.txt`). Trato leal, formal y personalizado como *"Amo"*. |
| 🌌 **HUD Nebulosa 3D** | Partículas Matemáticas Orbitantes | Renderizado a 30 FPS en `Canvas` con proyección en perspectiva 3D, mapa de colores optimizado mediante LUT y reactividad por estado (idle, escuchando, pensando, pausado). |
| 🎙️ **Voz Bidireccional** | Reconocimiento y Síntesis Nativa | Detección de voz en segundo plano con umbrales adaptativos y síntesis vocal en español clara y natural sin latencia externa (`pyttsx3`). |
| 🔊 **Volumen Maestro** | Windows CoreAudio (`pycaw`) | Control a porcentajes numéricos exactos (*"pon el volumen en 50%"*, *"baja al 20%"*), muteo instantáneo y variaciones relativas. |
| 🎵 **Control Multimedia** | Integración Spotify & Medios | Búsqueda y reproducción directa de canciones o artistas en Spotify, control de pausas, pistas siguientes y anteriores. |
| 📸 **Captura Silenciosa** | Screenshots en Background | Captura de pantalla instantánea almacenada en `Imágenes\Capturas DAEMON` sin desplegar ventanas ni interferir con el trabajo en pantalla. |
| ⌨️ **Escritura Asistida** | Automatización de Entrada | Dictado y tipeo automatizado de texto mediante simulación de teclado y portapapeles con soporte íntegro de tildes y caracteres en español. |
| 🌦️ **Meteorología en Vivo** | Open-Meteo REST API | Consulta meteorológica en tiempo real y pronósticos detallados para el día siguiente sin requerir claves de API externas. |
| 🌐 **Navegación Web** | Búsquedas Normales e Incógnito | Apertura inteligente de navegadores web y consultas en Google o YouTube según instrucción directa. |
| 🚀 **Gestor de Aplicaciones** | Lanzador y Terminador de Procesos | Inicia y cierra programas del sistema reconociendo herramientas de desarrollo (Antigravity IDE, VS Code, terminales), reproductores y navegadores. |
| 🎨 **Paletas de Neón** | Temas Espectrales | Múltiples estilos visuales configurables: Nebulosa Espectral Multicolor, Ámbar Neón, Cyan Neón, Verde Esmeralda, Rojo Carmesí y Púrpura Cyberpunk. |

---

## 🖥️ Controles del Widget Flotante

```
                 [ Anillo Galáctico de 1400 Partículas 3D ]
                            ╭──────────╮
                         ╭──┤  ●    ●  ├──╮   <-- Ojos Reactivos Centrales
                         │  ╰──────────╯  │
                         ╰────────────────╯
```

- **Clic Izquierdo:** Alterna entre escuchar comandos o pausar la escucha activa.
- **Doble Clic:** Abre o cierra el **Dashboard Central Home** a pantalla completa.
- **Clic Derecho:** Despliega el menú contextual con accesos rápidos:
  - 🏠 *Home / Pantalla Completa*
  - 🎙️ *Escuchar / Hablar*
  - ⏸️ *Pausar / Silenciar*
  - 📸 *Captura en Segundo Plano*
  - ⚙️ *Configuración*
  - ❌ *Cerrar DAEMON*
- **Arrastre Sostenido:** Mueve el widget flotante con total libertad a cualquier punto de la pantalla.

---

## 🛠️ Tecnologías y Arquitectura

- **Lenguaje:** Python 3.12+ (tipado estricto verificado con Pyright / Pyrefly)
- **Motor de IA:** [Ollama](https://ollama.com/) (compatible con modelos locales o cloud)
- **Interfaz Principal:** `customtkinter` (Dark Theme)
- **HUD Flotante:** `tkinter` con colorkey transparente nativo de Windows y matemáticas matriciales `numpy`
- **Control de Audio:** `pycaw` + `comtypes` (Windows CoreAudio API)
- **Entrada de Voz:** `SpeechRecognition` + `PyAudio`
- **Salida de Voz:** `pyttsx3` (SAPI5 nativo de Windows)
- **Automatización de Sistema:** `pyautogui`, `pyperclip`, `psutil`
- **Servicios Web:** Open-Meteo APIs (Geocoding & Forecast)

---

## 🚀 Instalación y Puesta en Marcha

### 1. Clonar el repositorio
```bash
git clone https://github.com/C7Dev-77/DAEMON-v2.0.git
cd DAEMON-v2.0
```

### 2. Crear y activar entorno virtual
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Ollama
1. Descarga e instala [Ollama](https://ollama.com/).
2. Descarga tu modelo de preferencia:
```bash
ollama run gemma4:31b-cloud
# o modelos locales ligeros:
# ollama pull llama3.2:3b
# ollama pull gemma2:9b
```

### 5. Iniciar DAEMON
```bash
python daemon_gui.py
```

---

## 📦 Compilación a Binario `.exe`

DAEMON incluye la configuración completa de PyInstaller para compilar un binario independiente de un solo archivo que funciona sin requerir Python instalado en la máquina objetivo:

```bash
pyinstaller --clean --noconfirm DAEMON.spec
```

El ejecutable optimizado se generará en la carpeta `dist\DAEMON.exe` con su icono espectral de alta resolución incrustado y todas las dependencias empaquetadas.

---

## 🎯 Ejemplos de Comandos por Voz y Texto

| Instrucción / Comando | Acción Ejecutada |
|---|---|
| *"Pon [canción o artista] en Spotify"* | Inicia la reproducción inmediata en Spotify. |
| *"Pausa la música"* / *"Siguiente pista"* | Control multimedia directo del reproductor. |
| *"Sube el volumen al 70%"* / *"Silencia el audio"* | Ajuste preciso del volumen del sistema. |
| *"Toma una captura de pantalla"* | Captura silenciosa guardada en la carpeta de imágenes. |
| *"Escribe: Hola mundo desde DAEMON"* | Escribe automáticamente el texto en el cursor activo. |
| *"¿Cómo estará el clima en Sincelejo mañana?"* | Previsión meteorológica completa (temperatura y lluvia). |
| *"¿Quién fue Alan Turing?"* / *"Explícame la teoría de la relatividad"* | Razonamiento cognitivo detallado provisto por el LLM. |
| *"Abre Google Chrome"* / *"Abre Antigravity"* | Lanzamiento de programas y herramientas de trabajo. |
| *"Entra en modo pausa"* / *"Silencio"* | Pone al asistente en reposo hasta nueva orden. |

---

## ⚙️ Configuración (`daemon_config.json`)

El archivo de configuración permite ajustar todos los parámetros operativos:

```json
{
  "owner_name": "Amo",
  "default_city": "Sincelejo",
  "model": "gemma4:31b-cloud",
  "voice_speed": 180,
  "voice_enabled": true,
  "show_floating_widget": true,
  "mic_energy_threshold": 300,
  "neon_theme": "spectral"
}
```

*Temas disponibles para `neon_theme`:* `"spectral"` (Nebulosa Galáctica 3D), `"amber"` (Ámbar Neón), `"cyan"` (Cyan Neón), `"green"` (Verde Esmeralda), `"red"` (Rojo Carmesí), `"purple"` (Púrpura Cyberpunk).

---

## 🛡️ Privacidad y Seguridad

- **Sin Telemetría:** DAEMON no recopila ni envía datos de telemetría a servidores de terceros.
- **Procesamiento Local:** Las inferencias de lenguaje se ejecutan en tu propio equipo a través de la API local de Ollama (`localhost:11434`).
- **Persistencia Aislada:** La memoria (`memoria_daemon.txt`), configuraciones y capturas residen exclusivamente en tu almacenamiento local.

---

## 📄 Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo [`LICENSE`](LICENSE) para más detalles.

---

<div align="center">
  <sub>Desarrollado con dedicación por <b>Cristian Morales (C7Dev_)</b></sub>
</div>
