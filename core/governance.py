import psutil
from core.audit import AuditLogger

PROFILES = {
    "POWER_SAVER": {
        "max_ram_percent": 60,
        "allow_avatar": False,
        "allow_voice": False,
        "allow_vision": False,
        "mode_description": "Text-only, lowest background footprint for gaming on RTX 4060."
    },
    "BALANCED": {
        "max_ram_percent": 80,
        "allow_avatar": True,
        "allow_voice": True,
        "allow_vision": False,
        "mode_description": "Standard productivity, balanced local AI and memory."
    },
    "MAX_PERFORMANCE": {
        "max_ram_percent": 95,
        "allow_avatar": True,
        "allow_voice": True,
        "allow_vision": True,
        "mode_description": "Full RTX 4060 allocation for heavy coding, vision, and RAG."
    }
}

class ResourceGovernor:
    def __init__(self, initial_profile: str = "BALANCED"):
        self.current_profile = initial_profile
        self.is_emergency_halted = False
        self.audit = AuditLogger()

    def set_profile(self, profile_name: str) -> bool:
        p = profile_name.upper()
        if p not in PROFILES:
            raise ValueError(f"Profile {profile_name} not recognized. Choose from: {list(PROFILES.keys())}")
        self.current_profile = p
        self.audit.log_action("SET_PERFORMANCE_PROFILE", {"profile": p, "details": PROFILES[p]}, reversible=True)
        print(f"[GOVERNOR] Performance Profile switched to: {p}")
        return True

    def check_system_headroom(self) -> dict:
        ram = psutil.virtual_memory()
        cpu = psutil.cpu_percent(interval=0.1)
        limits = PROFILES[self.current_profile]
        has_headroom = ram.percent <= limits["max_ram_percent"]
        return {
            "ram_used_percent": ram.percent,
            "ram_limit_percent": limits["max_ram_percent"],
            "cpu_percent": cpu,
            "can_load_heavy_task": has_headroom and not self.is_emergency_halted,
            "emergency_halted": self.is_emergency_halted
        }

    def emergency_override(self) -> bool:
        """Prime Directive 8: Instantly halts all active tasks into idle read-only state."""
        self.is_emergency_halted = True
        self.audit.log_action("EMERGENCY_OVERRIDE_TRIGGERED", {"status": "READ_ONLY_IDLE"}, reversible=True)
        print("[EMERGENCY] ALL DIABLO TASKS HALTED. System switched to idle read-only mode.")
        return True

    def resume_from_override(self) -> bool:
        self.is_emergency_halted = False
        self.audit.log_action("EMERGENCY_OVERRIDE_CLEARED", {"status": "NORMAL_OPERATION"}, reversible=True)
        print("[EMERGENCY] Override cleared. Resumed normal operation.")
        return True
