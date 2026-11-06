import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import threading
import time
import sys
import os
import subprocess
import webbrowser
import json
import datetime
import math
import random
import re
import requests
import xml.etree.ElementTree as ET
import pyautogui
import pyperclip
import psutil
import pyjokes
import speech_recognition as sr
import pyttsx3
import winsound
import numpy as np
from PIL import Image

# =============================================================================
# SEGURIDAD Y PREVENCIÓN DE ERRORES PYAUTOGUI
# =============================================================================
setattr(pyautogui, 'FAILSAFE', False)
pyautogui.PAUSE = 0.05
CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0

def type_text(txt: str):
    """Escribe texto simulando teclado o pegado directo con soporte completo de tildes y caracteres especiales."""
    try:
        pyperclip.copy(txt)
        pyautogui.hotkey('ctrl', 'v')
    except Exception as e:
        print(f"[ERROR TYPE] {e}")

# =============================================================================
# GESTIÓN DE RUTAS Y CONFIGURACIÓN PERSISTENTE (COMPATIBLE CON .EXE)
# =============================================================================
def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def get_resource_path(rel_path):
    meipass = getattr(sys, '_MEIPASS', None)
    if meipass:
        return os.path.join(meipass, rel_path)
    return os.path.join(get_base_dir(), rel_path)

CONFIG_FILE = os.path.join(get_base_dir(), "daemon_config.json")
MEMORY_FILE = os.path.join(get_base_dir(), "memoria_daemon.txt")
SCREENSHOT_DIR = os.path.join(os.path.expanduser("~"), "Pictures", "Capturas DAEMON")

DEFAULT_CONFIG = {
    "owner_name": "Amo",
    "default_city": "Sincelejo",
    "model": "gemma4:31b-cloud",
    "voice_speed": 180,
    "voice_enabled": True,
    "show_floating_widget": True,
    "mic_energy_threshold": 300,
    "neon_theme": "spectral",
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULT_CONFIG, **data}
        except Exception as e:
            print(f"[CONFIG ERROR] {e}")
    return DEFAULT_CONFIG.copy()

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[CONFIG SAVE ERROR] {e}")

config = load_config()

# =============================================================================
# AUTO-INICIO DE OLLAMA EN SEGUNDO PLANO
# =============================================================================
def ensure_ollama_running():
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=1.5)
        if r.status_code == 200:
            return
    except:
        pass
    try:
        subprocess.Popen(
            ["ollama", "serve"],
            creationflags=CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception as e:
        print(f"[ERROR INICIAR OLLAMA] {e}")

ensure_ollama_running()

# =============================================================================
# MOTOR DE VOZ (TTS)
# =============================================================================
class VoiceEngine:
    def __init__(self):
        self._lock = threading.Lock()

    def speak(self, text):
        if not config.get("voice_enabled", True) or not text:
            return
        with self._lock:
            try:
                engine = pyttsx3.init()
                engine.setProperty("rate", int(config.get("voice_speed", 180)))
                voices = engine.getProperty("voices")
                if isinstance(voices, (list, tuple)):
                    for v in voices:
                        name_lower = str(getattr(v, "name", "")).lower()
                        langs = [str(l).lower() for l in getattr(v, "languages", [])]
                        if any("es" in l for l in langs) or "spanish" in name_lower or "helena" in name_lower or "sabina" in name_lower or "laura" in name_lower:
                            engine.setProperty("voice", v.id)
                            break
                clean_text = text.replace("*", "").replace("#", "").replace("`", "")
                engine.say(clean_text)
                engine.runAndWait()
                engine.stop()
            except Exception as e:
                print(f"[ERROR VOZ] {e}")

voice = VoiceEngine()

def speak(text):
    voice.speak(text)

def listen_audio(energy_boost=350):
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 1.0
    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.8)
            recognizer.energy_threshold += energy_boost
            recognizer.dynamic_energy_threshold = False
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=14)
            recognize_fn = getattr(recognizer, "recognize_google", None)
            if recognize_fn:
                text = recognize_fn(audio, language="es-ES")
            else:
                text = recognizer.recognize_google(audio, language="es-ES")  # type: ignore
            return text.lower().strip()
    except (sr.WaitTimeoutError, sr.UnknownValueError):
        return ""
    except Exception as e:
        print(f"[ERROR MIC] {e}")
        return ""

# =============================================================================
# CONTROL EXACTO DE VOLUMEN (PORCENTAJES Y RELATIVO)
# =============================================================================
def set_exact_volume(scalar):
    try:
        from pycaw.pycaw import AudioUtilities
        speakers = AudioUtilities.GetSpeakers()
        endpoint = getattr(speakers, "EndpointVolume", None) if speakers else None
        if endpoint:
            endpoint.SetMasterVolumeLevelScalar(scalar, None)
            pct = round(scalar * 100)
            return f"Volumen ajustado al {pct}%, Amo."
        return "No se encontró el dispositivo de audio, Amo."
    except Exception:
        return "No pude ajustar el volumen en este momento, Amo."

def adjust_volume_delta(delta):
    try:
        from pycaw.pycaw import AudioUtilities
        speakers = AudioUtilities.GetSpeakers()
        endpoint = getattr(speakers, "EndpointVolume", None) if speakers else None
        if endpoint:
            current = endpoint.GetMasterVolumeLevelScalar()
            new_vol = max(0.0, min(1.0, current + delta))
            endpoint.SetMasterVolumeLevelScalar(new_vol, None)
            pct = round(new_vol * 100)
            return f"Volumen ajustado al {pct}%, Amo."
        raise RuntimeError("No speakers endpoint")
    except Exception:
        import ctypes
        user32 = ctypes.windll.user32
        vk = 0xAF if delta > 0 else 0xAE
        for _ in range(8):
            user32.keybd_event(vk, 0, 0, 0)
            time.sleep(0.02)
            user32.keybd_event(vk, 0, 2, 0)
            time.sleep(0.02)
        return "Volumen ajustado, Amo."

def toggle_audio_mute():
    try:
        from pycaw.pycaw import AudioUtilities
        speakers = AudioUtilities.GetSpeakers()
        endpoint = getattr(speakers, "EndpointVolume", None) if speakers else None
        if endpoint:
            new_mute = not endpoint.GetMute()
            endpoint.SetMute(new_mute, None)
            return "Audio silenciado, Amo." if new_mute else "Audio reactivado, Amo."
        raise RuntimeError("No speakers endpoint")
    except Exception:
        pyautogui.press('volumemute')
        return "Audio silenciado, Amo."

def handle_volume_command(cmd):
    is_vol_context = any(w in cmd for w in ["volumen", "audio", "sonido"])
    
    # 1. Porcentaje explícito: "sube el volumen al 100%", "baja el volumen al 50%", "volumen al 30", "pon el volumen en 80"
    match = re.search(r'(\d{1,3})\s*(%|por ciento)?', cmd)
    if match and is_vol_context:
        val = int(match.group(1))
        if 0 <= val <= 100:
            return set_exact_volume(val / 100.0)

    # 2. Máximo / Mínimo
    if any(w in cmd for w in ["al maximo", "al máximo", "todo el volumen", "volumen maximo", "volumen máximo"]):
        return set_exact_volume(1.0)
    if any(w in cmd for w in ["al minimo", "al mínimo", "volumen minimo", "volumen mínimo", "sin volumen"]):
        return set_exact_volume(0.0)

    # 3. Subir volumen
    if (is_vol_context and any(w in cmd for w in ["sube", "subir", "mas", "más", "aumenta", "aumentar", "alto"])) or \
       cmd in ["sube volumen", "sube el volumen", "mas volumen", "más volumen", "aumenta volumen", "aumenta el volumen", "subelo", "súbelo"]:
        return adjust_volume_delta(0.15)

    # 4. Bajar volumen
    if (is_vol_context and any(w in cmd for w in ["baja", "bajar", "menos", "disminuye", "disminuir", "bajo"])) or \
       cmd in ["baja volumen", "baja el volumen", "menos volumen", "disminuye volumen", "disminuye el volumen", "bájalo", "bajalo"]:
        return adjust_volume_delta(-0.15)

    # 5. Silenciar / Mutear
    if any(w in cmd for w in ["silenciar", "mutea", "ponte en mudo", "modo mudo", "reactiva el audio", "desmutea", "quita el silencio", "desmutear"]):
        return toggle_audio_mute()

    return None

# =============================================================================
# CAPTURA DE PANTALLA 100% EN SEGUNDO PLANO (SIN CONSOLAS NI INTERRUPCIONES)
# =============================================================================
def take_screenshot():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = os.path.join(SCREENSHOT_DIR, f"captura_{timestamp}.png")
    
    # 1. PIL ImageGrab / PyAutoGUI en memoria pura (0 ventanas, 0 consolas)
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab(all_screens=True)
        if img:
            img.save(path)
            if os.path.exists(path) and os.path.getsize(path) > 0:
                return path
    except Exception:
        pass

    try:
        img = pyautogui.screenshot()
        if img:
            img.save(path)
            if os.path.exists(path) and os.path.getsize(path) > 0:
                return path
    except Exception:
        pass

    # 2. Fallback con PowerShell oculto sin crear ninguna ventana visible
    ps_cmd = (
        "[void][System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms'); "
        "[void][System.Reflection.Assembly]::LoadWithPartialName('System.Drawing'); "
        "$bounds = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds; "
        "$bmp = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height; "
        "$g = [System.Drawing.Graphics]::FromImage($bmp); "
        "$g.CopyFromScreen($bounds.Location, [System.Drawing.Point]::Empty, $bounds.Size); "
        f"$bmp.Save('{path}', [System.Drawing.Imaging.ImageFormat]::Png); "
        "$g.Dispose(); $bmp.Dispose();"
    )
    try:
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0  # SW_HIDE
        subprocess.run(
            ["powershell", "-WindowStyle", "Hidden", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
            startupinfo=si,
            creationflags=CREATE_NO_WINDOW,
            timeout=8,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass

    return path

# =============================================================================
# MAPEO EXACTO DE APLICACIONES EN EL PC DEL USUARIO
# =============================================================================
APPS = {
    # Antigravity IDE (Estrictamente diferenciado de Visual Studio Code)
    "antigravity": {
        "path": r"C:\Users\Bienvenido\AppData\Local\Programs\Antigravity IDE\Antigravity IDE.exe",
        "process": "Antigravity IDE.exe",
        "name": "Antigravity IDE"
    },
    "antigravity ide": {
        "path": r"C:\Users\Bienvenido\AppData\Local\Programs\Antigravity IDE\Antigravity IDE.exe",
        "process": "Antigravity IDE.exe",
        "name": "Antigravity IDE"
    },
    "antigravityide": {
        "path": r"C:\Users\Bienvenido\AppData\Local\Programs\Antigravity IDE\Antigravity IDE.exe",
        "process": "Antigravity IDE.exe",
        "name": "Antigravity IDE"
    },
    "agy": {
        "path": r"C:\Users\Bienvenido\AppData\Local\Programs\Antigravity IDE\Antigravity IDE.exe",
        "process": "Antigravity IDE.exe",
        "name": "Antigravity IDE"
    },
    "ide": {
        "path": r"C:\Users\Bienvenido\AppData\Local\Programs\Antigravity IDE\Antigravity IDE.exe",
        "process": "Antigravity IDE.exe",
        "name": "Antigravity IDE"
    },

    # Visual Studio Code
    "visual studio code": {
        "path": r"C:\Users\Bienvenido\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "process": "Code.exe",
        "name": "Visual Studio Code"
    },
    "visual studio": {
        "path": r"C:\Users\Bienvenido\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "process": "Code.exe",
        "name": "Visual Studio Code"
    },
    "vs code": {
        "path": r"C:\Users\Bienvenido\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "process": "Code.exe",
        "name": "Visual Studio Code"
    },
    "vscode": {
        "path": r"C:\Users\Bienvenido\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "process": "Code.exe",
        "name": "Visual Studio Code"
    },
    "code": {
        "path": r"C:\Users\Bienvenido\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "process": "Code.exe",
        "name": "Visual Studio Code"
    },
    "visual": {
        "path": r"C:\Users\Bienvenido\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "process": "Code.exe",
        "name": "Visual Studio Code"
    },

    # CapCut
    "capcut": {
        "path": r"C:\Users\Bienvenido\AppData\Local\CapCut\Apps\CapCut.exe",
        "process": "CapCut.exe",
        "name": "CapCut"
    },
    "cap cut": {
        "path": r"C:\Users\Bienvenido\AppData\Local\CapCut\Apps\CapCut.exe",
        "process": "CapCut.exe",
        "name": "CapCut"
    },

    # NetBeans
    "netbeans": {
        "path": r"C:\Users\Bienvenido\netbeans\bin\netbeans64.exe",
        "process": "netbeans64.exe",
        "name": "NetBeans"
    },
    "net beans": {
        "path": r"C:\Users\Bienvenido\netbeans\bin\netbeans64.exe",
        "process": "netbeans64.exe",
        "name": "NetBeans"
    },

    # Docker Desktop
    "docker": {
        "path": r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
        "process": "Docker Desktop.exe",
        "name": "Docker Desktop"
    },
    "docker desktop": {
        "path": r"C:\Program Files\Docker\Docker\Docker Desktop.exe",
        "process": "Docker Desktop.exe",
        "name": "Docker Desktop"
    },

    # Navegadores
    "brave": {
        "path": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        "process": "brave.exe",
        "name": "Brave Browser"
    },
    "brave browser": {
        "path": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        "process": "brave.exe",
        "name": "Brave Browser"
    },
    "chrome": {
        "path": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "process": "chrome.exe",
        "name": "Google Chrome"
    },
    "google chrome": {
        "path": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "process": "chrome.exe",
        "name": "Google Chrome"
    },
    "edge": {
        "path": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "process": "msedge.exe",
        "name": "Microsoft Edge"
    },
    "microsoft edge": {
        "path": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "process": "msedge.exe",
        "name": "Microsoft Edge"
    },

    # Microsoft Office
    "word": {
        "path": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        "process": "WINWORD.EXE",
        "name": "Microsoft Word"
    },
    "microsoft word": {
        "path": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        "process": "WINWORD.EXE",
        "name": "Microsoft Word"
    },
    "excel": {
        "path": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
        "process": "EXCEL.EXE",
        "name": "Microsoft Excel"
    },
    "microsoft excel": {
        "path": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
        "process": "EXCEL.EXE",
        "name": "Microsoft Excel"
    },
    "powerpoint": {
        "path": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
        "process": "POWERPNT.EXE",
        "name": "PowerPoint"
    },
    "power point": {
        "path": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
        "process": "POWERPNT.EXE",
        "name": "PowerPoint"
    },
    "microsoft powerpoint": {
        "path": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
        "process": "POWERPNT.EXE",
        "name": "PowerPoint"
    },

    # Herramientas
    "airdroid": {
        "path": r"C:\Program Files (x86)\AirDroid\AirDroid.exe",
        "process": "AirDroid.exe",
        "name": "AirDroid"
    },
    "air droid": {
        "path": r"C:\Program Files (x86)\AirDroid\AirDroid.exe",
        "process": "AirDroid.exe",
        "name": "AirDroid"
    },
    "airdroid cast": {
        "path": r"C:\Users\Bienvenido\AppData\Local\AirDroidCast\AirDroidCast.exe",
        "process": "AirDroidCast.exe",
        "name": "AirDroid Cast"
    },
    "air droid cast": {
        "path": r"C:\Users\Bienvenido\AppData\Local\AirDroidCast\AirDroidCast.exe",
        "process": "AirDroidCast.exe",
        "name": "AirDroid Cast"
    },
    "free download manager": {
        "path": r"C:\Program Files\Softdeluxe\Free Download Manager\fdm.exe",
        "process": "fdm.exe",
        "name": "Free Download Manager"
    },
    "fdm": {
        "path": r"C:\Program Files\Softdeluxe\Free Download Manager\fdm.exe",
        "process": "fdm.exe",
        "name": "Free Download Manager"
    },
    "spotify": {
        "cmd": "start spotify:",
        "process": "Spotify.exe",
        "name": "Spotify"
    },
    "discord": {
        "cmd": "start discord:",
        "process": "Discord.exe",
        "name": "Discord"
    },
    "bloc de notas": {
        "cmd": "notepad",
        "process": "notepad.exe",
        "name": "Bloc de Notas"
    },
    "notepad": {
        "cmd": "notepad",
        "process": "notepad.exe",
        "name": "Bloc de Notas"
    },
    "calculadora": {
        "cmd": "calc",
        "process": "CalculatorApp.exe",
        "name": "Calculadora"
    },
    "explorador": {
        "cmd": "explorer",
        "process": "explorer.exe",
        "name": "Explorador de Archivos"
    },
    "proyectos dev": {
        "path": r"C:\Proyectos DEV_",
        "process": "explorer.exe",
        "name": "Carpeta Proyectos DEV_"
    },
    "proyectos dev_": {
        "path": r"C:\Proyectos DEV_",
        "process": "explorer.exe",
        "name": "Carpeta Proyectos DEV_"
    },
    "terminal": {
        "cmd": "start wt",
        "process": "WindowsTerminal.exe",
        "name": "Terminal"
    },
    "cmd": {
        "cmd": "start cmd",
        "process": "cmd.exe",
        "name": "Símbolo del Sistema"
    },
    "google": {
        "url": "https://www.google.com",
        "name": "Google"
    },
    "youtube": {
        "url": "https://www.youtube.com",
        "name": "YouTube"
    },
    "github": {
        "url": "https://www.github.com",
        "name": "GitHub"
    },
    "whatsapp": {
        "url": "https://web.whatsapp.com",
        "name": "WhatsApp Web"
    },
}

def resolve_app(query):
    if not query:
        return None
    q = query.lower().strip()
    for prefix in [
        "la aplicación ", "la aplicacion ", "el programa ", "el software ", 
        "la app de ", "el app de ", "la app ", "el app ", "la ventana de ", 
        "el navegador ", "la carpeta ", "carpeta ", "el ", "la ", "los ", "las "
    ]:
        if q.startswith(prefix):
            q = q[len(prefix):].strip()
            
    for suffix in [" por favor", " porfa", " ya", " ahora"]:
        if q.endswith(suffix):
            q = q[:-len(suffix)].strip()
            
    # 1. Coincidencia exacta con la clave
    for k, v in APPS.items():
        if q == k or q == k.replace(" ", ""):
            return v
            
    # 2. Desambiguación estricta de Antigravity vs Visual Studio
    if "antigravity" in q or "agy" in q:
        return APPS["antigravity"]
        
    if any(term in q for term in ["visual studio", "vs code", "vscode", "code"]):
        return APPS["visual studio code"]

    # 3. Coincidencia por subcadena ordenando por longitud descendente
    sorted_keys = sorted(APPS.keys(), key=lambda x: len(x), reverse=True)
    for k in sorted_keys:
        if k in q or q in k:
            return APPS[k]
            
    return None

def launch_app(query):
    app = resolve_app(query)
    if not app:
        return False, query
    try:
        if "url" in app:
            webbrowser.open(app["url"])
            return True, app["name"]
        elif "path" in app and os.path.exists(app["path"]):
            try:
                os.startfile(app["path"])
            except Exception:
                subprocess.Popen(f'"{app["path"]}"', shell=True, creationflags=CREATE_NO_WINDOW)
            return True, app["name"]
        elif "cmd" in app:
            subprocess.Popen(app["cmd"], shell=True, creationflags=CREATE_NO_WINDOW)
            return True, app["name"]
    except Exception as e:
        print(f"[LAUNCH ERROR] {e}")
    return False, app.get("name", query)

def close_app(query):
    app = resolve_app(query)
    proc_name = None
    app_name = None
    
    if app:
        proc_name = app.get("process")
        app_name = app.get("name")
    else:
        clean = query.lower().strip()
        for p in ["la aplicacion ", "la aplicación ", "el programa ", "la app ", "el ", "la "]:
            if clean.startswith(p):
                clean = clean[len(p):].strip()
        proc_name = clean if clean.endswith(".exe") else f"{clean}.exe"
        app_name = query
        
    if proc_name:
        try:
            subprocess.run(
                f'taskkill /IM "{proc_name}" /F',
                shell=True,
                creationflags=CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            for proc in psutil.process_iter(['name', 'pid']):
                try:
                    if proc.info['name'] and proc.info['name'].lower() == proc_name.lower():
                        proc.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            return True, app_name
        except Exception as e:
            print(f"[CLOSE ERROR] {e}")
            return False, app_name
            
    return False, app_name

def play_song_spotify(song_query):
    try:
        subprocess.Popen(f'start spotify:search:"{song_query}"', shell=True, creationflags=CREATE_NO_WINDOW)
        def _trigger_playback():
            time.sleep(2.0)
            pyautogui.press('enter')
            time.sleep(0.6)
            pyautogui.press('space')
        threading.Thread(target=_trigger_playback, daemon=True).start()
    except Exception as e:
        print(f"[SPOTIFY ERROR] {e}")

# =============================================================================
# SERVICIOS: CLIMA Y PRONÓSTICO PARA MAÑANA
# =============================================================================
def get_weather(city=None, is_tomorrow=False):
    if not city:
        city = str(config.get("default_city", "Sincelejo"))
    try:
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=es"
        geo_resp = requests.get(geo_url, timeout=8).json()
        if "results" not in geo_resp:
            return f"Disculpa Amo, no encontré datos para '{city}'."
        lat = geo_resp["results"][0]["latitude"]
        lon = geo_resp["results"][0]["longitude"]
        place_name = geo_resp["results"][0]["name"]

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            f"&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weathercode"
            f"&current_weather=true&timezone=auto"
        )
        weather_resp = requests.get(weather_url, timeout=8).json()

        weather_codes = {
            0: "cielo despejado", 1: "mayormente soleado", 2: "parcialmente nublado", 3: "nublado",
            45: "niebla", 48: "niebla con escarcha", 51: "llovizna ligera", 53: "llovizna moderada",
            55: "llovizna densa", 61: "lluvia ligera", 63: "lluvia moderada", 65: "lluvia fuerte",
            80: "chubascos dispersos", 81: "chubascos moderados", 82: "chubascos violentos",
            95: "tormenta eléctrica", 96: "tormenta con granizo", 99: "tormenta eléctrica fuerte"
        }

        if is_tomorrow and "daily" in weather_resp:
            daily = weather_resp["daily"]
            t_max = daily["temperature_2m_max"][1]
            t_min = daily["temperature_2m_min"][1]
            rain_prob = daily["precipitation_probability_max"][1]
            code = daily["weathercode"][1]
            desc = weather_codes.get(code, "tiempo variable")
            return f"El pronóstico para mañana en {place_name} indica una máxima de {t_max}°C, mínima de {t_min}°C, {desc} y un {rain_prob}% de probabilidad de lluvia, Amo."
        else:
            current = weather_resp["current_weather"]
            temp = current["temperature"]
            wind = current["windspeed"]
            code = current.get("weathercode", 0)
            desc = weather_codes.get(code, "tiempo agradable")
            return f"El clima actual en {place_name} es de {temp}°C, {desc} y viento a {wind} km/h, Amo."
    except Exception as e:
        return f"No pude consultar el clima en este momento, Amo. Error: {e}"

def get_news():
    try:
        url = "https://feeds.bbci.co.uk/mundo/rss.xml"
        resp = requests.get(url, timeout=8)
        root = ET.fromstring(resp.content)
        headlines = []
        for item in root.findall(".//item")[:4]:
            t = item.find("title")
            if t is not None and t.text:
                headlines.append(t.text.strip())
        if not headlines:
            return "No encontré noticias destacadas en este momento, Amo."
        return "Titulares de BBC Mundo, Amo: " + ". ".join(headlines)
    except Exception as e:
        return f"Disculpa Amo, no pude obtener las noticias. Error: {e}"

def get_system_info():
    try:
        battery = psutil.sensors_battery()
        cpu = psutil.cpu_percent(interval=0.5)
        ram = psutil.virtual_memory().percent
        parts = [f"Uso de CPU al {cpu}%", f"Memoria RAM al {ram}%"]
        if battery:
            estado = "conectada a la corriente" if battery.power_plugged else "en batería"
            parts.append(f"batería al {battery.percent}% ({estado})")
        return ". ".join(parts) + ", Amo."
    except Exception as e:
        return f"Error al consultar el sistema, Amo: {e}"

# =============================================================================
# CONSULTA A OLLAMA (TRATO "AMO" Y CONTEXTO RAG)
# =============================================================================
conversation_history = []

def query_ollama(prompt):
    global conversation_history
    model = str(config.get("model", "gemma4:31b-cloud"))
    
    memory_text = ""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                memory_text = f.read().strip()
        except:
            pass

    now = datetime.datetime.now()
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dia = dias[now.weekday()]
    fecha = now.strftime("%d/%m/%Y")
    hora = now.strftime("%I:%M %p")

    system_prompt = (
        "Eres DAEMON, el leal, super inteligente, divertido y eficiente asistente personal del Amo. "
        "Dirígete a tu creador SIEMPRE y ÚNICAMENTE como 'Amo' (nunca uses otros nombres ni repitas 'Amo Amo'). "
        f"Fecha y hora del sistema: {dia} {fecha}, {hora}. "
        f"Ciudad base: {config.get('default_city', 'Sincelejo')}. "
        "Responde siempre en español natural, conciso, directo e inteligente (máximo 2 a 3 oraciones salvo explicaciones complejas). "
        "Si te pregunta sobre personas, ciencia, historia o conceptos (como Gustavo Petro, Nikola Tesla o la gravedad), responde con conocimiento enciclopédico claro y preciso."
    )

    conversation_history.append({"role": "user", "content": prompt})
    if len(conversation_history) > 10:
        conversation_history = conversation_history[-10:]

    messages = [{"role": "system", "content": system_prompt}] + list(conversation_history)

    if memory_text:
        last_msg = messages[-1]["content"]
        messages[-1] = {
            "role": "user",
            "content": f"{last_msg}\n\n[MEMORIA PERMANENTE DEL AMO:\n{memory_text}]"
        }

    try:
        resp = requests.post(
            "http://localhost:11434/api/chat",
            json={"model": model, "messages": messages, "stream": False},
            timeout=50
        )
        if resp.status_code == 200:
            data = resp.json()
            answer = data.get("message", {}).get("content", "Disculpa Amo, no pude procesar la respuesta.")
            conversation_history.append({"role": "assistant", "content": answer})
            return answer
        else:
            return f"Ollama devolvió código: {resp.status_code}, Amo. Comprueba el modelo '{model}'."
    except requests.ConnectionError:
        ensure_ollama_running()
        return "Ollama se está iniciando en segundo plano, Amo. Por favor intenta de nuevo en unos segundos."
    except Exception as e:
        return f"Error al procesar con IA, Amo: {e}"

# =============================================================================
# ENRUTADOR MAESTRO DE COMANDOS
# =============================================================================
def process_command(cmd_raw):
    if not cmd_raw:
        return None, ""
    
    cmd = cmd_raw.lower().strip()

    # --- 1. APAGAR DAEMON ---
    shutdown_triggers = [
        "apagar daemon", "cerrar daemon", "adios daemon", "adiós daemon",
        "desactivar", "apagate", "apágate", "apaga el sistema", "salir", "sal de aqui", "cierrate", "ciérrate"
    ]
    if any(w in cmd for w in shutdown_triggers):
        frases = [
            "Listo Amo, me apago. Que le vaya excelente.",
            "Entendido Amo. Apagando sistemas. Nos vemos pronto.",
            "Ok Amo, me retiro. Cualquier cosa aquí estoy.",
        ]
        return "EXIT", random.choice(frases)

    # --- 2. PAUSAR DAEMON ---
    if cmd in ["pausa", "pausate", "paúsate", "silencio", "duerme", "modo espera", "pausa a daemon"]:
        frases = [
            "Listo Amo, me quedo en silencio. Haga clic en mi interfaz para despertar.",
            "Modo silencioso activado, Amo. Estoy aquí por si acaso.",
            "En pausa, Amo. Un toque en mi icono y vuelvo.",
        ]
        return "PAUSE", random.choice(frases)

    # --- 3. DESPERTAR ---
    if any(w in cmd for w in ["despertar", "despierta", "activar", "activa"]):
        frases = [
            "Ya estoy de vuelta, Amo. ¿Qué necesita?",
            "Aquí reportándome, Amo. Dígame.",
            "Listo y activo, Amo. A sus órdenes.",
        ]
        return "WAKE", random.choice(frases)

    # --- 4. CONTROL DE VOLUMEN (EXACTO Y RELATIVO) ---
    vol_res = handle_volume_command(cmd)
    if vol_res:
        return "ACTION", vol_res

    # --- 5. BÚSQUEDA EN INCÓGNITO (ESTRICTO) ---
    incognito_triggers = ["en anonimo", "en anónimo", "en incognito", "en incógnito", "modo incognito", "modo incógnito", "pestaña privada", "ventana privada"]
    if any(t in cmd for t in incognito_triggers):
        query = cmd
        for w in ["busca", "buscar", "en google", "en internet", "abre"]:
            query = query.replace(w, "")
        for t in incognito_triggers:
            query = query.replace(t, "")
        query = query.strip()
        if query:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            subprocess.Popen(f'start chrome --incognito "{url}"', shell=True, creationflags=CREATE_NO_WINDOW)
            return "ACTION", f"Buscando '{query}' en modo incógnito de Google Chrome, Amo."
        else:
            subprocess.Popen('start chrome --incognito', shell=True, creationflags=CREATE_NO_WINDOW)
            return "ACTION", "Abriendo ventana privada en incógnito, Amo."

    # --- 6. TRADUCCIÓN INTELIGENTE ---
    if any(w in cmd for w in ["traduce", "traducir", "cómo se dice", "como se dice"]):
        clipboard_text = ""
        try:
            clipboard_text = pyperclip.paste().strip()
        except:
            pass

        target_lang = "inglés" if ("ingles" in cmd or "inglés" in cmd) else "español" if ("español" in cmd or "espanol" in cmd) else "el idioma solicitado"
        
        extracted = ""
        for marker in ["traduce a ingles ", "traduce al ingles ", "traduce al inglés ", "traduce a inglés ", "traduce a español ", "traduce al español ", "traduce ", "traducir ", "cómo se dice ", "como se dice "]:
            if marker in cmd:
                extracted = cmd_raw[cmd.find(marker) + len(marker):].strip()
                break

        for aux in ["a ingles", "al ingles", "al inglés", "a inglés", "a español", "al español", "en ingles", "en inglés", "en español"]:
            if extracted.lower().startswith(aux):
                extracted = extracted[len(aux):].strip(": ").strip()
            if extracted.lower().endswith(aux):
                extracted = extracted[:-len(aux)].strip(": ").strip()

        if extracted and extracted not in ["esto", "el texto"]:
            prompt_trad = f"Traduce el siguiente texto al {target_lang}. Proporciona únicamente la traducción de forma directa y natural, sin introducciones:\n\n'{extracted}'"
            return "AI", query_ollama(prompt_trad)
        elif clipboard_text:
            prompt_trad = f"Traduce el siguiente texto al {target_lang}. Proporciona únicamente la traducción directa:\n\n'{clipboard_text}'"
            return "AI", query_ollama(prompt_trad)
        else:
            return "ACTION", f"Por favor dígame qué texto desea que traduzca al {target_lang}, Amo, o cópielo con Control C."

    # --- 7. MÚSICA Y SPOTIFY ---
    if any(w in cmd for w in ["pausa la musica", "pausar musica", "pausa la cancion", "pausa la canción", "deten la musica", "detener musica", "pausar spotify", "detén la música"]):
        pyautogui.press('playpause')
        return "ACTION", "Música pausada, Amo."

    if any(w in cmd for w in ["dale play", "reanuda la musica", "continua la musica", "pon musica", "reproduce la musica", "reproducir musica", "ponle play", "reproduce"]):
        if cmd == "reproduce" or "musica" in cmd or "música" in cmd:
            pyautogui.press('playpause')
            return "ACTION", "Reanudando reproducción, Amo."

    if any(w in cmd for w in ["siguiente cancion", "siguiente canción", "pasa la cancion", "cambia de cancion", "pon otra", "siguiente"]):
        pyautogui.press('nexttrack')
        return "ACTION", "Siguiente canción, Amo."

    if any(w in cmd for w in ["anterior cancion", "anterior canción", "cancion anterior", "regresa la cancion", "pon la anterior", "anterior"]):
        pyautogui.press('prevtrack')
        return "ACTION", "Canción anterior, Amo."

    music_verbs = ["reproduce la cancion ", "reproduce la canción ", "reproduce ", "pon la cancion ", "pon la canción ", "pon musica de ", "pon música de ", "toca la cancion ", "toca ", "pon "]
    for mv in music_verbs:
        if cmd.startswith(mv):
            song_to_play = cmd_raw[len(mv):].strip()
            is_yt = "en youtube" in song_to_play.lower()
            song_clean = song_to_play.lower().replace("en spotify", "").replace("en youtube", "").replace("de ", "").strip()
            if song_clean:
                if is_yt:
                    webbrowser.open(f"https://www.youtube.com/results?search_query={song_clean.replace(' ', '+')}")
                    return "ACTION", f"Reproduciendo '{song_clean}' en YouTube, Amo."
                else:
                    play_song_spotify(song_clean)
                    return "ACTION", f"Reproduciendo '{song_clean}' en Spotify, Amo."

    # --- 8. CERRAR APLICACIONES ---
    close_triggers = ["cierra ", "cerrar ", "apaga ", "mata ", "termina ", "quita "]
    for ct in close_triggers:
        if cmd.startswith(ct):
            app_target = cmd[len(ct):].strip()
            ok, name = close_app(app_target)
            return "ACTION", f"Listo Amo, he cerrado {name}."

    # --- 9. ABRIR APLICACIONES DEL SISTEMA ---
    if cmd in ["google", "abre google", "abrir google", "google normal"]:
        subprocess.Popen('start chrome "https://www.google.com"', shell=True, creationflags=CREATE_NO_WINDOW)
        return "ACTION", "Abriendo Google en modo normal, Amo."

    clean_cmd = cmd.strip()
    app_res = resolve_app(clean_cmd)
    if app_res:
        ok, name = launch_app(clean_cmd)
        return "ACTION", f"{name} iniciado, Amo."

    open_triggers = ["abre ", "abrir ", "inicia ", "iniciar ", "ejecuta ", "lanza ", "abreme "]
    for ot in open_triggers:
        if cmd.startswith(ot):
            target = cmd[len(ot):].strip()
            app_res = resolve_app(target)
            if app_res:
                ok, name = launch_app(target)
                return "ACTION", f"Abriendo {name}, Amo."
            elif "." in target or "http" in target:
                url = target if target.startswith("http") else f"https://{target}"
                webbrowser.open(url)
                return "ACTION", f"Abriendo {target}, Amo."
            else:
                try:
                    subprocess.Popen(f'start "" "{target}"', shell=True, creationflags=CREATE_NO_WINDOW)
                    return "ACTION", f"Iniciando {target}, Amo."
                except:
                    return "ACTION", f"No encontré esa aplicación, Amo."

    # --- 10. BÚSQUEDA GENERAL EN GOOGLE (MODO NORMAL) ---
    search_triggers = ["busca ", "buscar ", "investiga ", "googlea "]
    for st in search_triggers:
        if cmd.startswith(st):
            query = cmd.split(st, 1)[1].replace("en google", "").replace("sobre", "").strip()
            if "en youtube" in query:
                q = query.replace("en youtube", "").strip()
                webbrowser.open(f"https://www.youtube.com/results?search_query={q.replace(' ', '+')}")
                return "ACTION", f"Buscando {q} en YouTube, Amo."
            elif query:
                subprocess.Popen(f'start chrome "https://www.google.com/search?q={query.replace(" ", "+")}"', shell=True, creationflags=CREATE_NO_WINDOW)
                return "ACTION", f"Buscando '{query}' en Google, Amo."

    # --- 11. CAPTURA DE PANTALLA EN SEGUNDO PLANO ---
    if any(w in cmd for w in ["captura", "screenshot", "pantallazo", "foto de pantalla", "toma una captura"]):
        time.sleep(0.4)
        path = take_screenshot()
        return "ACTION", "Captura de pantalla realizada en segundo plano y guardada en su carpeta de imágenes, Amo."

    # --- 12. CLIMA Y PRONÓSTICO (HOY Y MAÑANA) ---
    if any(w in cmd for w in ["clima", "tiempo", "temperatura", "pronóstico", "pronostico", "lloverá", "llovera", "va a llover"]):
        city = str(config.get("default_city", "Sincelejo"))
        for trig in [" en ", " de ", " para "]:
            if trig in cmd:
                city = cmd.split(trig, 1)[1].strip()
                break
        is_tomorrow = any(w in cmd for w in ["mañana", "manana", "próximos días", "proximos dias"])
        return "ACTION", get_weather(city, is_tomorrow=is_tomorrow)

    # --- 13. ESCRIBIR TEXTO ---
    type_triggers = ["escribe ", "escribir ", "teclea ", "tipea ", "redacta ", "pon "]
    for trigger in type_triggers:
        if cmd.startswith(trigger):
            text_to_type = cmd_raw[len(trigger):].strip()
            if text_to_type:
                speak("Escribiendo texto, Amo. Sitúe su cursor donde desee el texto.")
                threading.Thread(target=lambda: (time.sleep(2.0), type_text(text_to_type)), daemon=True).start()
                return "ACTION", "Listo Amo, escribiendo el texto."

    # --- 14. LEER TEXTO DEL PORTAPAPELES ---
    if any(w in cmd for w in ["lee esto", "lee el texto", "lee lo seleccionado", "leeme esto", "léeme esto", "lee la selección", "léelo"]):
        try:
            copied = pyperclip.paste().strip()
            if copied:
                return "ACTION", f"El texto dice, Amo: {copied}"
            else:
                return "ACTION", "El portapapeles está vacío, Amo. Sombrea el texto y presiona Control C."
        except:
            return "ACTION", "Hubo un error al acceder al portapapeles, Amo."

    # --- 15. MEMORIA PERMANENTE RAG ---
    memory_triggers = ["recuerda que ", "recuérdame que ", "anota que ", "guarda que ", "recuerdame que "]
    for mt in memory_triggers:
        if mt in cmd:
            note = cmd.split(mt, 1)[1].strip()
            if note and not note.startswith("la ") and not note.startswith("el "):
                try:
                    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
                        f.write(f"- {note}\n")
                    return "ACTION", "Listo Amo, lo he registrado permanentemente en mi memoria."
                except:
                    return "ACTION", "Hubo un error al guardar ese recuerdo, Amo."

    if any(w in cmd for w in ["qué recuerdas", "que recuerdas", "mis notas", "ver memoria"]):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content:
                    return "ACTION", f"Mis registros en memoria dicen lo siguiente, Amo:\n{content}"
            except:
                pass
        return "ACTION", "Aún no tengo ninguna nota registrada en mi memoria permanente, Amo."

    # --- 16. HORA Y FECHA ---
    if any(w in cmd for w in ["hora", "qué hora", "que hora", "fecha"]):
        now = datetime.datetime.now().strftime("%I:%M %p")
        return "ACTION", f"Son las {now}, Amo."

    # --- 17. NOTICIAS Y SISTEMA ---
    if any(w in cmd for w in ["noticias", "noticia", "titulares"]):
        return "ACTION", get_news()

    if any(w in cmd for w in ["sistema", "información del sistema", "informacion del sistema", "batería", "bateria", "cpu", "ram"]):
        return "ACTION", get_system_info()

    if any(w in cmd for w in ["chiste", "cuéntame un chiste", "dime un chiste"]):
        try:
            return "ACTION", pyjokes.get_joke(language="es")
        except:
            return "ACTION", "¿Qué le dice un bit a otro? Nos vemos en el bus, Amo."

    if any(w in cmd for w in ["quién soy", "quien soy", "sobre mí", "sobre mi", "quién es mi desarrollador", "quien te creo", "quién te creó"]):
        return "ACTION", (
            "Usted es mi Amo, creador y desarrollador. "
            "Me programó desde cero y configuró mis funciones para asistirle en todo momento."
        )

    # --- 18. PREGUNTAS DE CONOCIMIENTO (GUSTAVO PETRO, NIKOLA TESLA, GRAVEDAD) ---
    if any(cmd.startswith(w) for w in ["quién es ", "quien es ", "qué es ", "que es ", "cuéntame de ", "cómo funciona ", "explicame ", "explícame "]):
        reply = query_ollama(cmd_raw)
        return "AI", reply

    # --- 19. CONSULTA GENERAL CON IA ---
    reply = query_ollama(cmd_raw)
    return "AI", reply

# =============================================================================
# NEBULOSA GALÁCTICA 3D: CONSTANTES Y HELPERS
# =============================================================================
SIZE = 100            # Lado del lienzo en px (100 = widget; 740 = tamaño del logo)
N_RING = 1400         # Partículas del anillo galáctico
N_CORE_LAT = 28       # Rejilla del núcleo: latitudes
N_CORE_LON = 36       # Rejilla del núcleo: longitudes (~1000 puntos)
PERSP_F = 10.0        # Distancia de perspectiva (mayor = menos distorsión)
TILT_DEG = 20         # Inclinación fija en el eje X
GRAD_LEVELS = 32      # Niveles de gradiente de color precalculados
DEPTH_LEVELS = 8      # Niveles de brillo por profundidad
DEEP = (10, 15, 42)   # #0a0f2a azul marino (núcleo)

SPIN_SPEED = {"idle": 0.6, "listening": 1.9, "thinking": 3.6, "paused": 0.12}  # grados/frame

# Paletas: de arriba (g=0) a abajo (g=1)
PALETTES = {
    "spectral": ["#00f5ff", "#d800ff", "#ff8800"],
    "cyan":     ["#e0ffff", "#00f5ff", "#005588"],
    "amber":    ["#fff4cc", "#ffaa00", "#884400"],
    "green":    ["#d4ffe6", "#00ff88", "#006633"],
    "red":      ["#ffd6dc", "#ff2244", "#880818"],
    "purple":   ["#f5d4ff", "#d800ff", "#5a0088"],
    "paused":   ["#883344", "#4a1525", "#240812"],
}

def _hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def _rgb_hex(c):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(v))) for v in c)

def _mix(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))

def _ramp(stops, g):
    rgbs = [_hex_rgb(s) for s in stops]
    pos = g * (len(rgbs) - 1)
    i = min(int(pos), len(rgbs) - 2)
    return _mix(rgbs[i], rgbs[i + 1], pos - i)

def _build_lut(stops):
    """LUT[gradiente][profundidad] -> color hex. Evita calcular colores por frame."""
    lut = []
    for gi in range(GRAD_LEVELS):
        base = _ramp(stops, gi / (GRAD_LEVELS - 1))
        row = []
        for di in range(DEPTH_LEVELS):
            b = 0.25 + 0.75 * di / (DEPTH_LEVELS - 1)  # atrás = tenue, delante = brillante
            row.append(_rgb_hex([c * b for c in base]))
        lut.append(row)
    return lut

def _core_stops(ring_stops):
    s = ring_stops
    return [
        _rgb_hex(_mix(_hex_rgb(s[0]), DEEP, 0.8)),
        _rgb_hex(_mix(_hex_rgb(s[1]), DEEP, 0.8)),
        _rgb_hex(_mix(_hex_rgb(s[0]), (255, 255, 255), 0.6)),  # chispas brillantes
    ]

_LUT_CACHE = {}

def _get_luts(key):
    if key not in _LUT_CACHE:
        ring_stops = PALETTES[key]
        _LUT_CACHE[key] = (_build_lut(ring_stops), _build_lut(_core_stops(ring_stops)))
    return _LUT_CACHE[key]

_CLOUD = None

def _get_cloud():
    """Genera la nube de partículas una sola vez."""
    global _CLOUD
    if _CLOUD is not None:
        return _CLOUD
    rng = np.random.default_rng(77)

    # (a) Anillo galáctico con dispersión gaussiana en radio y altura
    th = rng.uniform(0, 2 * np.pi, N_RING)
    phi = np.clip(rng.normal(0, 0.22, N_RING), -0.6, 0.6)
    rr = 0.92 + rng.normal(0, 0.06, N_RING)
    ring = np.stack([rr * np.cos(phi) * np.cos(th),
                     rr * np.sin(phi),
                     rr * np.cos(phi) * np.sin(th)], axis=1)
    ring_g = np.clip(0.5 - 0.9 * np.sin(phi) + rng.normal(0, 0.08, N_RING), 0, 1)

    # (b) Núcleo esférico con textura de rejilla
    lat = np.arcsin(np.linspace(-0.92, 0.92, N_CORE_LAT))
    lon = np.linspace(0, 2 * np.pi, N_CORE_LON, endpoint=False)
    LA, LO = np.meshgrid(lat, lon, indexing="ij")
    LA, LO = LA.ravel(), LO.ravel()
    n_core = LA.size
    rc = 0.78
    core = np.stack([rc * np.cos(LA) * np.cos(LO),
                     rc * np.sin(LA),
                     rc * np.cos(LA) * np.sin(LO)], axis=1)
    core += rng.normal(0, 0.01, core.shape)
    core_g = rng.uniform(0, 0.45, n_core)
    sparks = rng.random(n_core) < 0.06
    core_g[sparks] = rng.uniform(0.95, 1.0, int(sparks.sum()))

    P = np.vstack([ring, core])
    G = np.concatenate([ring_g, core_g])
    theta = np.concatenate([th, np.zeros(n_core)])
    is_ring = np.r_[np.ones(N_RING, bool), np.zeros(n_core, bool)]
    size = rng.uniform(0.9, 1.7, len(P))
    rad = np.hypot(P[:, 0], P[:, 2])
    spiral_w = np.where(is_ring, np.clip((rad - 0.85) / 0.15, 0, 1), 0.0)

    _CLOUD = {
        "P": P, "G": G, "size": size, "theta": theta,
        "is_ring": is_ring, "is_ring_list": is_ring.tolist(),
        "spiral_w": spiral_w,
    }
    return _CLOUD

# =============================================================================
# WIDGET FLOTANTE ARC REACTOR (EL ÚNICO QUE APARECE AL INICIO)
# =============================================================================
class FloatingArcWidget:
    def __init__(self, master_app):
        self.master_app = master_app
        self.root = tk.Toplevel()
        self.root.title("DAEMON HUD")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.94)

        self.size = SIZE
        screen_w = self.root.winfo_screenwidth()
        self.root.geometry(f"{self.size}x{self.size}+{screen_w - 130}+40")
        self.bg_color = '#000001'
        self.root.configure(bg=self.bg_color)
        try:
            self.root.wm_attributes("-transparentcolor", self.bg_color)
        except Exception:
            pass

        self.canvas = tk.Canvas(
            self.root, width=self.size, height=self.size,
            bg=self.bg_color, highlightthickness=0, cursor="hand2"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.pulse_angle = 0
        self.is_listening = False
        self.is_paused = False
        self.is_thinking = False
        self.is_deaf_mode = False
        self._dragging = False
        self._offset_x = 0
        self._offset_y = 0
        self._press_time: float = 0.0

        self.blink_counter = 0

        self.root.bind('<ButtonPress-1>', self._on_press)
        self.root.bind('<B1-Motion>', self._on_drag)
        self.root.bind('<ButtonRelease-1>', self._on_release)
        self.root.bind('<Double-Button-1>', lambda e: self.show_home())
        self.root.bind('<Button-3>', self._show_context_menu)

        self.menu = tk.Menu(
            self.root, tearoff=0,
            bg='#121324', fg='#00d2ff',
            activebackground='#0055ff', activeforeground='white',
            font=('Segoe UI', 10, 'bold'), bd=1, relief='solid'
        )
        self.menu.add_command(label="🏠  Home / Pantalla Completa", command=self.show_home)
        self.menu.add_separator()
        self.menu.add_command(label="🎙️  Escuchar / Hablar", command=self.toggle_listen)
        self.menu.add_command(label="⏸️  Pausar / Silenciar", command=self.toggle_pause)
        self.menu.add_command(label="📸  Captura en Segundo Plano", command=self.cmd_screenshot)
        self.menu.add_command(label="⚙️  Configuración", command=self.show_config)
        self.menu.add_separator()
        self.menu.add_command(label="❌  Cerrar DAEMON", command=self.master_app.shutdown)

        self._draw_reactor()
        self._animate()

    def show_home(self):
        self.master_app.show_window("chat")

    def show_config(self):
        self.master_app.show_window("config")

    def _on_press(self, event):
        self._offset_x = event.x
        self._offset_y = event.y
        self._dragging = False
        self._press_time = time.time()

    def _on_drag(self, event):
        self._dragging = True
        x = self.root.winfo_pointerx() - self._offset_x
        y = self.root.winfo_pointery() - self._offset_y
        self.root.geometry(f"{self.size}x{self.size}+{x}+{y}")

    def _on_release(self, event):
        elapsed = time.time() - self._press_time
        if not self._dragging and elapsed < 0.35:
            self.toggle_listen()
        self._dragging = False

    def _show_context_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def toggle_listen(self):
        if self.is_listening:
            self.is_listening = False
            self.master_app.set_status("En espera")
            winsound.MessageBeep(winsound.MB_ICONHAND)
        else:
            self.is_listening = True
            self.is_paused = False
            self.master_app.set_status("Escuchando...")
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
            threading.Thread(target=self._listen_thread, daemon=True).start()

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        self.is_listening = False
        if self.is_paused:
            self.master_app.set_status("Pausado")
            speak("DAEMON en modo pausa, Amo.")
        else:
            self.master_app.set_status("Listo")
            speak("Reactivado, Amo. A sus órdenes.")

    def cmd_screenshot(self):
        time.sleep(0.2)
        take_screenshot()
        speak("Captura guardada en segundo plano, Amo.")
        self.master_app.add_chat_message("DAEMON", "📸 Captura guardada en segundo plano en Capturas DAEMON, Amo.")

    def _listen_thread(self):
        while self.is_listening and not self.is_paused:
            cmd = listen_audio()
            if cmd:
                if self.is_deaf_mode:
                    if any(w in cmd for w in ["eres inteligente", "despierta", "llega", "vuelve", "regresa"]):
                        self.is_deaf_mode = False
                        speak("Aquí estoy, Amo. A su disposición.")
                    continue
                
                if any(w in cmd for w in ["eres ciega", "eres sorda", "vete", "largate", "no escuches"]):
                    self.is_deaf_mode = True
                    speak("A la orden, Amo. Me desconecto.")
                    continue

                self.is_thinking = True
                self.master_app.add_chat_message("Tú", cmd)
                action_type, reply = process_command(cmd)
                self.is_thinking = False
                
                if action_type == "EXIT":
                    self.master_app.shutdown()
                    return
                elif action_type == "PAUSE":
                    self.toggle_pause()
                    return
                elif action_type == "WAKE":
                    self.is_paused = False
                
                if reply:
                    self.master_app.add_chat_message("DAEMON", reply)
                    speak(reply)
            time.sleep(0.1)

    def _draw_reactor(self):
        self.canvas.delete("all")
        cx = self.size // 2
        cy = self.size // 2

        custom_theme = str(config.get("neon_theme", "spectral")).lower()

        if self.is_paused:
            state_mode = 'paused'
        elif self.is_thinking:
            state_mode = 'thinking'
        elif self.is_listening:
            state_mode = 'listening'
        else:
            state_mode = 'idle'

        if any(w in custom_theme for w in ["reactor", "triangular", "triangulo"]):
            self._draw_classic_reactor(cx, cy, state_mode, custom_theme)
        else:
            self._draw_galactic_nebula(cx, cy, state_mode, custom_theme)

    def _draw_galactic_nebula(self, cx, cy, state_mode, custom_theme):
        cloud = _get_cloud()
        k = self.size / 100.0            # escala global: todo se multiplica por k
        R = 0.446 * self.size            # radio visible de la esfera (~89% del diámetro)
        t = self.pulse_angle
        self.blink_counter = (self.blink_counter + 1) % 180

        # 0. Zona de clic invisible (mantiene clic, arrastre y menú con transparentcolor)
        r_hit = R + 2 * k
        self.canvas.create_oval(cx - r_hit, cy - r_hit, cx + r_hit, cy + r_hit,
                                fill="#020308", stipple="gray25", outline="")

        # 1. Velocidad de giro según estado
        self._spin = (getattr(self, "_spin", 0.0) + SPIN_SPEED[state_mode]) % 360

        # 2. Deformaciones por estado (respiración en idle, ondas en listening)
        ring = cloud["is_ring"]
        radial = np.ones(len(cloud["P"]))
        if state_mode == "idle":
            radial[:] = 1 + 0.02 * math.sin(t * 0.05)
        elif state_mode == "listening":
            radial[ring] = 1 + 0.07 * np.sin(cloud["theta"][ring] * 4 - t * 0.25)
        P = cloud["P"] * np.column_stack([radial, np.ones_like(radial), radial])

        # 3. Rotación en Y (con espiral en el anillo exterior al pensar)
        ang = np.full(len(P), math.radians(self._spin))
        if state_mode == "thinking":
            ang = ang + cloud["spiral_w"] * (0.9 + 0.3 * math.sin(t * 0.05))
        c, s = np.cos(ang), np.sin(ang)
        x = P[:, 0] * c + P[:, 2] * s
        z = -P[:, 0] * s + P[:, 2] * c
        y = P[:, 1]

        # 4. Inclinación fija en X
        ct = math.cos(math.radians(TILT_DEG))
        st = math.sin(math.radians(TILT_DEG))
        y2 = y * ct - z * st
        z2 = y * st + z * ct

        # 5. Proyección en perspectiva (normalizada: el frente mide exactamente R)
        persp = (PERSP_F - 1.3) / (PERSP_F - z2)
        sx = (cx + x * R * persp).tolist()
        sy = (cy - y2 * R * persp).tolist()
        zn = np.clip((z2 + 1.3) / 2.6, 0, 1)  # 0 = atrás, 1 = delante

        # 6. Color y tamaño por partícula
        key = "paused" if state_mode == "paused" else next(
            (p for p in PALETTES if p != "paused" and p in custom_theme), "spectral")
        ring_lut, core_lut = _get_luts(key)

        gshift = 0.12 * math.sin(t * 0.07) if state_mode == "thinking" else 0.0
        g = np.clip(cloud["G"] + gshift, 0, 1)
        gi = np.rint(g * (GRAD_LEVELS - 1)).astype(int).tolist()
        di = np.rint(zn * (DEPTH_LEVELS - 1)).astype(int)
        if state_mode == "listening":
            di = np.minimum(di + 1, DEPTH_LEVELS - 1)  # brillo sube al escuchar
        di = di.tolist()

        size_px = cloud["size"] * k * (0.55 + 0.75 * zn)
        if state_mode == "listening":
            size_px = size_px * 1.1
        size_px = size_px.tolist()

        ring_flags = cloud["is_ring_list"]
        order = np.argsort(z2).tolist()  # painter's algorithm: fondo primero

        # 7. Dibujo
        for i in order:
            sz = size_px[i]
            if sz < 0.35:
                continue
            lut = ring_lut if ring_flags[i] else core_lut
            px, py = sx[i], sy[i]
            self.canvas.create_oval(px - sz, py - sz, px + sz, py + sz,
                                    fill=lut[gi[i]][di[i]], outline="")

        # 8. Ojos centrales (se conservan los estados de la app)
        lx, rx, ey = cx - 5.5 * k, cx + 5.5 * k, cy
        blinking = 175 <= self.blink_counter <= 179 and state_mode != "listening"
        if state_mode == "paused" or blinking:
            col = "#441525" if state_mode == "paused" else "#88aacc"
            for ex in (lx, rx):
                self.canvas.create_line(ex - 2 * k, ey, ex + 2 * k, ey,
                                        fill=col, width=max(1, k))
        else:
            if state_mode == "listening":
                r_e, outline = 2.4 * k, "#00f5ff"
            elif state_mode == "thinking":
                r_e, outline = (1.8 + 0.6 * math.sin(t * 0.3)) * k, "#d800ff"
            else:
                r_e, outline = 1.8 * k, "#77aaff"
            for ex in (lx, rx):
                self.canvas.create_oval(ex - r_e, ey - r_e, ex + r_e, ey + r_e,
                                        fill="#ffffff", outline=outline)

    def _draw_classic_reactor(self, cx, cy, state_mode, custom_theme):
        r_ring = 35
        
        if state_mode == 'paused':
            glow = '#440810'; base = '#d41133'; bright = '#ff2244'; core = '#ffd6dc'
        elif state_mode == 'thinking':
            glow = '#4a2500'; base = '#d47500'; bright = '#ffaa00'; core = '#fff2cc'
        elif state_mode == 'listening':
            glow = '#00381a'; base = '#00b359'; bright = '#00ff77'; core = '#dbffe8'
        else:
            if any(w in custom_theme for w in ["ambar", "ámbar", "amber", "oro"]):
                glow = '#4a2500'; base = '#d47500'; bright = '#ffaa00'; core = '#fff2cc'
            elif any(w in custom_theme for w in ["verde", "green"]):
                glow = '#00381a'; base = '#00b359'; bright = '#00ff77'; core = '#dbffe8'
            elif any(w in custom_theme for w in ["rojo", "red"]):
                glow = '#440810'; base = '#d41133'; bright = '#ff2244'; core = '#ffd6dc'
            elif any(w in custom_theme for w in ["purpura", "púrpura", "purple"]):
                glow = '#38004d'; base = '#9900cc'; bright = '#cc33ff'; core = '#f7e6ff'
            else:
                glow = '#002e4d'; base = '#0099dd'; bright = '#00d2ff'; core = '#e0f8ff'

        self.canvas.create_oval(cx - r_ring - 12, cy - r_ring - 12, cx + r_ring + 12, cy + r_ring + 12, fill='#070812', outline='')

        num_bars = 32
        for i in range(num_bars):
            ang = (i / num_bars) * (2 * math.pi) + math.radians(self.pulse_angle * 0.4)
            cos_a = math.cos(ang)
            sin_a = math.sin(ang)

            if state_mode == 'listening':
                h = 3 + int(9.0 * (math.sin(self.pulse_angle * 0.18 + i * 0.65) ** 2 * 0.6 + 
                                  math.cos(self.pulse_angle * 0.12 - i * 0.8) ** 2 * 0.4))
            elif state_mode == 'thinking':
                h = 3 + int(8.0 * (math.sin(self.pulse_angle * 0.3 + i * 0.75) ** 2))
            elif state_mode == 'paused':
                h = 2
            else:
                h = 2 + int(6.0 * (math.sin(self.pulse_angle * 0.08 + i * 0.45) ** 2))

            r_in = r_ring + 2
            r_out = r_in + h
            x1 = cx + int(r_in * cos_a)
            y1 = cy + int(r_in * sin_a)
            x2 = cx + int(r_out * cos_a)
            y2 = cy + int(r_out * sin_a)

            self.canvas.create_line(x1, y1, x2, y2, fill=glow, width=3.5)
            self.canvas.create_line(x1, y1, x2, y2, fill=bright, width=1.5)
            self.canvas.create_oval(x2 - 1, y2 - 1, x2 + 1, y2 + 1, fill=core, outline='')

        self.canvas.create_oval(cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring, outline=glow, width=5)
        self.canvas.create_oval(cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring, outline=bright, width=2, fill='#0b0d1b')
        self.canvas.create_oval(cx - r_ring, cy - r_ring, cx + r_ring, cy + r_ring, outline=core, width=0.8)

        r_mid = 26
        for j in range(3):
            arc_start = (self.pulse_angle * 1.4 + j * 120) % 360
            self.canvas.create_arc(
                cx - r_mid, cy - r_mid, cx + r_mid, cy + r_mid,
                start=arc_start, extent=45, style='arc', outline=glow, width=4.5
            )
            self.canvas.create_arc(
                cx - r_mid, cy - r_mid, cx + r_mid, cy + r_mid,
                start=arc_start, extent=45, style='arc', outline=bright, width=1.8
            )

        r_in_ring = 19
        self.canvas.create_oval(cx - r_in_ring, cy - r_in_ring, cx + r_in_ring, cy + r_in_ring, outline=glow, width=2.5)
        self.canvas.create_oval(cx - r_in_ring, cy - r_in_ring, cx + r_in_ring, cy + r_in_ring, outline=base, width=1)

        tr = 14
        pts = [
            cx, cy - tr,
            cx - int(tr * 0.866), cy + int(tr * 0.5),
            cx + int(tr * 0.866), cy + int(tr * 0.5)
        ]
        self.canvas.create_polygon(pts, outline=glow, fill='', width=4.5)
        self.canvas.create_polygon(pts, outline=bright, fill='', width=2)
        self.canvas.create_polygon(pts, outline=core, fill='', width=0.8)

        self.canvas.create_oval(cx - 5, cy + 0.5, cx + 5, cy + 10.5, fill=glow, outline='')
        self.canvas.create_oval(cx - 3.5, cy + 2, cx + 3.5, cy + 9, fill=bright, outline='')
        self.canvas.create_oval(cx - 1.5, cy + 4, cx + 1.5, cy + 7, fill=core, outline='')

        for k in range(4):
            k_ang = math.radians(-self.pulse_angle * 0.5 + k * 90)
            kx1 = cx + int((r_ring - 4) * math.cos(k_ang))
            ky1 = cy + int((r_ring - 4) * math.sin(k_ang))
            kx2 = cx + int((r_ring + 3) * math.cos(k_ang))
            ky2 = cy + int((r_ring + 3) * math.sin(k_ang))
            self.canvas.create_line(kx1, ky1, kx2, ky2, fill=core, width=1.5)

    def _animate(self):
        self.pulse_angle = (self.pulse_angle + 2) % 360
        self._draw_reactor()
        self.root.after(33, self._animate)  # ~30 FPS

# =============================================================================
# VENTANA PRINCIPAL HOME
# =============================================================================
class DaemonApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("D.A.E.M.O.N. - Asistente Personal con IA")
        self.geometry("1050x700")
        self.minsize(920, 620)
        self.configure(fg_color="#0c0d15")

        icon_file = get_resource_path("icon.ico")
        if os.path.exists(icon_file):
            try:
                self.iconbitmap(icon_file)
            except:
                pass

        self.protocol("WM_DELETE_WINDOW", self.minimize_to_widget)
        self.widget = FloatingArcWidget(self)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content_areas()

        self.show_view("chat")
        self.withdraw()  # Inicia oculto, solo el icono pequeño en pantalla

        self.after(1200, self._startup_greeting)

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#121320")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(6, weight=1)

        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=16, pady=(24, 16))

        logo_file = get_resource_path("daemon_logo.png")
        if os.path.exists(logo_file):
            try:
                pil_logo = Image.open(logo_file)
                self.sidebar_logo_img = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(38, 38))
                logo_img_lbl = ctk.CTkLabel(logo_frame, image=self.sidebar_logo_img, text="")
                logo_img_lbl.pack(side="left", padx=(0, 10))
            except Exception:
                pass

        header_text_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        header_text_frame.pack(side="left", fill="both", expand=True)

        title_lbl = ctk.CTkLabel(
            header_text_frame, text="⚡ D.A.E.M.O.N.",
            font=("Segoe UI", 18, "bold"), text_color="#00d2ff"
        )
        title_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            header_text_frame, text="Asistente de IA • v2.0 Pro",
            font=("Segoe UI", 10), text_color="#7b849b"
        )
        sub_lbl.pack(anchor="w")

        self.status_pill = ctk.CTkLabel(
            self.sidebar,
            text=f"● En línea | {config.get('model', 'gemma4:31b-cloud')}",
            font=("Segoe UI", 11, "bold"), text_color="#00ff88",
            fg_color="#182329", corner_radius=8, padx=8, pady=3
        )
        self.status_pill.pack(anchor="w", padx=16, pady=(0, 12))

        new_chat_btn = ctk.CTkButton(
            self.sidebar, text="＋ Nueva Conversación",
            font=("Segoe UI", 13, "bold"), fg_color="#1f2338",
            hover_color="#2b314d", text_color="#ffffff",
            height=38, corner_radius=8, command=self.clear_chat
        )
        new_chat_btn.pack(fill="x", padx=16, pady=(8, 20))

        self.nav_btns = {}
        nav_items = [
            ("chat", "💬  Home / Chat"),
            ("actions", "⚡  Acciones Rápidas"),
            ("memory", "🧠  Memoria RAG"),
            ("config", "⚙️  Configuración"),
        ]

        for view_key, label in nav_items:
            btn = ctk.CTkButton(
                self.sidebar, text=label,
                font=("Segoe UI", 13), fg_color="transparent",
                hover_color="#1c1f33", text_color="#c3cbe0",
                anchor="w", height=40, corner_radius=8,
                command=lambda vk=view_key: self.show_view(vk)
            )
            btn.pack(fill="x", padx=12, pady=3)
            self.nav_btns[view_key] = btn

        bottom_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom_frame.pack(side="bottom", fill="x", padx=16, pady=20)

        min_btn = ctk.CTkButton(
            bottom_frame, text="🗗  Ocultar a Icono Flotante",
            font=("Segoe UI", 12), fg_color="#1a1c2e",
            hover_color="#262942", text_color="#00d2ff",
            height=34, corner_radius=8, command=self.minimize_to_widget
        )
        min_btn.pack(fill="x", pady=(0, 10))

        self.user_tag = ctk.CTkLabel(
            bottom_frame,
            text="👤 Amo",
            font=("Segoe UI", 12, "bold"), text_color="#98a3c2"
        )
        self.user_tag.pack(anchor="w")

    def _build_content_areas(self):
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="#0c0d15")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.views = {}
        self.views["chat"] = self._create_chat_view()
        self.views["actions"] = self._create_actions_view()
        self.views["memory"] = self._create_memory_view()
        self.views["config"] = self._create_config_view()

    def _create_chat_view(self):
        view = ctk.CTkFrame(self.main_container, fg_color="transparent")

        header = ctk.CTkFrame(view, fg_color="#121320", height=60, corner_radius=0)
        header.pack(fill="x", side="top")
        
        hour = datetime.datetime.now().hour
        saludo = "Buenos días" if hour < 12 else "Buenas tardes" if hour < 19 else "Buenas noches"
        self.greeting_lbl = ctk.CTkLabel(
            header, text=f"{saludo}, Amo",
            font=("Segoe UI", 16, "bold"), text_color="#ffffff"
        )
        self.greeting_lbl.pack(side="left", padx=20, pady=15)

        self.status_text_lbl = ctk.CTkLabel(
            header, text="Listo para sus órdenes",
            font=("Segoe UI", 12), text_color="#00d2ff"
        )
        self.status_text_lbl.pack(side="right", padx=20, pady=15)

        chips_frame = ctk.CTkFrame(view, fg_color="transparent")
        chips_frame.pack(fill="x", padx=20, pady=(10, 5))

        chips = [
            ("⛅ Clima", "clima"),
            ("⛅ Mañana", "como estara el clima mañana"),
            ("🌐 Google", "abre google"),
            ("🎵 Spotify", "spotify"),
            ("🚀 Antigravity", "abre antigravity"),
            ("📸 Captura", "captura de pantalla"),
            ("🔊 100%", "sube el volumen al 100%"),
            ("🔉 50%", "baja el volumen al 50%"),
        ]
        for label, cmd_text in chips:
            chip_btn = ctk.CTkButton(
                chips_frame, text=label, height=28,
                font=("Segoe UI", 11), fg_color="#181a2b",
                hover_color="#242840", text_color="#8ea4c8",
                corner_radius=14, command=lambda c=cmd_text: self.send_command(c)
            )
            chip_btn.pack(side="left", padx=4)

        self.chat_scroll = ctk.CTkScrollableFrame(view, fg_color="#0e0f1a", corner_radius=10)
        self.chat_scroll.pack(fill="both", expand=True, padx=20, pady=10)

        input_bar = ctk.CTkFrame(view, fg_color="#141624", height=65, corner_radius=12)
        input_bar.pack(fill="x", padx=20, pady=(0, 20))

        self.entry = ctk.CTkEntry(
            input_bar,
            placeholder_text="Escribe una orden o pregunta (ej: 'abre antigravity', 'sube el volumen al 100%', 'clima mañana')...",
            font=("Segoe UI", 13), fg_color="#1a1c2e", border_color="#282c44",
            height=44, corner_radius=8
        )
        self.entry.pack(side="left", fill="x", expand=True, padx=(12, 10), pady=10)
        self.entry.bind("<Return>", lambda e: self.on_send())

        send_btn = ctk.CTkButton(
            input_bar, text="Enviar", width=80, height=44,
            font=("Segoe UI", 13, "bold"), fg_color="#0066cc",
            hover_color="#0077ee", corner_radius=8, command=self.on_send
        )
        send_btn.pack(side="left", padx=(0, 8), pady=10)

        self.mic_btn = ctk.CTkButton(
            input_bar, text="🎤 Hablar", width=95, height=44,
            font=("Segoe UI", 13, "bold"), fg_color="#00a86b",
            hover_color="#00cc80", corner_radius=8, command=self.on_mic_click
        )
        self.mic_btn.pack(side="left", padx=(0, 12), pady=10)

        return view

    def _create_actions_view(self):
        view = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")

        title = ctk.CTkLabel(view, text="⚡ Centro de Acciones Rápidas", font=("Segoe UI", 20, "bold"), text_color="#ffffff")
        title.pack(anchor="w", padx=20, pady=(20, 5))
        desc = ctk.CTkLabel(view, text="Inicia o cierra las aplicaciones de tu PC con un solo clic.", font=("Segoe UI", 12), text_color="#7b849b")
        desc.pack(anchor="w", padx=20, pady=(0, 15))

        categories = [
            ("💻 Mis Aplicaciones (Abrir)", [
                ("🚀 Antigravity IDE", "abre antigravity"),
                ("💻 VS Code", "abre vs code"),
                ("☕ NetBeans", "abre netbeans"),
                ("🎬 CapCut", "abre capcut"),
                ("🦁 Brave", "abre brave"),
                ("🐳 Docker Desktop", "abre docker"),
            ]),
            ("❌ Mis Aplicaciones (Cerrar)", [
                ("🛑 Cerrar Antigravity", "cierra antigravity"),
                ("🛑 Cerrar VS Code", "cierra vs code"),
                ("🛑 Cerrar CapCut", "cierra capcut"),
                ("🛑 Cerrar NetBeans", "cierra netbeans"),
                ("🛑 Cerrar Brave", "cierra brave"),
                ("🛑 Cerrar Spotify", "cierra spotify"),
            ]),
            ("🔊 Control de Volumen y Sistema", [
                ("🔊 Volumen al 100%", "sube el volumen al 100%"),
                ("🔉 Volumen al 50%", "baja el volumen al 50%"),
                ("🔈 Volumen al 20%", "pon el volumen al 20%"),
                ("🔇 Silenciar / Mute", "silenciar"),
                ("📸 Captura en 2do Plano", "captura de pantalla"),
                ("🌙 Suspender PC", "modo suspension"),
            ]),
            ("🎵 Música y Navegación", [
                ("🎧 Abrir Spotify", "spotify"),
                ("▶ / ⏸ Play / Pausa", "pausa la musica"),
                ("🌐 Google Normal", "abre google"),
                ("🕵️ Incógnito", "busca flores en anonimo"),
                ("📰 Noticias BBC", "noticias"),
            ]),
        ]

        for cat_name, actions in categories:
            cat_frame = ctk.CTkFrame(view, fg_color="#121322", corner_radius=10)
            cat_frame.pack(fill="x", padx=20, pady=8)

            cat_lbl = ctk.CTkLabel(cat_frame, text=cat_name, font=("Segoe UI", 14, "bold"), text_color="#00d2ff")
            cat_lbl.pack(anchor="w", padx=16, pady=(12, 8))

            btn_grid = ctk.CTkFrame(cat_frame, fg_color="transparent")
            btn_grid.pack(fill="x", padx=12, pady=(0, 12))

            for label, cmd_str in actions:
                btn = ctk.CTkButton(
                    btn_grid, text=label, font=("Segoe UI", 12),
                    fg_color="#1c1f33", hover_color="#262b47", text_color="#e1e6f5",
                    height=36, corner_radius=8,
                    command=lambda c=cmd_str: (self.show_view("chat"), self.send_command(c))
                )
                btn.pack(side="left", padx=4, pady=4, expand=True, fill="x")

        return view

    def _create_memory_view(self):
        view = ctk.CTkFrame(self.main_container, fg_color="transparent")

        title = ctk.CTkLabel(view, text="🧠 Memoria Permanente RAG", font=("Segoe UI", 20, "bold"), text_color="#ffffff")
        title.pack(anchor="w", padx=20, pady=(20, 5))
        desc = ctk.CTkLabel(view, text="Información que DAEMON recuerda e inyecta en cada respuesta de IA.", font=("Segoe UI", 12), text_color="#7b849b")
        desc.pack(anchor="w", padx=20, pady=(0, 15))

        self.memory_textbox = ctk.CTkTextbox(view, font=("Segoe UI", 13), fg_color="#121322", text_color="#d8e2ff", corner_radius=10)
        self.memory_textbox.pack(fill="both", expand=True, padx=20, pady=10)

        add_frame = ctk.CTkFrame(view, fg_color="#121322", corner_radius=10)
        add_frame.pack(fill="x", padx=20, pady=(0, 20))

        self.new_mem_entry = ctk.CTkEntry(
            add_frame, placeholder_text="Añadir nuevo recuerdo permanente...",
            font=("Segoe UI", 12), fg_color="#1c1f33", border_color="#2b304c", height=38
        )
        self.new_mem_entry.pack(side="left", fill="x", expand=True, padx=(12, 8), pady=10)
        self.new_mem_entry.bind("<Return>", lambda e: self.add_memory_item())

        add_btn = ctk.CTkButton(
            add_frame, text="Añadir Recuerdo", font=("Segoe UI", 12, "bold"),
            fg_color="#0066cc", hover_color="#0077ee", height=38, command=self.add_memory_item
        )
        add_btn.pack(side="left", padx=(0, 8), pady=10)

        save_btn = ctk.CTkButton(
            add_frame, text="Guardar Cambios", font=("Segoe UI", 12, "bold"),
            fg_color="#00a86b", hover_color="#00cc80", height=38, command=self.save_memory_changes
        )
        save_btn.pack(side="left", padx=(0, 12), pady=10)

        self._reload_memory_box()
        return view

    def _reload_memory_box(self):
        self.memory_textbox.delete("1.0", "end")
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                    self.memory_textbox.insert("1.0", content)
            except Exception as e:
                self.memory_textbox.insert("1.0", f"Error cargando memoria: {e}")

    def add_memory_item(self):
        text = self.new_mem_entry.get().strip()
        if text:
            if not text.startswith("- "):
                text = f"- {text}"
            try:
                with open(MEMORY_FILE, "a", encoding="utf-8") as f:
                    f.write(f"{text}\n")
                self.new_mem_entry.delete(0, "end")
                self._reload_memory_box()
                messagebox.showinfo("Memoria Guardada", "El nuevo recuerdo ha sido registrado, Amo.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar: {e}")

    def save_memory_changes(self):
        content = self.memory_textbox.get("1.0", "end").strip()
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                f.write(content + "\n")
            messagebox.showinfo("Memoria Actualizada", "Los cambios en la memoria han sido guardados, Amo.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la memoria: {e}")

    def _create_config_view(self):
        view = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")

        title = ctk.CTkLabel(view, text="⚙️ Configuración del Sistema", font=("Segoe UI", 20, "bold"), text_color="#ffffff")
        title.pack(anchor="w", padx=20, pady=(20, 5))
        desc = ctk.CTkLabel(view, text="Personaliza el modelo de IA, identidad y preferencias de DAEMON.", font=("Segoe UI", 12), text_color="#7b849b")
        desc.pack(anchor="w", padx=20, pady=(0, 20))

        form_frame = ctk.CTkFrame(view, fg_color="#121322", corner_radius=12)
        form_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkLabel(form_frame, text="Modelo de Inteligencia Artificial (Ollama):", font=("Segoe UI", 13, "bold"), text_color="#00d2ff").pack(anchor="w", padx=20, pady=(16, 4))
        
        models: list[str] = [str(config.get("model", "gemma4:31b-cloud"))]
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=2).json()
            fetched = [m["name"] for m in r.get("models", [])]
            if fetched:
                models = fetched
        except:
            pass

        self.model_var = ctk.StringVar(value=str(config.get("model", "gemma4:31b-cloud")))
        model_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        model_row.pack(fill="x", padx=20, pady=(0, 10))

        self.model_dropdown = ctk.CTkOptionMenu(
            model_row, values=models, variable=self.model_var,
            font=("Segoe UI", 12), fg_color="#1f2338", button_color="#0066cc", height=36
        )
        self.model_dropdown.pack(side="left", fill="x", expand=True, padx=(0, 10))

        test_btn = ctk.CTkButton(
            model_row, text="Probar Conexión", font=("Segoe UI", 12, "bold"),
            fg_color="#2b314d", hover_color="#384066", height=36, command=self.test_ollama_model
        )
        test_btn.pack(side="left")

        ctk.CTkLabel(form_frame, text="Trato hacia el Creador:", font=("Segoe UI", 13, "bold"), text_color="#00d2ff").pack(anchor="w", padx=20, pady=(10, 4))
        self.owner_entry = ctk.CTkEntry(form_frame, font=("Segoe UI", 12), fg_color="#1c1f33", height=36)
        self.owner_entry.insert(0, "Amo")
        self.owner_entry.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(form_frame, text="Ciudad Predeterminada (para Clima y Pronósticos):", font=("Segoe UI", 13, "bold"), text_color="#00d2ff").pack(anchor="w", padx=20, pady=(10, 4))
        self.city_entry = ctk.CTkEntry(form_frame, font=("Segoe UI", 12), fg_color="#1c1f33", height=36)
        self.city_entry.insert(0, str(config.get("default_city", "Sincelejo")))
        self.city_entry.pack(fill="x", padx=20, pady=(0, 10))

        ctk.CTkLabel(form_frame, text="Opciones de Voz y Síntesis:", font=("Segoe UI", 13, "bold"), text_color="#00d2ff").pack(anchor="w", padx=20, pady=(10, 4))
        
        self.voice_switch = ctk.CTkSwitch(
            form_frame, text="Habilitar Respuesta por Voz (TTS)",
            font=("Segoe UI", 12), onvalue=True, offvalue=False
        )
        if config.get("voice_enabled", True):
            self.voice_switch.select()
        else:
            self.voice_switch.deselect()
        self.voice_switch.pack(anchor="w", padx=20, pady=(0, 10))

        speed_label = ctk.CTkLabel(form_frame, text=f"Velocidad de habla: {config.get('voice_speed', 180)} wpm", font=("Segoe UI", 12), text_color="#98a3c2")
        speed_label.pack(anchor="w", padx=20)
        self.speed_slider = ctk.CTkSlider(
            form_frame, from_=130, to=240, number_of_steps=22,
            command=lambda v: speed_label.configure(text=f"Velocidad de habla: {int(v)} wpm")
        )
        self.speed_slider.set(float(config.get("voice_speed", 180)))
        self.speed_slider.pack(fill="x", padx=20, pady=(0, 16))

        self.widget_switch = ctk.CTkSwitch(
            form_frame, text="Mantener Icono Flotante Arc Reactor en Pantalla",
            font=("Segoe UI", 12), onvalue=True, offvalue=False
        )
        if config.get("show_floating_widget", True):
            self.widget_switch.select()
        else:
            self.widget_switch.deselect()
        self.widget_switch.pack(anchor="w", padx=20, pady=(0, 16))

        ctk.CTkLabel(form_frame, text="Estilo Visual y Neón del Asistente:", font=("Segoe UI", 13, "bold"), text_color="#00d2ff").pack(anchor="w", padx=20, pady=(0, 4))
        theme_options = [
            "🌌 Nebulosa Galáctica Espectral (Multicolor 3D)",
            "Ámbar / Oro Neón (Akatsuki / Cyberpunk)",
            "Cyan Neón (Azul Clásico DAEMON)",
            "Verde Esmeralda Neón",
            "Rojo Carmesí Neón",
            "Púrpura Cyberpunk Neón"
        ]
        curr_theme = str(config.get("neon_theme", "spectral")).lower()
        default_theme_label = theme_options[0]
        for opt in theme_options:
            if curr_theme in opt.lower() or ("spectral" in curr_theme and "nebulosa" in opt.lower()):
                default_theme_label = opt
                break
        self.theme_var = ctk.StringVar(value=default_theme_label)
        self.theme_dropdown = ctk.CTkOptionMenu(
            form_frame, values=theme_options, variable=self.theme_var,
            font=("Segoe UI", 12), fg_color="#1f2338", button_color="#0066cc", height=36
        )
        self.theme_dropdown.pack(fill="x", padx=20, pady=(0, 20))

        save_cfg_btn = ctk.CTkButton(
            form_frame, text="💾  Guardar Configuración",
            font=("Segoe UI", 13, "bold"), fg_color="#00a86b",
            hover_color="#00cc80", height=42, command=self.save_settings
        )
        save_cfg_btn.pack(fill="x", padx=20, pady=(0, 20))

        return view

    def test_ollama_model(self):
        m = self.model_var.get().strip()
        self.set_status(f"Probando {m}...")
        def _test():
            try:
                r = requests.post(
                    "http://localhost:11434/api/chat",
                    json={"model": m, "messages": [{"role": "user", "content": "Di 'Conexión exitosa, Amo'"}], "stream": False},
                    timeout=10
                )
                if r.status_code == 200:
                    ans = r.json().get("message", {}).get("content", "")
                    messagebox.showinfo("Conexión Exitosa", f"Ollama respondió con el modelo '{m}':\n\n{ans}")
                else:
                    messagebox.showerror("Error", f"Ollama devolvió código: {r.status_code}")
            except Exception as e:
                messagebox.showerror("Error de Conexión", f"No se pudo conectar a Ollama: {e}")
            self.set_status("Listo")
        threading.Thread(target=_test, daemon=True).start()

    def save_settings(self):
        global config
        config["model"] = self.model_var.get().strip()
        config["owner_name"] = "Amo"
        config["default_city"] = self.city_entry.get().strip()
        config["voice_enabled"] = bool(self.voice_switch.get())
        config["voice_speed"] = int(self.speed_slider.get())
        config["show_floating_widget"] = bool(self.widget_switch.get())

        sel_theme = self.theme_var.get().lower()
        if "nebulosa" in sel_theme or "espectral" in sel_theme or "galáctica" in sel_theme:
            config["neon_theme"] = "spectral"
        elif "ambar" in sel_theme or "ámbar" in sel_theme or "oro" in sel_theme:
            config["neon_theme"] = "amber"
        elif "verde" in sel_theme:
            config["neon_theme"] = "green"
        elif "rojo" in sel_theme:
            config["neon_theme"] = "red"
        elif "purpura" in sel_theme or "púrpura" in sel_theme:
            config["neon_theme"] = "purple"
        else:
            config["neon_theme"] = "cyan"

        save_config(config)

        self.status_pill.configure(text=f"● En línea | {config['model']}")
        self.greeting_lbl.configure(text="Hola, Amo")
        self.user_tag.configure(text="👤 Amo")

        if config["show_floating_widget"]:
            self.widget.root.deiconify()
            self.widget._draw_reactor()
        else:
            self.widget.root.withdraw()

        messagebox.showinfo("Configuración Guardada", "Los ajustes han sido guardados, Amo.")

    def show_view(self, view_name):
        for vk, frame in self.views.items():
            if vk == view_name:
                frame.pack(fill="both", expand=True)
                self.nav_btns[vk].configure(fg_color="#1c1f33", text_color="#00d2ff")
            else:
                frame.pack_forget()
                self.nav_btns[vk].configure(fg_color="transparent", text_color="#c3cbe0")

    def show_window(self, view_name="chat"):
        self.deiconify()
        self.lift()
        self.focus_force()
        self.show_view(view_name)

    def minimize_to_widget(self):
        self.withdraw()
        self.widget.root.deiconify()
        self.widget.root.lift()

    def set_status(self, text):
        self.status_text_lbl.configure(text=text)

    def add_chat_message(self, sender, text):
        msg_frame = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        msg_frame.pack(fill="x", padx=10, pady=6)

        is_user = (sender == "Tú")
        align = "e" if is_user else "w"
        card_bg = "#1b2a47" if is_user else "#151726"
        border_col = "#2a4270" if is_user else "#00d2ff"

        card = ctk.CTkFrame(msg_frame, fg_color=card_bg, corner_radius=12, border_width=1, border_color=border_col)
        card.pack(anchor=align, padx=4)

        header_lbl = ctk.CTkLabel(
            card, text="👤 Amo" if is_user else f"🤖 {sender}",
            font=("Segoe UI", 11, "bold"), text_color="#00d2ff" if not is_user else "#85b7ff"
        )
        header_lbl.pack(anchor="w", padx=14, pady=(8, 2))

        content_lbl = ctk.CTkLabel(
            card, text=text, font=("Segoe UI", 13), text_color="#f0f3fa",
            wraplength=600, justify="left"
        )
        content_lbl.pack(anchor="w", padx=14, pady=(2, 10))
        self.chat_scroll._parent_canvas.yview_moveto(1.0)

    def clear_chat(self):
        global conversation_history
        conversation_history = []
        for widget in self.chat_scroll.winfo_children():
            widget.destroy()
        self.add_chat_message("DAEMON", "Conversación reiniciada. ¿Qué orden desea impartir hoy, Amo?")

    def send_command(self, text):
        if not text:
            return
        self.add_chat_message("Tú", text)
        self.set_status("Procesando...")

        def _execute():
            action_type, reply = process_command(text)
            self.set_status("Listo")

            if action_type == "EXIT":
                self.shutdown()
                return
            elif action_type == "PAUSE":
                self.widget.toggle_pause()
                return
            elif action_type == "WAKE":
                self.widget.is_paused = False

            if reply:
                self.add_chat_message("DAEMON", reply)
                speak(reply)

        threading.Thread(target=_execute, daemon=True).start()

    def on_send(self):
        text = self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self.send_command(text)

    def on_mic_click(self):
        self.widget.toggle_listen()

    def _startup_greeting(self):
        hour = datetime.datetime.now().hour
        saludo = "Buenos días" if hour < 12 else "Buenas tardes" if hour < 19 else "Buenas noches"
        greetings = [
            f"{saludo}, Amo. Todos los núcleos en línea y sistemas listos.",
            f"{saludo}, Amo. Sistemas cargados y a sus órdenes.",
            f"Inicialización completada. {saludo}, Amo. ¿Qué haremos hoy?",
        ]
        msg = random.choice(greetings)
        self.add_chat_message("DAEMON", msg)
        threading.Thread(target=speak, args=(msg,), daemon=True).start()

    def shutdown(self):
        try:
            self.widget.root.destroy()
        except:
            pass
        try:
            self.destroy()
        except:
            pass
        os._exit(0)

# =============================================================================
# ENTRADA PRINCIPAL
# =============================================================================
def main():
    app = DaemonApp()
    app.mainloop()

if __name__ == "__main__":
    main()