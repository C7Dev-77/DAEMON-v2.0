"""
D.A.E.M.O.N. - NebulaFaceClient
Lightweight IPC Client used by daemon_gui.py to interact with the independent 3D Nebula Face process.
Handles non-blocking command transmission and event callbacks (clicks, dragging, state changes).
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
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

class NebulaFaceClient:
    def __init__(
        self,
        port: int = 9876,
        auto_start: bool = True,
        on_left_click: Optional[Callable[[], None]] = None,
        on_right_click: Optional[Callable[[int, int], None]] = None,
        on_double_click: Optional[Callable[[], None]] = None,
        on_drag_end: Optional[Callable[[int, int], None]] = None
    ):
        self.default_port = port
        self.port = port
        self.auto_start = auto_start
        self.on_left_click = on_left_click
        self.on_right_click = on_right_click
        self.on_double_click = on_double_click
        self.on_drag_end = on_drag_end

        self.sock: Optional[socket.socket] = None
        self.sock_lock = threading.Lock()
        self.is_connected = False
        self.is_running = True
        self.process: Optional[subprocess.Popen] = None

        if self.auto_start:
            self._ensure_server_running()

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
        # Check if already responding
        p = self._get_server_port()
        try:
            test_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_s.settimeout(0.3)
            test_s.connect(('127.0.0.1', p))
            test_s.close()
            return
        except Exception:
            pass

        # Find nebula_server.py
        candidates = [
            os.path.join(get_base_dir(), "nebula_server.py"),
            os.path.join(get_base_dir(), "nebula_face", "nebula_server.py"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "nebula_server.py")
        ]
        script_path = next((c for c in candidates if os.path.exists(c)), None)

        if script_path:
            CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0
            python_exe = sys.executable
            try:
                self.process = subprocess.Popen(
                    [python_exe, script_path],
                    creationflags=CREATE_NO_WINDOW,
                    close_fds=True
                )
                time.sleep(1.0)
            except Exception as e:
                print(f"[NEBULA CLIENT] Failed to launch server: {e}")

    def _connection_manager(self):
        while self.is_running:
            if not self.is_connected:
                try:
                    p = self._get_server_port()
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2.0)
                    s.connect(('127.0.0.1', p))
                    s.settimeout(None)
                    with self.sock_lock:
                        self.sock = s
                        self.is_connected = True
                    # Start receiver thread
                    threading.Thread(target=self._listen_events, args=(s,), daemon=True).start()
                except Exception:
                    time.sleep(1.0)
            else:
                time.sleep(1.5)

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
        """Sets the state: 'idle', 'listening', 'thinking', 'speaking', 'error', 'paused'"""
        self._send_cmd({"cmd": "set_state", "state": state})

    def set_level(self, level: float):
        """Sets audio reactivity level (0.0 to 1.0)"""
        self._send_cmd({"cmd": "set_level", "level": max(0.0, min(1.0, float(level)))})

    def set_bands(self, bass: float, mid: float, treble: float):
        """Sets 3-band audio spectrum values (0.0 to 1.0 each)"""
        self._send_cmd({
            "cmd": "set_bands",
            "bass": max(0.0, min(1.0, float(bass))),
            "mid": max(0.0, min(1.0, float(mid))),
            "treble": max(0.0, min(1.0, float(treble)))
        })

    def set_theme(self, theme_name: str):
        """Sets palette: 'spectral', 'aurora', 'gold', 'monochrome'"""
        self._send_cmd({"cmd": "set_theme", "theme": theme_name})

    def set_quality(self, quality: str):
        """Sets quality scaler: 'auto', 'high', 'medium', 'low'"""
        self._send_cmd({"cmd": "set_quality", "quality": quality})

    def set_bloom(self, intensity: float):
        """Sets post-processing bloom intensity (0.0 to 2.5)"""
        self._send_cmd({"cmd": "set_bloom", "intensity": float(intensity)})

    def toggle_spectrum(self, visible: bool):
        """Toggles the fine 64-band radial audio spectrum ring"""
        self._send_cmd({"cmd": "toggle_spectrum", "visible": bool(visible)})

    def set_size_mode(self, mode: str):
        """Sets window size mode: 'widget' (180px) or 'expanded' (480px)"""
        self._send_cmd({"cmd": "set_size_mode", "mode": mode})

    def show_menu(self):
        """Requests display of contextual action menu"""
        self._send_cmd({"cmd": "show_menu"})

    def close(self):
        """Closes the independent face window and disconnects"""
        self._send_cmd({"cmd": "close"})
        self.is_running = False
        with self.sock_lock:
            if self.sock:
                try:
                    self.sock.close()
                except Exception:
                    pass
                self.sock = None
