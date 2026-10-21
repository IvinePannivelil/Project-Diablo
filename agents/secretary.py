import time
import os
import json
from core.audit import AuditLogger

class MeetingSecretary:
    def __init__(self, logs_dir: str = "logs/meetings"):
        self.logs_dir = logs_dir
        self.audit = AuditLogger()
        self.is_recording = False
        os.makedirs(self.logs_dir, exist_ok=True)

    def start_meeting(self, meeting_title: str = "Meeting"):
        """Prime Directive: Requires explicit manual start per meeting."""
        self.is_recording = True
        self.current_title = meeting_title
        self.start_time = time.time()
        self.transcripts = []
        self.audit.log_action("START_MEETING", {"title": meeting_title}, reversible=False)
        print(f"[SECRETARY] Meeting '{meeting_title}' started. Recording active.")

    def add_transcript_segment(self, speaker: str, text: str):
        if not self.is_recording:
            return
        self.transcripts.append({
            "timestamp": time.strftime("%H:%M:%S"),
            "speaker": speaker,
            "text": text
        })

    def end_meeting(self) -> str:
        if not self.is_recording:
            return ""
        self.is_recording = False
        duration = round(time.time() - self.start_time, 1)
        
        meeting_data = {
            "title": self.current_title,
            "date": time.strftime("%Y-%m-%d"),
            "duration_seconds": duration,
            "transcript": self.transcripts,
            "summary": "Meeting recorded and transcribed by Diablo.",
            "action_items": ["Review transcripts", "Confirm action points"]
        }
        
        filename = f"meeting_{time.strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.logs_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(meeting_data, f, indent=2)
            
        self.audit.log_action("END_MEETING", {"title": self.current_title, "file": filepath}, reversible=False)
        print(f"[SECRETARY] Meeting finalized and saved to {filepath}")
        return filepath
