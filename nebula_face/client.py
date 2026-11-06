"""
D.A.E.M.O.N. - NebulaFaceClient
Robust, safe IPC client with strict timeouts, fork-bomb immunity, and max retries.
"""

import sys
import os
import json
import socket
import subprocess
import threading
import time
from typing import Callable, Optional

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

class NebulaFaceClient:
    def __init__(
        self,
        port: int = 9876,
        auto_start: bool = True,
        on_left_click: Optional[Callable[[], None]] = None,
        on_right_click: Optional[Callable[[int, int], None]] = None,
        on_double_click: Optional[Callable[[], None]] = None,
        on_drag_end: Optional[Callable[[int, int], None]] = None,
        on_connected: Optional[Callable[[], None]] = None,
        on_failed: Optional[Callable[[], None]] = None
    ):
        self.default_port = port
        self.port = port
        self.auto_start = auto_start
        self.on_left_click = on_left_click
        self.on_right_click = on_right_click
        self.on_double_click = on_double_click
        self.on_drag_end = on_drag_end
        self.on_connected = on_connected
        self.on_failed = on_failed

        self.sock: Optional[socket.socket] = None
        self.sock_lock = threading.Lock()
        self.is_connected = False
        self.is_running = True
        self.failed = False
        self.process: Optional[subprocess.Popen] = None

        if self.auto_start:
            self._ensure_server_running()

        # Connect thread with strict 5.0s timeout and max 2 attempts
        self._connect_thread = threading.Thread(target=self._connection_manager, daemon=True)
        self._connect_thread.start()

    def _get_server_port(self) -> int:
        port_file = os.path.join(os.path.expanduser("~"), ".daemon_nebula_port")
        if os.path.exists(port_file):
            try:
                with open(port_file, "r") as f:
                    p = int(f.read().strip())
                    if 1024 < p < 65535:
                        return p
            except Exception:
                pass
        return self.default_port

    def _ensure_server_running(self):
        """
        Launches the face process safely without ANY risk of fork-loop.
        1. In PyInstaller (frozen): ONLY launches 'NebulaFace.exe' by fixed path.
           NEVER uses sys.executable!
        2. In Development: ONLY launches python.exe if sys.executable is an actual python interpreter.
        """
        # Step 1: Check if already running and responding
        p = self._get_server_port()
        try:
            test_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_s.settimeout(0.3)
            test_s.connect(('127.0.0.1', p))
            test_s.close()
            return  # Already alive!
        except Exception:
            pass

        CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0

        # Step 2: Frozen mode (PyInstaller .exe)
        if getattr(sys, 'frozen', False):
            # Look for NebulaFace.exe alongside the main executable
            base_dir = get_base_dir()
            face_exe = os.path.join(base_dir, "NebulaFace.exe")
            if not os.path.exists(face_exe):
                # Check current dir
                face_exe = os.path.join(os.getcwd(), "NebulaFace.exe")

            if os.path.exists(face_exe):
                try:
                    self.process = subprocess.Popen(
                        [face_exe],
                        creationflags=CREATE_NO_WINDOW,
                        close_fds=True
                    )
                    time.sleep(0.5)
                except Exception as e:
                    print(f"[NEBULA CLIENT] Error launching NebulaFace.exe: {e}")
                    self.failed = True
            else:
                print(f"[NEBULA CLIENT] NebulaFace.exe no encontrado en {base_dir}. Continuando con canvas.")
                self.failed = True
            return

        # Step 3: Script / Development mode
        exec_name = os.path.basename(sys.executable).lower()
        if not ("python" in exec_name):
            print(f"[NEBULA CLIENT REJECT] sys.executable no es python ({sys.executable}). Abortando spawn.")
            self.failed = True
            return

        # Find nebula_server.py
        search_paths = [
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "nebula_server.py"),
            os.path.join(os.getcwd(), "nebula_face", "nebula_server.py"),
            os.path.join(os.getcwd(), "nebula_server.py")
        ]
        script_path = next((p for p in search_paths if os.path.exists(p)), None)

        if script_path:
            try:
                self.process = subprocess.Popen(
                    [sys.executable, script_path],
                    creationflags=CREATE_NO_WINDOW,
                    close_fds=True
                )
                time.sleep(0.5)
            except Exception as e:
                print(f"[NEBULA CLIENT] Error iniciando nebula_server.py: {e}")
                self.failed = True
        else:
            print("[NEBULA CLIENT] nebula_server.py no encontrado.")
            self.failed = True

    def _connection_manager(self):
        """
        Tries to connect to the face server.
        Limits to 2 attempts and a maximum of 5.0 seconds total deadline.
        If timeout occurs, marks failed=True, calls on_failed, and exits.
        """
        start_time = time.time()
        attempts = 0
        max_attempts = 2

        while self.is_running and not self.is_connected and not self.failed:
            if (time.time() - start_time) > 5.0 or attempts >= max_attempts:
                print(f"[NEBULA CLIENT] Tiempo de espera agotado (5s o {attempts} intentos). Continuando sin la cara 3D.")
                self.failed = True
                if self.on_failed:
                    try:
                        self.on_failed()
                    except Exception:
                        pass
                break

            attempts += 1
            try:
                p = self._get_server_port()
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1.5)
                s.connect(('127.0.0.1', p))
                s.settimeout(None)
                with self.sock_lock:
                    self.sock = s
                    self.is_connected = True
                
                # Connection successful!
                if self.on_connected:
                    try:
                        self.on_connected()
                    except Exception:
                        pass

                # Start listener thread
                threading.Thread(target=self._listen_events, args=(s,), daemon=True).start()
                break
            except Exception:
                time.sleep(1.0)

    def _listen_events(self, s: socket.socket):
        buffer = ""
        while self.is_running and self.is_connected:
            try:
                data = s.recv(4096).decode('utf-8')
                if not data:
                    break
                buffer += data
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    line = line.strip()
                    if line:
                        self._handle_event_message(line)
            except Exception:
                break
        with self.sock_lock:
            self.is_connected = False
            self.sock = None
        try:
            s.close()
        except Exception:
            pass

    def _handle_event_message(self, line: str):
        try:
            msg = json.loads(line)
            event = msg.get("event")
            data = msg.get("data", {})

            if event == "click_izquierdo" and self.on_left_click:
                self.on_left_click()
            elif event == "click_derecho" and self.on_right_click:
                self.on_right_click(data.get("x", 0), data.get("y", 0))
            elif event == "doble_clic" and self.on_double_click:
                self.on_double_click()
            elif event == "posicion_final_al_arrastrar" and self.on_drag_end:
                self.on_drag_end(data.get("x", 0), data.get("y", 0))
        except Exception as e:
            print(f"[NEBULA EVENT ERR] {e}")

    def _send_cmd(self, payload: dict):
        if not self.is_connected or not self.sock:
            return
        try:
            raw = json.dumps(payload) + "\n"
            with self.sock_lock:
                if self.sock:
                    self.sock.sendall(raw.encode('utf-8'))
        except Exception:
            with self.sock_lock:
                self.is_connected = False
                self.sock = None

    # =========================================================================
    # PUBLIC CONTROL METHODS
    # =========================================================================
    def set_state(self, state: str):
        self._send_cmd({"cmd": "set_state", "state": state})

    def set_level(self, level: float):
        self._send_cmd({"cmd": "set_level", "level": max(0.0, min(1.0, float(level)))})

    def set_bands(self, bass: float, mid: float, treble: float):
        self._send_cmd({
            "cmd": "set_bands",
            "bass": max(0.0, min(1.0, float(bass))),
            "mid": max(0.0, min(1.0, float(mid))),
            "treble": max(0.0, min(1.0, float(treble)))
        })

    def set_theme(self, theme_name: str):
        self._send_cmd({"cmd": "set_theme", "theme": theme_name})

    def set_quality(self, quality: str):
        self._send_cmd({"cmd": "set_quality", "quality": quality})

    def set_bloom(self, intensity: float):
        self._send_cmd({"cmd": "set_bloom", "intensity": float(intensity)})

    def toggle_spectrum(self, visible: bool):
        self._send_cmd({"cmd": "toggle_spectrum", "visible": bool(visible)})

    def set_size_mode(self, mode: str):
        self._send_cmd({"cmd": "set_size_mode", "mode": mode})

    def show_menu(self):
        self._send_cmd({"cmd": "show_menu"})

    def close(self):
        self._send_cmd({"cmd": "close"})
        self.is_running = False
        with self.sock_lock:
            if self.sock:
                try:
                    self.sock.close()
                except Exception:
                    pass
                self.sock = None
