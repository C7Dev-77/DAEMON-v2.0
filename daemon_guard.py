"""
D.A.E.M.O.N. - System Process Guard
Includes:
1. Win32 Named Kernel Mutex (Single Instance Lock)
2. Circuit Breaker (Disyuntor de seguridad anti-bucles)
"""

import sys
import os
import json
import time
import ctypes
from ctypes import wintypes

ERROR_ALREADY_EXISTS = 183

# Global references to keep Win32 handles open for process lifetime
_MUTEX_HANDLES = {}

def acquire_single_instance_mutex(mutex_name: str) -> bool:
    """
    Acquires a named Windows kernel mutex.
    Returns True if this is the ONLY instance running.
    Returns False if another instance is already active.
    """
    if os.name != 'nt':
        return True

    try:
        kernel32 = ctypes.windll.kernel32
        # CreateMutexW(security_attributes, initial_owner, name)
        handle = kernel32.CreateMutexW(None, False, mutex_name)
        last_error = kernel32.GetLastError()
        if last_error == ERROR_ALREADY_EXISTS:
            if handle:
                kernel32.CloseHandle(handle)
            return False
        _MUTEX_HANDLES[mutex_name] = handle
        return True
    except Exception as e:
        print(f"[GUARD] Mutex check failed ({e}), allowing start.")
        return True

def check_circuit_breaker(app_name: str, max_starts: int = 3, window_seconds: float = 10.0) -> bool:
    """
    Disyuntor de seguridad:
    Si detecta más de 'max_starts' arranques en 'window_seconds' segundos,
    bloquea la ejecución, registra el incidente en un log y retorna False.
    """
    temp_dir = os.environ.get("TEMP", os.path.expanduser("~"))
    breaker_file = os.path.join(temp_dir, f"{app_name}_circuit_breaker.json")
    log_file = os.path.join(temp_dir, f"{app_name}_emergency_circuit_breaker.log")

    now = time.time()
    history = []

    if os.path.exists(breaker_file):
        try:
            with open(breaker_file, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    # Keep timestamps within window
                    history = [t for t in data if (now - t) < window_seconds]
        except Exception:
            history = []

    history.append(now)

    try:
        with open(breaker_file, "w") as f:
            json.dump(history, f)
    except Exception:
        pass

    if len(history) > max_starts:
        # Tripped circuit breaker!
        msg = (
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] DISYUNTOR ACTIVADO: "
            f"{app_name} superó {max_starts} arranques en {window_seconds}s ({len(history)} intentos). "
            f"Ejecución abortada inmediatamente para proteger el sistema.\n"
        )
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(msg)
        except Exception:
            pass
        print(msg, file=sys.stderr)
        return False

    return True

