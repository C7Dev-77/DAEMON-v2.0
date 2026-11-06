"""
D.A.E.M.O.N. - 3D Galactic Nebula Floating Face Process
Runs as an isolated, independent GUI process using Microsoft Edge WebView2 (via pywebview)
Features:
 - Frameless, 100% transparent alpha channel window
 - Always on top, freely draggable
 - Full WebGL2 Three.js 3D galactic nebula particle cloud
 - Localhost IPC TCP socket server for low-latency JSON communication with DAEMON
 - PyInstaller single-file compatibility (sys._MEIPASS)
"""

import sys
import os
import json
import socket
import threading
import multiprocessing
import time
import webview

try:
    from daemon_guard import acquire_single_instance_mutex, check_circuit_breaker
except ImportError:
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    from daemon_guard import acquire_single_instance_mutex, check_circuit_breaker

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

def get_html_path():
    base = get_base_dir()
    # Check if index.html is in current dir or nebula_face subdir
    p1 = os.path.join(base, "index.html")
    if os.path.exists(p1):
        return p1
    p2 = os.path.join(base, "nebula_face", "index.html")
    if os.path.exists(p2):
        return p2
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html")

class NebulaBridgeApi:
    """Exposes methods to the JavaScript front-end to forward user interaction events."""
    def __init__(self, server_instance):
        self.server = server_instance

    def on_event(self, event_type, data):
        self.server.broadcast_event(event_type, data)

class NebulaServer:
    def __init__(self, port=9876, width=180, height=180):
        self.port = port
        self.width = width
        self.height = height
        self.window = None
        self.clients = []
        self.clients_lock = threading.Lock()
        self.is_running = True
        self.api = NebulaBridgeApi(self)

    def start_socket_server(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind with fallback to next free port if 9876 is busy
        bound = False
        for p in range(self.port, self.port + 20):
            try:
                server_sock.bind(('127.0.0.1', p))
                self.port = p
                bound = True
                break
            except Exception:
                continue

        if not bound:
            server_sock.bind(('127.0.0.1', 0))
            self.port = server_sock.getsockname()[1]

        server_sock.listen(5)
        print(f"[NEBULA SERVER] Listening for IPC commands on 127.0.0.1:{self.port}", flush=True)

        # Write discovery port file so clients can locate this instance
        try:
            port_file = os.path.join(os.path.expanduser("~"), ".daemon_nebula_port")
            with open(port_file, "w") as f:
                f.write(str(self.port))
        except Exception:
            pass

        while self.is_running:
            try:
                client_sock, _ = server_sock.accept()
                with self.clients_lock:
                    self.clients.append(client_sock)
                threading.Thread(target=self._handle_client, args=(client_sock,), daemon=True).start()
            except Exception:
                break

    def _handle_client(self, client_sock):
        buffer = ""
        while self.is_running:
            try:
                data = client_sock.recv(4096).decode('utf-8')
                if not data:
                    break
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    if line:
                        self._process_ipc_message(line)
            except Exception:
                break
        with self.clients_lock:
            if client_sock in self.clients:
                self.clients.remove(client_sock)
        try:
            client_sock.close()
        except Exception:
            pass

    def _process_ipc_message(self, message_str):
        try:
            msg = json.loads(message_str)
            cmd = msg.get("cmd")
            if not self.window:
                return

            if cmd == "set_state":
                state = msg.get("state", "idle")
                self.window.evaluate_js(f"window.nebulaSetState('{state}');")
            elif cmd == "set_level":
                level = float(msg.get("level", 0.0))
                self.window.evaluate_js(f"window.nebulaSetLevel({level});")
            elif cmd == "set_bands":
                b = float(msg.get("bass", 0.0))
                m = float(msg.get("mid", 0.0))
                t = float(msg.get("treble", 0.0))
                self.window.evaluate_js(f"window.nebulaSetBands({b}, {m}, {t});")
            elif cmd == "set_theme":
                theme = msg.get("theme", "spectral")
                self.window.evaluate_js(f"window.nebulaSetTheme('{theme}');")
            elif cmd == "set_quality":
                quality = msg.get("quality", "auto")
                self.window.evaluate_js(f"window.nebulaSetQuality('{quality}');")
            elif cmd == "set_bloom":
                intensity = float(msg.get("intensity", 0.95))
                self.window.evaluate_js(f"window.nebulaSetBloom({intensity});")
            elif cmd == "toggle_spectrum":
                vis = "true" if msg.get("visible", True) else "false"
                self.window.evaluate_js(f"window.nebulaToggleSpectrum({vis});")
            elif cmd == "set_size_mode":
                mode = msg.get("mode", "widget")
                if mode == "expanded":
                    self.window.resize(480, 480)
                else:
                    self.window.resize(180, 180)
            elif cmd == "close":
                self.is_running = False
                self.window.destroy()
        except Exception as e:
            print(f"[IPC ERR] {e}", flush=True)

    def broadcast_event(self, event_type, data):
        payload = json.dumps({"event": event_type, "data": data}) + "\n"
        with self.clients_lock:
            dead_clients = []
            for c in self.clients:
                try:
                    c.sendall(payload.encode('utf-8'))
                except Exception:
                    dead_clients.append(c)
            for dc in dead_clients:
                self.clients.remove(dc)

    def run(self):
        # 1. Start IPC Socket Listener in background thread
        threading.Thread(target=self.start_socket_server, daemon=True).start()

        # 2. Configure PyWebView for frameless transparent Edge WebView2
        html_file = get_html_path()

        # Calculate initial position on bottom right of screen
        try:
            screens = webview.screens
            primary = screens[0] if screens else None
            sw = primary.width if primary else 1920
            sh = primary.height if primary else 1080
            pos_x = sw - self.width - 40
            pos_y = sh - self.height - 120
        except Exception:
            pos_x, pos_y = 1680, 840

        self.window = webview.create_window(
            title="DAEMON 3D Face",
            url=html_file,
            js_api=self.api,
            width=self.width,
            height=self.height,
            x=pos_x,
            y=pos_y,
            frameless=True,
            easy_drag=True,
            on_top=True,
            transparent=True,
            background_color='#000000'
        )

        # 3. Start WebView GUI loop (blocking)
        webview.start(debug=False)

if __name__ == "__main__":
    multiprocessing.freeze_support()
    # 1. Candado de instancia única para la cara flotante
    if not acquire_single_instance_mutex("Global\\DAEMON_NebulaFace_Instance_Mutex_77"):
        sys.exit(0)

    # 2. Disyuntor de seguridad (máximo 3 arranques en 10s)
    if not check_circuit_breaker("NebulaFace", max_starts=3, window_seconds=10.0):
        sys.exit(99)

    server = NebulaServer()
    server.run()

