# =============================================================================
# J.A.R.V.I.S. v3 - Asistente Local con IA (Ollama)
# SEGURIDAD: Todo local. Unico trafico externo: Google Speech (voz a texto)
# =============================================================================

import tkinter as tk
import threading
import time
import os
import subprocess
import webbrowser
import pyperclip
import pyautogui
import speech_recognition as sr
import win32com.client
import requests
import math
import random
from datetime import datetime
import winsound

# ========================== CONFIGURACION ==========================
OLLAMA_URL = "http://localhost:11434"
OLLAMA_MODEL = "gemma4:31b-cloud"
OWNER_NAME = "Cristian"
STARTUP_DELAY = 4
OLLAMA_START_DELAY = 1
conversation_history = []

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.05


# ========================== MOTOR DE VOZ ==========================
class VoiceEngine:
    def __init__(self):
        self._lock = threading.Lock()
        try:
            self._engine = win32com.client.Dispatch("SAPI.SpVoice")
            self._engine.Rate = 2  # Un poco mas rapido (rango -10 a 10)
        except Exception as e:
            print(f"[ERROR SAPI] {e}")
            self._engine = None

    def speak(self, text):
        with self._lock:
            try:
                print(f"[JARVIS] {text}")
                if self._engine:
                    # Hablar sincronamente
                    self._engine.Speak(text)
            except Exception as e:
                print(f"[ERROR VOZ] {e}")


voice = VoiceEngine()


def speak(text):
    voice.speak(text)


def listen():
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            # Calibracion de ruido de fondo (1 segundo)
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            # Aumentamos agresivamente el umbral para ignorar musica, pc y calle
            recognizer.energy_threshold += 800 
            recognizer.dynamic_energy_threshold = False 
            print("[MIC] Escuchando (Umbral ajustado para ruido)...")
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=15)
            text = recognizer.recognize_google(audio, language="es-ES")
            print(f"[MIC] Reconocido: {text}")
            return text.lower().strip()
    except (sr.WaitTimeoutError, sr.UnknownValueError):
        return ""
    except Exception as e:
        print(f"[ERROR MIC] {e}")
        return ""


# ========================== APPS CONOCIDAS ==========================
APPS = {
    "word": {"cmd": "winword", "name": "Microsoft Word"},
    "excel": {"cmd": "excel", "name": "Microsoft Excel"},
    "powerpoint": {"cmd": "powerpnt", "name": "PowerPoint"},
    "bloc de notas": {"cmd": "notepad", "name": "Bloc de Notas"},
    "notepad": {"cmd": "notepad", "name": "Bloc de Notas"},
    "calculadora": {"cmd": "calc", "name": "Calculadora"},
    "paint": {"cmd": "mspaint", "name": "Paint"},
    "explorador": {"cmd": "explorer", "name": "Explorador de archivos"},
    "chrome": {"cmd": "chrome", "name": "Google Chrome"},
    "google chrome": {"cmd": "chrome", "name": "Google Chrome"},
    "edge": {"cmd": "msedge", "name": "Microsoft Edge"},
    "firefox": {"cmd": "firefox", "name": "Firefox"},
    "google": {"url": "https://www.google.com", "name": "Google"},
    "youtube": {"url": "https://www.youtube.com", "name": "YouTube"},
    "github": {"url": "https://www.github.com", "name": "GitHub"},
    "visual studio": {"cmd": "code", "name": "VS Code"},
    "vs code": {"cmd": "code", "name": "VS Code"},
    "antigravity": {"cmd": "code", "name": "VS Code"},
    "terminal": {"cmd": "wt", "name": "Windows Terminal"},
    "cmd": {"cmd": "cmd", "name": "Simbolo del sistema"},
    "spotify": {"cmd": "spotify", "name": "Spotify"},
    "discord": {"cmd": "discord", "name": "Discord"},
}


def open_app(app_key):
    app = APPS.get(app_key)
    if not app:
        return False
    try:
        if "url" in app:
            webbrowser.open(app["url"])
        else:
            subprocess.Popen(
                f'start "" "{app["cmd"]}"',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        return True
    except Exception as e:
        print(f"[ERROR] No se pudo abrir {app_key}: {e}")
        try:
            os.system(f'start {app.get("cmd", app_key)}')
            return True
        except:
            return False


def type_text(text):
    """Escribe texto donde este el cursor usando portapapeles (soporta acentos)."""
    if not text:
        return

    # Guardar portapapeles actual
    old_clipboard = ""
    try:
        old_clipboard = pyperclip.paste()
    except:
        pass

    # Copiar el texto nuevo al portapapeles
    pyperclip.copy(text)
    time.sleep(0.5)

    # Pegar con Ctrl+V
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)

    # Restaurar portapapeles
    try:
        if old_clipboard:
            pyperclip.copy(old_clipboard)
    except:
        pass


SCREENSHOT_DIR = r"C:\Users\Bienvenido\Pictures\Capturas Jarvis"

def take_screenshot():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = os.path.join(SCREENSHOT_DIR, f"captura_{timestamp}.png")
    screenshot = pyautogui.screenshot()
    screenshot.save(path)
    return path


# ========================== PROCESADOR DE COMANDOS ==========================
def find_app_in_command(command):
    """Busca una app conocida dentro del comando. Retorna la key mas larga que coincida."""
    matches = []
    for app_key in APPS:
        if app_key in command:
            matches.append(app_key)
    if matches:
        # Retornar la coincidencia mas larga (ej: "google chrome" antes que "chrome")
        return max(matches, key=len)
    return None


def process_command(command):
    global conversation_history
    if not command:
        return None

    print(f"[CMD] Procesando: {command}")

    # --- APAGAR ---
    shutdown_triggers = ["apagar jarvis", "cerrar jarvis", "desactivar", "adios jarvis", "apagate", "apagar", "apaga el sistema", "salir", "sal de aqui", "cierrate"]
    if any(w in command for w in shutdown_triggers):
        frases = [
            f"Listo Amo {OWNER_NAME}, me apago. Que le vaya excelente.",
            f"Entendido jefe. Apagando todo. Nos vemos luego.",
            f"Ok Amo {OWNER_NAME}, me retiro. Cualquier cosa aqui estoy.",
        ]
        speak(random.choice(frases))
        return "EXIT"

    # --- PAUSAR JARVIS ---
    if command in ["pausa", "pausate", "silencio", "duerme", "modo espera", "pausa a jarvis"]:
        frases = [
            "Ok, me quedo calladito. Haga clic en mi interfaz para despertar.",
            "Modo silencioso activado. Estoy aqui por si acaso.",
            "Listo, en pausa. Un toque en mi logo y vuelvo.",
        ]
        speak(random.choice(frases))
        return "PAUSE"

    # --- DESPERTAR ---
    if any(w in command for w in ["despertar", "despierta", "activar", "activa"]):
        frases = [
            f"Ya estoy de vuelta, Amo {OWNER_NAME}. Que necesita.",
            f"Aqui reportandome jefe. Digame.",
            f"Listo, activo y escuchando. Ordene Amo {OWNER_NAME}.",
        ]
        speak(random.choice(frases))
        return "WAKE"

    # --- CAPTURA DE PANTALLA ---
    if any(w in command for w in ["captura", "screenshot", "pantallazo", "foto de pantalla", "toma una captura"]):
        speak("Un momento, tomando la foto.")
        time.sleep(1)
        take_screenshot()
        frases = [
            "Captura lista. Guardada en su carpeta de imagenes.",
            "Listo, ya quedo la captura. Esta en Capturas Jarvis.",
            "Foto tomada y guardada. Revise su carpeta de imagenes.",
        ]
        speak(random.choice(frases))
        return None

    # --- LEER TEXTO (EN VOZ ALTA) ---
    if any(w in command for w in ["lee esto", "lee el texto", "lee lo seleccionado", "leeme esto", "lee la seleccion", "leelo"]):
        try:
            selected = pyperclip.paste().strip()
            if selected:
                speak(f"El texto dice: {selected}")
            else:
                speak("Tu portapapeles esta vacio. Por favor, sombrea el texto, presiona Control C, y vuelve a pedirme que lo lea.")
        except:
            speak("Hubo un error al acceder al portapapeles.")
        return None

    # --- CONTROL DE SISTEMA ---
    if "sube el volumen" in command or "subir el volumen" in command or "mas volumen" in command:
        pyautogui.press('volumeup', presses=15)
        speak("Volumen arriba.")
        return None
    if "baja el volumen" in command or "bajar el volumen" in command or "menos volumen" in command:
        pyautogui.press('volumedown', presses=15)
        speak("Volumen abajo.")
        return None
    if "silenciar" in command or "mutea" in command or "ponte en mudo" in command:
        pyautogui.press('volumemute')
        speak("Sistema silenciado.")
        return None
    
    if "sube el brillo" in command or "mas brillo" in command:
        os.system('powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, 100)')
        speak("Brillo de la pantalla al maximo.")
        return None
    if "baja el brillo" in command or "menos brillo" in command:
        os.system('powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, 30)')
        speak("Brillo de la pantalla disminuido.")
        return None

    if "enciende el bluetooth" in command or "apaga el bluetooth" in command or "bluetooth" in command:
        os.system("start ms-settings:bluetooth")
        speak("Abriendo la configuracion de Bluetooth. Por seguridad de Windows, debes activarlo o desactivarlo desde esta ventana.")
        return None

    if "abre la calculadora" in command or "calculadora" in command:
        os.system("calc")
        speak("Calculadora lista.")
        return None

    if "vacia la papelera" in command or "limpia la papelera" in command:
        speak("Vaciando la papelera de reciclaje.")
        os.system("powershell Clear-RecycleBin -Force")
        speak("Papelera limpia.")
        return None

    if "modo suspension" in command or "suspender pc" in command or "duerme la pc" in command:
        speak("A mimir. Suspendiendo el sistema en 3, 2, 1...")
        time.sleep(2)
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return None

    # --- MEMORIA (RECORDATORIOS) ---
    memory_triggers = ["recuerda que", "recuerdame que", "anota que", "guarda que", "recuerdame", "recuerda", "anota", "guarda"]
    for trigger in memory_triggers:
        if command.startswith(trigger) or f" {trigger} " in f" {command} ":
            nota = command.split(trigger, 1)[1].strip()
            # Evitar capturar cosas como "guarda la imagen"
            if nota and not nota.startswith("la ") and not nota.startswith("el "):
                try:
                    with open("memoria_jarvis.txt", "a", encoding="utf-8") as f:
                        f.write(f"- {nota}\n")
                    speak("Listo, ya lo anote permanentemente en mis registros de memoria.")
                except:
                    speak("Hubo un error al guardar ese recuerdo.")
                return None

    # --- CERRAR APLICACIONES ---
    if "cierra" in command or "cerrar" in command:
        if "chrome" in command:
            os.system("taskkill /IM chrome.exe /F")
            speak("Chrome cerrado.")
            return None
        if "spotify" in command:
            os.system("taskkill /IM Spotify.exe /F")
            speak("Spotify cerrado.")
            return None
        if "discord" in command:
            os.system("taskkill /IM Discord.exe /F")
            speak("Discord cerrado.")
            return None
        if "bloc de notas" in command or "notepad" in command:
            os.system("taskkill /IM notepad.exe /F")
            speak("Bloc de notas cerrado.")
            return None

    # --- CONTROL DE MEDIOS (SPOTIFY / YOUTUBE) ---
    if any(w in command for w in ["pausa la musica", "pausar la musica", "pausa la cancion", "pausa", "pausar spotify", "deten la cancion", "pausar cancion", "detener cancion"]):
        pyautogui.press('playpause')
        return None
        
    play_triggers = [
        "reproduce la musica", "reanuda la musica", "continua", "dale play", 
        "ponle play", "reproduce la que esta sonando", "reproduce la cancion que esta sonando",
        "reproduce cancion", "reproducir cancion", "pon musica"
    ]
    if command in ["reproduce la cancion", "pon la cancion", "reproduce"] or any(w in command for w in play_triggers):
        pyautogui.press('playpause')
        return None
            
    if any(w in command for w in ["siguiente cancion", "pasa la cancion", "cambia la cancion", "pon otra", "siguiente"]):
        pyautogui.press('nexttrack')
        return None
        
    if any(w in command for w in ["anterior cancion", "cancion anterior", "regresa la cancion", "pon la anterior", "anterior"]):
        pyautogui.press('prevtrack')
        return None

    # --- BUSCAR MUSICA NUEVA ---
    # Solo buscara si incluyes explicitamente la palabra 'busca' o 'buscar'
    if "cancion" in command and any(w in command for w in ["busca", "buscar"]):
        song = command
        for word in ["busca en google la cancion", "busca la cancion de", "busca la cancion", "buscar la cancion", "busca", "buscar", "en spotify", "en youtube", "de"]:
            song = song.replace(word, "").strip()
        
        if song:
            if "youtube" in command:
                speak(f"Buscando {song} en YouTube.")
                webbrowser.open(f"https://www.youtube.com/results?search_query={song.replace(' ', '+')}")
            else:
                speak(f"Buscando {song} en Spotify.")
                os.system(f'start spotify:search:{song.replace(" ", "%20")}')
            return None
            
    # Otras formas de buscar musica sin la palabra "cancion"
    for trigger in ["busca la musica de "]:
        if trigger in command:
            song = command.split(trigger, 1)[1].strip()
            if song:
                speak(f"Buscando {song} en Spotify.")
                os.system(f'start spotify:search:{song.replace(" ", "%20")}')
                return None

    # --- ABRIR APLICACIONES ---
    open_triggers = ["abre", "abrir", "inicia", "iniciar", "ejecuta", "lanza", "abreme", "abre el", "abre la"]
    is_open_command = any(w in command for w in open_triggers)

    if is_open_command:
        app_key = find_app_in_command(command)
        if app_key:
            app_info = APPS[app_key]
            open_app(app_key)
            frases = [
                f"{app_info['name']} iniciado. Listo para usar.",
                f"Ya abri {app_info['name']}. Ahi lo tiene.",
                f"{app_info['name']} arriba y corriendo.",
            ]
            speak(random.choice(frases))
            return None

        # Si no encontro app conocida, extraer nombre e intentar
        for trigger in open_triggers:
            if trigger in command:
                parts = command.split(trigger, 1)
                if len(parts) > 1:
                    app_name = parts[1].strip()
                    if app_name:
                        speak(f"Buscando {app_name} en el sistema.")
                        try:
                            subprocess.Popen(f'start "" "{app_name}"', shell=True,
                                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                            speak("Listo, deberia estar abriendose.")
                        except:
                            speak("No encontre esa aplicacion. Revise el nombre.")
                        return None
        return None

    # --- ESCRIBIR TEXTO ---
    type_triggers = ["escribe", "escribir", "teclea", "tipea", "redacta", "pon"]
    for trigger in type_triggers:
        if trigger in command:
            text_to_type = command.split(trigger, 1)[1].strip()
            if text_to_type:
                speak("Dale, escribiendo. Asegurese de tener el cursor donde quiere.")
                time.sleep(2.5)
                type_text(text_to_type)
                frases = [
                    f"Listo, ya lo escribi.",
                    f"Ahi quedo. Revise que este bien.",
                    f"Escrito. Cualquier cosa me dice y lo corrijo.",
                    f"Ya esta. Vaya texto eh jaja.",
                ]
                speak(random.choice(frases))
                return None

    # --- BUSCAR EN GOOGLE ---
    search_triggers = ["busca", "buscar", "investiga", "googlea"]
    for trigger in search_triggers:
        if trigger in command:
            query = command.split(trigger, 1)[1].strip()
            # Limpiar cosas como "en google"
            query = query.replace("en google", "").replace("sobre", "").strip()
            if query:
                speak(f"Buscando {query}. Un momento.")
                webbrowser.open(f"https://www.google.com/search?q={query}")
                time.sleep(1)
                frases = [
                    f"Listo, ahi estan los resultados de {query}.",
                    f"Ya le busque {query}. Reviselo en el navegador.",
                    f"Busqueda lista. Ojala encuentre lo que necesita.",
                ]
                speak(random.choice(frases))
                return None

    # --- HORA ---
    if any(w in command for w in ["hora", "que hora"]):
        now = datetime.now().strftime("%I:%M %p")
        frases = [
            f"Son las {now}, Amo {OWNER_NAME}.",
            f"Ahorita son las {now} jefe.",
            f"Marca las {now}. A darle.",
        ]
        speak(random.choice(frases))
        return None

    # --- RUTEO INTELIGENTE (PORTAPAPELES A OLLAMA) ---
    trigger_words = ["traduce", "traducir", "traducelo", "traduceme", "resume", "resumir", "resumelo", "resumeme", "explica", "explicame", "analiza", "analizalo"]
    
    is_smart_cmd = False
    for t in trigger_words:
        if t in command:
            is_smart_cmd = True
            break
            
    if is_smart_cmd:
        # Ya no evaluamos si la oracion es larga. Simplemente sacamos el texto de Control C
        try:
            selected = pyperclip.paste().strip()
            if selected:
                # Modificamos el comando crudo para adjuntarle el texto a Ollama
                command = f"{command}. El texto que debes procesar es el siguiente: '{selected}'"
            else:
                speak("No detecte ningun texto en tu portapapeles. Copialo presionando Control C y pidemelo de nuevo.")
                return None
        except:
            pass

    # --- PREGUNTAR A OLLAMA ---
    # Cargar memoria RAG
    notas_memoria = ""
    if os.path.exists("memoria_jarvis.txt"):
        try:
            with open("memoria_jarvis.txt", "r", encoding="utf-8") as f:
                notas_memoria = f.read().strip()
        except Exception as e:
            print(f"[ERROR MEMORIA] {e}")

    try:
        # 1. Agregamos el nuevo mensaje del usuario al historial temporal
        conversation_history.append({"role": "user", "content": command})
        
        # 2. Limitamos el historial para no saturar la memoria (ultimos 10 mensajes)
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
            
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        hora_actual = datetime.now().strftime("%I:%M %p")
        dias = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
        dia_semana = dias[datetime.now().weekday()]

        system_prompt = (
            f"Eres JARVIS, el asistente leal, super inteligente, divertido y un poco sarcastico del Amo {OWNER_NAME}. "
            f"Ten en cuenta que la fecha actual del sistema es {dia_semana} {fecha_actual} y la hora es {hora_actual}. "
            "Si te pide hacer algo absurdo o jugueton, SIGUELE LA CORRIENTE actuando como si realmente tuvieras un cuerpo fisico o brazos mecanicos. "
            "Responde en espanol sin tildes ni caracteres especiales. "
            "Se directo y conciso, maximo 2 a 3 oraciones."
        )
        
        messages = [{"role": "system", "content": system_prompt}] + list(conversation_history)
        
        # Inyectar la memoria a largo plazo DIRECTAMENTE en el ultimo mensaje para que la IA no la ignore
        if notas_memoria:
            ultimo_mensaje = messages[-1]["content"]
            messages[-1] = {
                "role": "user",
                "content": f"{ultimo_mensaje}\n\n[CONTEXTO OCULTO PARA TI - MEMORIA A LARGO PLAZO DEL USUARIO:\n{notas_memoria}\nUsa esta informacion para responder si es necesario]"
            }

        response = requests.post(
            f"{OLLAMA_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False
            },
            timeout=60
        )
        data = response.json()
        if "error" in data:
            print(f"[OLLAMA ERROR] {data['error']}")
            speak("Mi procesador de IA dice que el modelo no esta disponible.")
        else:
            answer = data.get("message", {}).get("content", "No pude procesar eso.")
            
            # 3. Guardamos la respuesta de Jarvis en el historial para contexto futuro
            conversation_history.append({"role": "assistant", "content": answer})
            
            # Limpieza de tildes para el sintetizador de voz de Windows
            answer = answer.replace("\u00e1", "a").replace("\u00e9", "e").replace("\u00ed", "i")
            answer = answer.replace("\u00f3", "o").replace("\u00fa", "u").replace("\u00f1", "ni")
            speak(answer)
    except requests.ConnectionError:
        speak("Ollama no esta disponible en este momento.")
    except Exception as e:
        speak("Hubo un error al consultar la inteligencia artificial.")
        print(f"[ERROR OLLAMA] {e}")

    return None


# ========================== INTERFAZ FLOTANTE ==========================

class JarvisWidget:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JARVIS")

        # Sin barra de titulo, siempre encima
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.92)

        # Tamano
        self.widget_size = 80
        screen_w = self.root.winfo_screenwidth()
        self.root.geometry(f"{self.widget_size}x{self.widget_size}+{screen_w - 110}+30")

        # FONDO SOLIDO (NO transparente - esto arregla el arrastre y los clics)
        self.bg_color = '#0d0d2b'
        self.root.configure(bg=self.bg_color)

        # Canvas
        self.canvas = tk.Canvas(
            self.root,
            width=self.widget_size,
            height=self.widget_size,
            bg=self.bg_color,
            highlightthickness=0,
            cursor="hand2"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Estado
        self.is_listening = False
        self.is_paused = False
        self.is_running = True
        self.is_deaf_mode = False
        self.pulse_angle = 0

        # Variables para el arrastre
        self._offset_x = 0
        self._offset_y = 0
        self._is_dragging = False
        self._press_time = 0

        # Eventos del mouse -- directamente en la ventana root para maxima captura
        self.root.bind('<ButtonPress-1>', self._on_press)
        self.root.bind('<B1-Motion>', self._on_drag)
        self.root.bind('<ButtonRelease-1>', self._on_release)
        self.root.bind('<Button-3>', self._show_menu)

        # Menu contextual
        self.menu = tk.Menu(
            self.root, tearoff=0,
            bg='#111133', fg='#00ccff',
            activebackground='#0044aa', activeforeground='white',
            font=('Segoe UI', 11), bd=2, relief='ridge'
        )
        self.menu.add_command(
            label="\U0001F3A4  Escuchar / Detener",
            command=lambda: threading.Thread(target=self._toggle_listen, daemon=True).start()
        )
        self.menu.add_command(
            label="\u23F8  Pausar",
            command=lambda: threading.Thread(target=self._pause, daemon=True).start()
        )
        self.menu.add_separator()
        self.menu.add_command(
            label="\U0001F4F7  Captura Pantalla",
            command=lambda: threading.Thread(target=self._cmd_screenshot, daemon=True).start()
        )
        self.menu.add_command(
            label="\U0001F916  Cambiar Modelo IA",
            command=self._change_model
        )
        self.menu.add_separator()
        self.menu.add_command(
            label="\u26A0  Apagar JARVIS",
            command=self._shutdown
        )

        # Dibujar y animar
        self._draw_icon()
        self._animate()

    # --------- DIBUJO ---------
    def _draw_icon(self):
        self.canvas.delete("all")
        cx = self.widget_size // 2
        cy = self.widget_size // 2
        r = self.widget_size // 2 - 4

        if self.is_paused:
            color = '#ff3333'
        elif self.is_listening:
            color = '#00ff88'
        else:
            color = '#00ccff'

        # Glow exterior
        glow_color = color.replace('ff', '44').replace('cc', '33').replace('88', '22')
        self.canvas.create_oval(
            cx - r - 3, cy - r - 3, cx + r + 3, cy + r + 3,
            outline=glow_color, width=4
        )

        # Circulo principal con relleno solido
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline=color, width=3, fill='#0d0d2b'
        )

        # Circulo interior
        r2 = r - 10
        self.canvas.create_oval(
            cx - r2, cy - r2, cx + r2, cy + r2,
            outline=color, width=1
        )

        # Triangulo
        tr = r2 - 6
        pts = [
            cx, cy - tr,
            cx - int(tr * 0.87), cy + int(tr * 0.5),
            cx + int(tr * 0.87), cy + int(tr * 0.5),
        ]
        self.canvas.create_polygon(pts, outline=color, fill='', width=2)

        # Punto central
        self.canvas.create_oval(cx - 4, cy, cx + 4, cy + 8, fill=color, outline='')

        # Marcas giratorias
        for i in range(4):
            angle = math.radians(self.pulse_angle + i * 90)
            x1 = cx + int((r - 2) * math.cos(angle))
            y1 = cy + int((r - 2) * math.sin(angle))
            x2 = cx + int((r + 4) * math.cos(angle))
            y2 = cy + int((r + 4) * math.sin(angle))
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)

    def _animate(self):
        if not self.is_running:
            return
        self.pulse_angle = (self.pulse_angle + 3) % 360
        self._draw_icon()
        self.root.after(80, self._animate)

    # --------- ARRASTRE ---------
    def _on_press(self, event):
        # Guardar posicion del mouse relativa a la ventana
        self._offset_x = event.x
        self._offset_y = event.y
        self._is_dragging = False
        self._press_time = time.time()

    def _on_drag(self, event):
        self._is_dragging = True
        # Calcular nueva posicion de la ventana
        x = self.root.winfo_pointerx() - self._offset_x
        y = self.root.winfo_pointery() - self._offset_y
        self.root.geometry(f"{self.widget_size}x{self.widget_size}+{x}+{y}")

    def _on_release(self, event):
        elapsed = time.time() - self._press_time
        if not self._is_dragging and elapsed < 0.4:
            # Click rapido = toggle escucha
            threading.Thread(target=self._toggle_listen, daemon=True).start()
        self._is_dragging = False

    # --------- MENU ---------
    def _show_menu(self, event):
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    # --------- ACCIONES ---------
    def _toggle_listen(self):
        if self.is_paused:
            self.is_paused = False
            speak(f"Reactivado, Amo {OWNER_NAME}. A sus ordenes.")

        self.is_listening = not self.is_listening

        if self.is_listening:
            # Sonido agudo al activar
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
            self._listen_loop()
        else:
            # Sonido grave al desactivar
            winsound.MessageBeep(winsound.MB_ICONHAND)

    def _listen_loop(self):
        while self.is_listening and self.is_running and not self.is_paused:
            command = listen()
            if command:
                if self.is_deaf_mode:
                    if any(w in command for w in ["eres inteligente", "despierta", "llega", "vuelve", "regresa"]):
                        self.is_deaf_mode = False
                        speak(random.choice(["Aqui estoy.", "Dime.", "A tu disposicion.", "Claro."]))
                    continue
                
                if any(w in command for w in ["eres ciega", "eres sorda", "vete", "largate", "no escuches"]):
                    self.is_deaf_mode = True
                    speak(random.choice(["Ok.", "Como digas.", "A la orden.", "Claro que si."]))
                    continue

                result = process_command(command)
                if result == "EXIT":
                    # Forzar el cierre inmediato desde el hilo
                    self.is_running = False
                    os._exit(0)
                elif result == "PAUSE":
                    self.is_paused = True
                    self.is_listening = False
                    return
                elif result == "WAKE":
                    self.is_paused = False
            time.sleep(0.1)

    def _pause(self):
        self.is_paused = True
        self.is_listening = False
        speak("Modo espera activado. Haga clic para reactivar.")

    def _cmd_screenshot(self):
        self.root.withdraw()
        time.sleep(0.5)
        take_screenshot()
        self.root.deiconify()
        speak("Captura de pantalla guardada.")

    def _change_model(self):
        global OLLAMA_MODEL
        win = tk.Toplevel(self.root)
        win.title("Modelo IA")
        win.geometry("350x180")
        win.configure(bg='#111133')
        win.attributes('-topmost', True)
        win.resizable(False, False)

        tk.Label(
            win, text="Modelo de Ollama:", bg='#111133', fg='#00ccff',
            font=('Segoe UI', 12, 'bold')
        ).pack(pady=(20, 5))

        entry = tk.Entry(
            win, bg='#1a1a44', fg='white', font=('Segoe UI', 12),
            insertbackground='white', justify='center', bd=2, relief='groove'
        )
        entry.insert(0, OLLAMA_MODEL)
        entry.pack(padx=30, fill='x', ipady=5)
        entry.focus_set()
        entry.select_range(0, tk.END)

        def save():
            global OLLAMA_MODEL
            new_model = entry.get().strip()
            if new_model:
                OLLAMA_MODEL = new_model
                speak(f"Modelo cambiado a {OLLAMA_MODEL}")
            win.destroy()

        tk.Button(
            win, text="Guardar", command=save,
            bg='#00ccff', fg='black', font=('Segoe UI', 11, 'bold'),
            cursor='hand2', bd=0, padx=20, pady=5
        ).pack(pady=15)

        entry.bind('<Return>', lambda e: save())

    def _shutdown(self):
        self.is_running = False
        self.is_listening = False
        try:
            self.root.destroy()
        except:
            pass
        os._exit(0)

    def run(self):
        self.root.mainloop()


# ========================== INICIO ==========================
def main():
    # Iniciar Ollama
    time.sleep(OLLAMA_START_DELAY)
    try:
        subprocess.Popen(
            ["ollama", "serve"],
            creationflags=subprocess.CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass

    # Esperar para saludo
    time.sleep(STARTUP_DELAY - OLLAMA_START_DELAY)

    # Saludo dinamico
    hour = datetime.now().hour
    if hour < 12:
        saludo = "Buenos dias"
    elif hour < 19:
        saludo = "Buenas tardes"
    else:
        saludo = "Buenas noches"
        
    greetings = [
        f"{saludo} Amo {OWNER_NAME}. Todos los nucleos en linea y sistemas cargados.",
        f"{saludo} Amo {OWNER_NAME}. Sistemas iniciados y listos a sus ordenes.",
        f"Inicializacion completada. {saludo} Amo {OWNER_NAME}. Que haremos hoy?",
    ]
    speak(random.choice(greetings))

    # Widget + escucha
    app = JarvisWidget()
    app.is_listening = True
    threading.Thread(target=app._listen_loop, daemon=True).start()
    app.run()


if __name__ == "__main__":
    main()
