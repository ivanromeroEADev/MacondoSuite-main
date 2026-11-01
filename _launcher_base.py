"""
Startup code for the .exe files.

Picks a free port, opens the browser and runs Streamlit headless with the Macondo
theme passed as flags, so the .exe doesn't need the .streamlit folder.
"""

import os
import socket
import sys
import threading
import time
import webbrowser

from streamlit.web import cli as stcli

import macondo_theme  # to reuse exactly the same theme colors

PREFERRED_PORT = 8501


def _resource_path(name):
    """Path to a file, whether running from the .exe (PyInstaller temp folder) or from the code."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def _free_port(preferred):
    """Uses the preferred port; if it's taken (another app is open), takes a free one."""
    for port in (preferred, 0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("127.0.0.1", port))
                return sock.getsockname()[1]
            except OSError:
                continue
    return preferred


def _open_browser(port):
    time.sleep(3)  # give Streamlit time to start before opening the browser
    webbrowser.open(f"http://localhost:{port}")


def run(app_file):
    """Starts the given app. app_file is the name of the .py (e.g. 'macondo_app.py')."""
    port = _free_port(PREFERRED_PORT)
    threading.Thread(target=_open_browser, args=(port,), daemon=True).start()
    sys.argv = [
        "streamlit", "run", _resource_path(app_file),
        "--global.developmentMode=false",
        "--server.headless=true",
        "--server.address=127.0.0.1",
        f"--server.port={port}",
        "--browser.gatherUsageStats=false",
        # Built-in Macondo theme, taking the colors from macondo_theme itself.
        "--theme.base=light",
        f"--theme.primaryColor={macondo_theme.MUSTARD}",
        f"--theme.backgroundColor={macondo_theme.BACKGROUND}",
        f"--theme.secondaryBackgroundColor={macondo_theme.BEIGE}",
        f"--theme.textColor={macondo_theme.BROWN}",
        "--theme.font=sans serif",
    ]
    sys.exit(stcli.main())
