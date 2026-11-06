<div align="center">
  <img src="daemon_logo.png" width="180" alt="D.A.E.M.O.N. Cyber Reactor Logo" />
  <h1>⚡ D.A.E.M.O.N. V2.0</h1>
  <h3>Digital Automated Entity for Monitoring & Operations Network</h3>
  <p><i>Evolución de siguiente generación de J.A.R.V.I.S. V1.0 — Asistente Cibernético Personal Autónomo para Windows</i></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/Ollama-Local_AI-000000?style=for-the-badge&logo=Ollama&logoColor=white" alt="Ollama" />
    <img src="https://img.shields.io/badge/GUI-CustomTkinter-1f6feb?style=for-the-badge" alt="CustomTkinter" />
    <img src="https://img.shields.io/badge/HUD-Arc_Reactor-FF9900?style=for-the-badge" alt="Arc Reactor HUD" />
    <img src="https://img.shields.io/badge/Windows-11_CoreAudio-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows" />
    <img src="https://img.shields.io/badge/License-MIT-success?style=for-the-badge" alt="License MIT" />
  </p>

  <p>Creado por <b><a href="https://github.com/C7Dev-77">Cristian Morales (C7Dev_)</a></b></p>
</div>

---

## 📖 Acerca del Proyecto

**D.A.E.M.O.N.** es un asistente personal de escritorio de alto rendimiento para **Windows**, diseñado con una arquitectura dual única:
1. **HUD Flotante Arc Reactor:** Un widget interactivo, transparente y minimalista con un espectro de audio radial reactivo en tiempo real (32 bandas dinámicas) y efectos neón multi-capa.
2. **Dashboard Central Home:** Una interfaz de mando moderna inspirada en ChatGPT desarrollada con `CustomTkinter`, que incluye historial de chat interactivo, panel lateral retráctil y centro de ajustes completo.

A diferencia de los asistentes convencionales, **DAEMON opera de manera 100% privada y local** utilizando [Ollama](https://ollama.com/), garantizando que tus conversaciones, comandos y datos de sistema nunca salgan de tu equipo.

---

## 🌟 Novedades y Capacidades V2.0

| Módulo | Capacidad | Descripción |
|---|---|---|
| 🧠 **Cerebro Cognitivo** | IA Local + Memoria Persistente | Conexión directa a Ollama (`gemma4:31b-cloud`, `llama3.2`, etc.) con inyección de memoria persistente (`memoria_daemon.txt`). Trato leal y formal hacia su creador como *"Amo"*. |
| 🎵 **Control Spotify** | Integración Multimedia Nativa | Búsqueda y reproducción directa de canciones o artistas específicos, pasar pistas, retroceder, pausar y reanudar sin desincronización. |
| 🔊 **Volumen Maestro** | Windows CoreAudio (`pycaw`) | Control a porcentajes numéricos exactos (*"sube el volumen al 80%"*, *"baja al 20%"*), muteo instantáneo e incrementos relativos. |
| 📸 **Captura Silenciosa** | Screenshots en Segundo Plano | Captura de pantalla instantánea guardada directamente en `Imágenes\Capturas DAEMON` sin desplegar consolas, PowerShell ni interferir con la pantalla. |
| 🌦️ **Meteorología en Vivo** | Open-Meteo REST API | Consulta meteorológica en tiempo real y previsión detallada para el día de mañana (temperaturas, probabilidad de lluvia y condiciones) sin requerir API keys. |
| 🌐 **Navegación Web** | Google Normal e Incógnito | Apertura de búsquedas en modo normal de forma predeterminada; el modo incógnito solo se activa bajo instrucción explícita. |
| 🗣️ **Traductor Bidireccional** | Detección Lingüística | Traducción inmediata de oraciones o del contenido del portapapeles entre inglés y español sin rodeos. |
| 📚 **Cultura Enciclopédica** | Wikipedia + LLM | Respuestas precisas sobre figuras históricas, mandatarios mundiales, física cuántica, ciencia y eventos globales. |
| 🚀 **Gestor de Aplicaciones** | Lanzador y Terminador de Procesos | Inicia y cierra herramientas del sistema distinguiendo aplicaciones similares (ej. Antigravity IDE vs Visual Studio Code, Chrome, Spotify, CapCut, Office). |
| 🎨 **HUD Neón Dinámico** | Espectro Radial & 5 Temas | 32 barras de frecuencia armónica con reactividad según estado (Escuchando, Pensando, En pausa) y 5 paletas de color (Ámbar Neón, Cyan Clásico, Verde Esmeralda, Rojo Plasma, Púrpura Cyberpunk). |

---

## 🖥️ Estructura del HUD y Controles

```
                 [ 32 Barras de Espectro Dinámico ]
                           ╭──────────╮
                        ╭──┤  ▲   ●   ├──╮   <-- Reactor Neón Central
                        │  ╰──────────╯  │
                        ╰────────────────╯
```

- **Clic Izquierdo:** Activa / Desactiva el micrófono para escuchar comandos.
- **Doble Clic:** Despliega el **Dashboard Home** a pantalla completa estilo ChatGPT.
- **Clic Derecho:** Abre el menú contextual rápido:
  - 🏠 *Home / Pantalla Completa*
  - 🎙️ *Escuchar / Hablar*
  - ⏸️ *Pausar / Silenciar*
  - 📸 *Captura en Segundo Plano*
  - ⚙️ *Configuración*
  - ❌ *Cerrar DAEMON*
- **Arrastre:** Haz clic sostenido sobre el reactor para moverlo libremente a cualquier posición de la pantalla.

---

## 🛠️ Tecnologías Utilizadas

- **Python 3.12+**
- **IA Backend:** [Ollama](https://ollama.com/) (soporte para cualquier modelo local/cloud)
- **GUI Principal:** `customtkinter` (Dark Theme)
- **HUD Widget:** `tkinter` (Canvas 30 FPS + Win32 Colorkey Transparency)
- **Audio de Windows:** `pycaw` + `comtypes` (CoreAudio API)
- **Reconocimiento de Voz:** `SpeechRecognition` + `PyAudio`
- **Síntesis de Voz (TTS):** `pyttsx3` (Voces en español nativas de Windows)
- **Automatización del Sistema:** `pyautogui`, `pyperclip`, `psutil`
- **Meteorología:** Open-Meteo Geocoding & Forecast APIs

---

## 🚀 Instalación y Puesta en Marcha

### 1. Clonar el repositorio
```bash
git clone https://github.com/C7Dev-77/Jarvis-V1.0-C7Dev.git
cd Jarvis-V1.0-C7Dev
```

### 2. Crear entorno virtual (Recomendado)
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
# o modelos ligeros como:
# ollama pull llama3.2:3b
# ollama pull gemma2:9b
```

### 5. Iniciar DAEMON
Puedes iniciarlo con cualquiera de los dos comandos:
```bash
python daemon_gui.py
# o mediante el launcher de compatibilidad:
python jarvis.py
```

---

## 📦 Compilación a Ejecutable `.exe`

DAEMON incluye la especificación lista para compilar un binario independiente de un solo archivo que funciona sin necesidad de tener Python instalado:

```bash
pyinstaller --clean --noconfirm DAEMON.spec
```

El ejecutable resultante se generará en la carpeta `dist\DAEMON.exe` con su icono nativo incrustado y todas las librerías empaquetadas.

---

## 🎯 Ejemplos de Comandos por Voz

| Frase / Comando de Voz | Acción Ejecutada |
|---|---|
| *"Pon [nombre de canción] en Spotify"* | Busca y reproduce el tema en la app oficial de Spotify. |
| *"Pausa la música"* / *"Siguiente canción"* | Controla la reproducción multimedia. |
| *"Sube el volumen al 80%"* / *"Baja el volumen"* | Ajusta el volumen maestro de Windows. |
| *"Toma una captura de pantalla"* | Guarda el screenshot silenciosamente en segundo plano. |
| *"¿Cómo estará el clima mañana?"* | Informa temperatura, mínimas, máximas y estado del cielo. |
| *"Traduce 'Good morning, how are you?' a español"* | Traduce la frase al instante. |
| *"¿Quién fue Nikola Tesla?"* / *"¿Qué es la gravedad?"* | Respuesta enciclopédica clara y sintética. |
| *"Abre Google Chrome"* / *"Abre Google en incógnito"* | Abre el navegador en el modo solicitado. |
| *"Abre Antigravity"* / *"Cierra Antigravity"* | Controla las herramientas y editores de desarrollo. |
| *"Pausa"* / *"Entra en reposo"* | Silencia a DAEMON hasta que se le vuelva a ordenar. |

---

## ⚙️ Configuración (`daemon_config.json`)

El archivo de configuración permite personalizar el comportamiento del asistente:

```json
{
  "owner_name": "Amo",
  "default_city": "Sincelejo",
  "model": "gemma4:31b-cloud",
  "voice_speed": 180,
  "voice_enabled": true,
  "show_floating_widget": true,
  "mic_energy_threshold": 300,
  "neon_theme": "amber"
}
```

*Temas neón disponibles para `neon_theme`:* `"amber"`, `"cyan"`, `"green"`, `"red"`, `"purple"`.

---

## 🛡️ Privacidad Absoluta

- **Sin Telemetría:** DAEMON no recopila ni transmite estadísticas ni datos de uso.
- **Procesamiento Local:** Las inferencias de lenguaje se procesan en tu propia máquina a través del puerto local `11434` de Ollama.
- **Archivos Locales:** Toda la memoria (`memoria_daemon.txt`), configuraciones y capturas permanecen exclusivamente en tu disco duro.

---

## 📄 Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo [`LICENSE`](LICENSE) para más detalles.

---

<div align="center">
  <sub>Desarrollado con dedicación por <b>Cristian Morales (C7Dev_)</b></sub>
</div>
