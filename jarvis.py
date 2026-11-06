"""
=============================================================================
 D.A.E.M.O.N. (Evolución de J.A.R.V.I.S. V1.0 - C7Dev)
 Launcher y puente de compatibilidad directa
=============================================================================
"""
import os
import sys
import subprocess

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_script = os.path.join(script_dir, "daemon_gui.py")
    if os.path.exists(target_script):
        print("⚡ [D.A.E.M.O.N.] Iniciando asistente...")
        subprocess.run([sys.executable, target_script] + sys.argv[1:])
    else:
        print("[ERROR] No se encontro 'daemon_gui.py' en el directorio.")

if __name__ == "__main__":
    main()
