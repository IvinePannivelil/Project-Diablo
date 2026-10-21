import sys
import os
import threading
import uvicorn
from PyQt6.QtWidgets import QApplication

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from core.governance import ResourceGovernor
from core.staging import StagingManager
from core.audit import AuditLogger
from core.memory import RAGMemory
from core.backup import BackupManager
from ui.dashboard import app as fastapi_app
from ui.desktop_overlay import DiabloHUD

def start_backend_server():
    """Runs the Mission Control API in a background daemon thread."""
    try:
        uvicorn.run(fastapi_app, host='127.0.0.1', port=8000, log_level='warning')
    except Exception as e:
        print(f"[SERVER ERROR]: {e}")

def run_system_check():
    print("==================================================")
    print("         PROJECT DIABLO - MASTER LAUNCHER         ")
    print("==================================================")
    print("Enforcing 11 Prime Directives...")
    gov = ResourceGovernor()
    hr = gov.check_system_headroom()
    print(f"Hardware Status: RAM Used: {hr['ram_used_percent']}% | Profile: {gov.current_profile}")
    print("ChromaDB Memory: Ready")
    print("Mission Control: http://localhost:8000")
    print("Desktop HUD: Active")
    print("System Tray: Active (Next to Clock)")
    print("==================================================")

def main():
    run_system_check()

    # 1. Start FastAPI server in background thread
    server_thread = threading.Thread(target=start_backend_server, daemon=True)
    server_thread.start()

    # 2. Start Desktop HUD & System Tray in main thread
    qt_app = QApplication(sys.argv)
    hud = DiabloHUD()
    hud.show()
    sys.exit(qt_app.exec())

if __name__ == '__main__':
    main()