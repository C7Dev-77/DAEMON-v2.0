"""
D.A.E.M.O.N. - Nebula Face 3D Standalone Demo Launcher
Opens the interactive testbed with sliders, state controls and live GPU telemetry.
"""

import os
import sys
import webview

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

def main():
    demo_file = os.path.join(get_base_dir(), "demo.html")
    if not os.path.exists(demo_file):
        demo_file = os.path.join(get_base_dir(), "nebula_face", "demo.html")

    print(f"[DEMO] Launching Nebula 3D Testbed: {demo_file}")

    window = webview.create_window(
        title="D.A.E.M.O.N. - Nebula Face 3D Visual Testbed",
        url=demo_file,
        width=1000,
        height=720,
        resizable=True,
        min_size=(640, 480)
    )
    webview.start(debug=False)

if __name__ == "__main__":
    main()

