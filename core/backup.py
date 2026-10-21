import os
import shutil
import time
import zipfile
from core.audit import AuditLogger

BACKUP_DIR = "backups"
CHROMA_DIR = "memory/chroma_db"

class BackupManager:
    def __init__(self, backup_dir: str = BACKUP_DIR):
        self.backup_dir = backup_dir
        self.audit = AuditLogger()
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_snapshot(self, tag: str = "auto") -> str:
        """Creates an offline, compressed snapshot of ChromaDB memory and config."""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_filename = f"diablo_backup_{tag}_{timestamp}.zip"
        backup_filepath = os.path.join(self.backup_dir, backup_filename)

        with zipfile.ZipFile(backup_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if os.path.exists(CHROMA_DIR):
                for root, dirs, files in os.walk(CHROMA_DIR):
                    for file in files:
                        full_path = os.path.join(root, file)
                        rel_path = os.path.relpath(full_path, start=".")
                        zipf.write(full_path, rel_path)
            
            # Backup staging queue and audit logs
            if os.path.exists("staging/review_queue.json"):
                zipf.write("staging/review_queue.json", "staging/review_queue.json")
            if os.path.exists("logs/audit_trail.jsonl"):
                zipf.write("logs/audit_trail.jsonl", "logs/audit_trail.jsonl")

        self.audit.log_action("CREATE_BACKUP", {"path": backup_filepath, "tag": tag}, reversible=False)
        print(f"[BACKUP] Snapshot saved to {backup_filepath}")
        return backup_filepath

    def list_backups(self):
        if not os.path.exists(self.backup_dir):
            return []
        files = [f for f in os.listdir(self.backup_dir) if f.endswith(".zip")]
        return sorted(files, reverse=True)
