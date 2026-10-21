import os
import shutil
from typing import Dict
from core.staging import StagingManager

DEFAULT_RULES = {
    ".pdf": "Documents/PDFs",
    ".docx": "Documents/Word",
    ".xlsx": "Documents/Excel",
    ".csv": "Data/CSVs",
    ".png": "Pictures/Screenshots",
    ".jpg": "Pictures/Photos",
    ".mp4": "Videos",
    ".zip": "Archives"
}

class FileOrganizerAgent:
    def __init__(self, dropzone_dir: str = "dropzone", base_target_dir: str = "organized_files"):
        self.dropzone_dir = dropzone_dir
        self.base_target_dir = base_target_dir
        self.staging = StagingManager()
        os.makedirs(self.dropzone_dir, exist_ok=True)
        os.makedirs(self.base_target_dir, exist_ok=True)

    def scan_and_stage_dropzone(self) -> list:
        staged_items = []
        files = [f for f in os.listdir(self.dropzone_dir) if os.path.isfile(os.path.join(self.dropzone_dir, f))]
        for filename in files:
            source_file = os.path.join(self.dropzone_dir, filename)
            _, ext = os.path.splitext(filename)
            subfolder = DEFAULT_RULES.get(ext.lower(), "Others")
            destination = os.path.join(self.base_target_dir, subfolder, filename)
            
            stage_id = self.staging.stage_file_for_organization(source_file, destination)
            staged_items.append({"id": stage_id, "file": filename, "proposed": destination})
        return staged_items
