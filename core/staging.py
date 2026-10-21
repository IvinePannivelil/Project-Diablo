import json
import os
import shutil
import uuid
import time
from core.audit import AuditLogger

STAGING_DIR = "staging"
QUEUE_FILE = os.path.join(STAGING_DIR, "review_queue.json")

class StagingManager:
    def __init__(self, staging_dir: str = STAGING_DIR):
        self.staging_dir = staging_dir
        self.queue_file = QUEUE_FILE
        self.audit = AuditLogger()
        os.makedirs(self.staging_dir, exist_ok=True)
        if not os.path.exists(self.queue_file):
            with open(self.queue_file, "w", encoding="utf-8") as f:
                json.dump([], f)

    def stage_file_for_organization(self, source_path: str, proposed_destination: str) -> str:
        """Prime Directive 4 & 6: Stages a file before moving to final destination."""
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file {source_path} not found.")

        item_id = str(uuid.uuid4())[:8]
        filename = os.path.basename(source_path)
        staged_copy_path = os.path.join(self.staging_dir, f"{item_id}_{filename}")
        
        # Copy to staging sandbox
        shutil.copy2(source_path, staged_copy_path)
        
        entry = {
            "id": item_id,
            "type": "FILE_ORGANIZATION",
            "source_path": source_path,
            "staged_path": staged_copy_path,
            "proposed_destination": proposed_destination,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "PENDING_REVIEW"
        }
        
        self._add_to_queue(entry)
        self.audit.log_action("STAGE_FILE", {"file": filename, "id": item_id}, reversible=True)
        return item_id

    def stage_knowledge_for_review(self, title: str, content: str, source_url: str = "") -> str:
        """Prime Directive 4: Stages researched knowledge before permanent memory write."""
        item_id = str(uuid.uuid4())[:8]
        entry = {
            "id": item_id,
            "type": "KNOWLEDGE_INGESTION",
            "title": title,
            "content": content,
            "source_url": source_url,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "PENDING_REVIEW"
        }
        self._add_to_queue(entry)
        self.audit.log_action("STAGE_KNOWLEDGE", {"title": title, "id": item_id}, reversible=False)
        return item_id

    def get_pending_queue(self):
        with open(self.queue_file, "r", encoding="utf-8") as f:
            items = json.load(f)
        return [i for i in items if i.get("status") == "PENDING_REVIEW"]

    def approve_item(self, item_id: str, memory_engine = None):
        """User explicitly approves item per Prime Directive 2 (Absolute Consent)."""
        with open(self.queue_file, "r", encoding="utf-8") as f:
            items = json.load(f)

        target = None
        for item in items:
            if item["id"] == item_id and item["status"] == "PENDING_REVIEW":
                target = item
                item["status"] = "APPROVED"
                break

        if not target:
            raise ValueError(f"Item {item_id} not found in pending review queue.")

        with open(self.queue_file, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2)

        if target["type"] == "FILE_ORGANIZATION":
            dest_dir = os.path.dirname(target["proposed_destination"])
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(target["staged_path"], target["proposed_destination"])
            # Remove original only after verified move
            if os.path.exists(target["source_path"]):
                os.remove(target["source_path"])
            self.audit.log_action("COMMIT_FILE_MOVE", target, reversible=True, undo_payload={"revert_to": target["source_path"], "current": target["proposed_destination"]})
            print(f"[STAGING] Approved & moved {target['source_path']} -> {target['proposed_destination']}")

        elif target["type"] == "KNOWLEDGE_INGESTION" and memory_engine:
            memory_engine.ingest_text(target["content"], source=target["source_url"] or target["title"], doc_id=f"doc_{item_id}")
            self.audit.log_action("COMMIT_KNOWLEDGE", {"title": target["title"], "id": item_id}, reversible=True)
            print(f"[STAGING] Approved & saved knowledge '{target['title']}' to permanent memory.")

        return True

    def _add_to_queue(self, entry):
        with open(self.queue_file, "r", encoding="utf-8") as f:
            items = json.load(f)
        items.append(entry)
        with open(self.queue_file, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2)
