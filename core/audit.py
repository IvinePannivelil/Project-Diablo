import json
import os
import time
from typing import Dict, Any

AUDIT_LOG_PATH = "logs/audit_trail.jsonl"

class AuditLogger:
    def __init__(self, log_path: str = AUDIT_LOG_PATH):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def log_action(self, action_type: str, details: Dict[str, Any], reversible: bool = True, undo_payload: Dict[str, Any] = None):
        entry = {
            "timestamp": time.time(),
            "readable_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "action_type": action_type,
            "details": details,
            "reversible": reversible,
            "undo_payload": undo_payload or {},
            "status": "COMPLETED"
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        print(f"[AUDIT] {entry['readable_time']} | {action_type} logged.")

    def get_recent_actions(self, limit: int = 10):
        if not os.path.exists(self.log_path):
            return []
        with open(self.log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        return [json.loads(line) for line in lines[-limit:]]
