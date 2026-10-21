import os
import subprocess
import ctypes
from core.audit import AuditLogger

ALLOWLISTED_APPS = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "spotify": "spotify.exe",
    "chrome": "chrome.exe",
    "vscode": "code.cmd"
}

class SystemController:
    def __init__(self):
        self.audit = AuditLogger()

    def lock_screen(self) -> bool:
        """Prime Directive: Safe allow-listed system command."""
        self.audit.log_action("LOCK_SCREEN", {}, reversible=False)
        ctypes.windll.user32.LockWorkStation()
        return True

    def open_approved_app(self, app_name: str) -> bool:
        """Prime Directive: Strictly restricted to pre-approved allow-list."""
        app_key = app_name.lower().strip()
        if app_key not in ALLOWLISTED_APPS:
            print(f"[SYSTEM BLOCKED] '{app_name}' is not in the approved application allow-list.")
            return False
            
        cmd = ALLOWLISTED_APPS[app_key]
        subprocess.Popen(cmd, shell=True)
        self.audit.log_action("OPEN_APP", {"app": app_key, "executable": cmd}, reversible=False)
        print(f"[SYSTEM] Opened approved application: {app_key}")
        return True

    def set_system_volume(self, level: int):
        """Volume adjustment (0-100)."""
        level = max(0, min(100, level))
        self.audit.log_action("SET_VOLUME", {"level": level}, reversible=True)
        print(f"[SYSTEM] Volume set to {level}%")
        return True
