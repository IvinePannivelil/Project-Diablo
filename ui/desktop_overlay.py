import os
import sys
import math
import webbrowser

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

from PyQt6.QtCore import Qt, QTimer, QPoint, QRectF
from PyQt6.QtGui import QPainter, QPixmap, QColor, QFont, QPen, QIcon
from PyQt6.QtWidgets import (QApplication, QWidget, QLineEdit, 
                             QSystemTrayIcon, QMenu, QFileDialog)

from core.voice import VoiceInterface
from core.memory import RAGMemory
from core.governance import ResourceGovernor
from core.audit import AuditLogger
from core.docs import DocumentManager
from core.system_control import SystemController
from agents.coder import CoderAgent
from agents.organizer import FileOrganizerAgent
from agents.secretary import MeetingSecretary

class DiabloHUD(QWidget):
    def __init__(self):
        super().__init__()
        self.governor = ResourceGovernor()
        self.memory = RAGMemory()
        self.voice = VoiceInterface()
        self.audit = AuditLogger()
        self.doc_mgr = DocumentManager()
        self.system_ctrl = SystemController()
        self.coder = CoderAgent()
        self.organizer = FileOrganizerAgent()
        self.secretary = MeetingSecretary()

        self.rotation_angle = 0.0
        self.float_phase = 0.0
        self.state = "IDLE" # IDLE, LISTENING, THINKING, SPEAKING, HALTED
        self.speech_text = "Kufufufu... At your service, Lord Ivine."
        self.speech_opacity = 1.0
        self.speech_timer_count = 360
        self.drag_position = QPoint()

        self.profiles = ["BALANCED", "MAX_PERFORMANCE", "POWER_SAVER"]
        self.profile_idx = 0

        # Load Pixmaps
        self.pixmap_seal = QPixmap("ui/assets/diablo_seal_circle.png")
        self.pixmap_avatar = QPixmap("ui/assets/diablo_avatar_circle.png")

        # Enable Drag and Drop for Files
        self.setAcceptDrops(True)

        self.init_window()
        self.init_chat_input()
        self.init_tray()
        self.init_timers()

        # Startup Voice Greeting
        QTimer.singleShot(600, self.voice.greet)

    def init_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.SubWindow
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.resize(360, 490)

        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - 380, screen.height() - 540)

    def init_chat_input(self):
        self.chat_input = QLineEdit(self)
        self.chat_input.setGeometry(25, 410, 310, 36)
        self.chat_input.setPlaceholderText("💬 Type command, file path, or drop file here...")
        self.chat_input.setStyleSheet("""
            QLineEdit {
                background: rgba(17, 24, 39, 0.95);
                border: 1.5px solid rgba(239, 68, 68, 0.6);
                border-radius: 18px;
                color: #f3f4f6;
                padding: 0 14px;
                font-size: 12px;
                font-family: 'Segoe UI';
            }
            QLineEdit:focus {
                border: 1.5px solid #ef4444;
                background: rgba(17, 24, 39, 1.0);
            }
        """)
        self.chat_input.returnPressed.connect(self.handle_text_query)

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        if os.path.exists("ui/assets/diablo_avatar_circle.png"):
            self.tray_icon.setIcon(QIcon("ui/assets/diablo_avatar_circle.png"))

        tray_menu = QMenu()
        show_action = tray_menu.addAction("👑 Summon Diablo")
        show_action.triggered.connect(self.show_hud)

        hide_action = tray_menu.addAction("🌑 Banish Diablo (Hide)")
        hide_action.triggered.connect(self.hide_hud)

        tray_menu.addSeparator()
        self.voice_action = tray_menu.addAction("🔊 Voice Output: ON")
        self.voice_action.triggered.connect(self.toggle_voice_output)

        dash_action = tray_menu.addAction("📊 Mission Control")
        dash_action.triggered.connect(lambda: webbrowser.open("http://localhost:8000"))

        halt_action = tray_menu.addAction("🛑 Emergency Halt")
        halt_action.triggered.connect(self.trigger_halt)

        tray_menu.addSeparator()
        quit_action = tray_menu.addAction("❌ Terminate Diablo")
        quit_action.triggered.connect(QApplication.instance().quit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide_hud()
            else:
                self.show_hud()

    def show_hud(self):
        self.show()
        self.set_speech("Kufufufu... I have returned, Lord Ivine.", duration=4)

    def hide_hud(self):
        self.hide()
        self.tray_icon.showMessage("Diablo", "Diablo has retreated into the shadows. Click icon to summon him.", QSystemTrayIcon.MessageIcon.Information, 2000)

    def init_timers(self):
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start(16)

    def update_animation(self):
        current_prof = self.profiles[self.profile_idx]
        speed = 0.8 if current_prof == "BALANCED" else 3.5 if current_prof == "MAX_PERFORMANCE" else 0.3
        if self.state == "LISTENING":
            speed *= 2.5
        elif self.state == "THINKING":
            speed *= 4.0

        self.rotation_angle = (self.rotation_angle + speed) % 360.0
        self.float_phase = (self.float_phase + 0.05) % (2 * math.pi)

        if self.speech_timer_count > 0:
            self.speech_timer_count -= 1
            if self.speech_timer_count == 0:
                self.speech_opacity = 0.0

        self.update()

    def set_speech(self, text: str, duration: int = 7):
        self.speech_text = text
        self.speech_opacity = 1.0
        self.speech_timer_count = duration * 60

    # Drag and Drop File Handlers
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.state = "LISTENING"
            self.set_speech("A file offering? Release to present it to me.", duration=3)

    def dragLeaveEvent(self, event):
        self.state = "IDLE"

    def dropEvent(self, event):
        self.state = "THINKING"
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.process_uploaded_file(file_path)
        event.acceptProposedAction()

    def select_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Present File to Diablo", "", "All Supported Files (*.pdf *.docx *.txt *.csv *.py *.json *.png *.jpg);;All Files (*)")
        if file_path:
            self.process_uploaded_file(file_path)

    def process_uploaded_file(self, file_path: str):
        try:
            res = self.doc_mgr.read_any_file(file_path)
            # Ingest into ChromaDB Memory
            doc_id = f"doc_{os.path.basename(file_path)}_{math.floor(os.path.getmtime(file_path))}"
            if res['text']:
                self.memory.ingest_text(res['text'][:4000], source=res['filename'], doc_id=doc_id)
            
            preview = res['text'][:120].replace('\n', ' ') if res['text'] else "Binary content"
            reply = f"I have read and committed '{res['filename']}' ({res['size_kb']} KB) to my memory: \"{preview}...\""
            self.state = "SPEAKING"
            self.set_speech(reply, duration=8)
            self.voice.speak(reply, async_mode=True)
        except Exception as e:
            self.set_speech(f"Failed to process file: {e}", duration=4)
        finally:
            self.state = "IDLE"

    def handle_text_query(self):
        query = self.chat_input.text().strip()
        if not query:
            return
        self.chat_input.clear()
        
        self.state = "THINKING"
        self.set_speech(f"Consulting records for: '{query}'...", duration=2)
        QTimer.singleShot(200, lambda: self.execute_intelligent_action(query))

    def execute_intelligent_action(self, query: str):
        q = query.lower().strip()
        reply = ""
        
        try:
            # 1. Direct File Path Inspection ("check file C:\..." or "read C:\...")
            clean_q = query.strip("\"' ")
            if (os.path.exists(clean_q) and os.path.isfile(clean_q)) or (len(query.split()) > 1 and os.path.exists(query.split()[-1].strip("\"' "))):
                target_path = clean_q if os.path.exists(clean_q) else query.split()[-1].strip("\"' ")
                self.process_uploaded_file(target_path)
                return

            # 2. Dropzone & Folder Organization
            if any(k in q for k in ["organize", "dropzone", "clean file", "sort file"]):
                staged = self.organizer.scan_and_stage_dropzone()
                if staged:
                    reply = f"I have categorized and staged {len(staged)} file(s) from Dropzone for your approval."
                else:
                    reply = "The Dropzone is completely clear, Lord Ivine. No unorganized files found."

            # 3. Document Creation (Word)
            elif "create doc" in q or "make doc" in q or "word file" in q:
                topic = query.replace("create doc", "").replace("make doc", "").replace("word file", "").strip() or "General Briefing"
                path = self.doc_mgr.create_word_doc(f"Diablo Report: {topic.title()}", [f"Subject: {topic}", "Generated autonomously under Prime Directives.", "Awaiting review."])
                reply = f"Word document created successfully at: {path}"

            # 4. Document Creation (Excel)
            elif "create sheet" in q or "make excel" in q or "spreadsheet" in q:
                path = self.doc_mgr.create_excel_sheet(["Item", "Metric", "Status"], [["System", "RTX 4060", "Online"], ["Diablo Memory", "ChromaDB", "Optimal"]])
                reply = f"Excel spreadsheet generated at: {path}"

            # 5. Meeting Secretary
            elif "start meeting" in q:
                title = query.replace("start meeting", "").strip() or "Executive Session"
                self.secretary.start_meeting(title)
                reply = f"Meeting '{title}' recording initiated. Standing by to transcribe."
            elif "end meeting" in q or "stop meeting" in q:
                path = self.secretary.end_meeting()
                reply = f"Meeting finalized. Summary and transcript archived at: {path}" if path else "No active meeting recording found."

            # 6. System Controls
            elif "lock screen" in q or "lock laptop" in q:
                self.system_ctrl.lock_screen()
                reply = "Workstation locked as requested."
            elif "open " in q:
                app_name = q.replace("open ", "").strip()
                if self.system_ctrl.open_approved_app(app_name):
                    reply = f"Opened {app_name} from the approved allow-list."
                else:
                    reply = f"Application '{app_name}' is not in the approved allow-list (Prime Directive #1)."

            # 7. Memory Ingestion ("remember ...")
            elif q.startswith("remember ") or q.startswith("save note "):
                note = query.replace("remember ", "").replace("save note ", "").strip()
                self.memory.ingest_text(note, source="user_verbal_note", doc_id=f"user_note_{math.floor(os.path.getmtime('main.py'))}")
                reply = f"Kufufufu... That knowledge has been engraved into my permanent memory, Lord Ivine."

            # 8. Conversational & RAG Memory Search
            elif "who are you" in q:
                reply = "I am Diablo, Primordial Black. It is my eternal honor to serve as your personal AI butler. Kufufufu..."
            elif "system status" in q or "headroom" in q:
                hr = self.governor.check_system_headroom()
                reply = f"Status: Profile={self.governor.current_profile}, RAM={hr['ram_used_percent']}%, CPU={hr['cpu_percent']}%. All systems optimal."
            else:
                # Semantic RAG Search
                res = self.memory.search(query, n_results=1)
                if res:
                    reply = f"From your records: {res[0]}"
                else:
                    reply = f"Understood, Lord Ivine. '{query}' has been registered into my records."

            self.state = "SPEAKING"
            self.set_speech(reply, duration=7)
            self.voice.speak(reply, async_mode=True)
        except Exception as e:
            self.set_speech(f"Error executing command: {e}", duration=4)
        finally:
            self.state = "IDLE"

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        current_prof = self.profiles[self.profile_idx]

        # 1. Draw Speech Bubble
        if self.speech_opacity > 0:
            bubble_rect = QRectF(25, 10, 310, 80)
            painter.setOpacity(self.speech_opacity)
            painter.setBrush(QColor(17, 24, 39, 240))
            
            border_color = QColor(245, 158, 11) if current_prof == "MAX_PERFORMANCE" else QColor(239, 68, 68)
            painter.setPen(QPen(border_color, 1.5))
            painter.drawRoundedRect(bubble_rect, 12, 12)

            # Title
            painter.setPen(border_color)
            painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
            voice_tag = "🔊 VOICE ON" if self.voice.voice_enabled else "🔇 SILENT MODE"
            painter.drawText(QRectF(35, 16, 290, 15), Qt.AlignmentFlag.AlignLeft, f"DIABLO  •  {current_prof}  •  {voice_tag}")

            # Dialogue Text
            painter.setPen(QColor(243, 244, 246))
            painter.setFont(QFont("Segoe UI", 9))
            painter.drawText(QRectF(35, 34, 290, 52), Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap, self.speech_text)

        painter.setOpacity(1.0)

        center_x = 180
        center_y = 210
        float_y = math.sin(self.float_phase) * 6.0 if current_prof != "POWER_SAVER" else 0.0

        # === MODE 1: POWER_SAVER (Compact Gaming Sigil) ===
        if current_prof == "POWER_SAVER":
            if not self.pixmap_seal.isNull():
                mini_size = 90
                painter.save()
                painter.translate(center_x, center_y)
                painter.rotate(self.rotation_angle)
                painter.setOpacity(0.85)
                painter.drawPixmap(int(-mini_size/2), int(-mini_size/2), mini_size, mini_size, self.pixmap_seal)
                painter.restore()
                
                painter.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
                painter.setPen(QColor(156, 163, 175))
                painter.drawText(QRectF(center_x - 50, center_y + 55, 100, 20), Qt.AlignmentFlag.AlignCenter, "STEALTH MODE")

        # === MODE 2 & 3: BALANCED & MAX PERFORMANCE ===
        else:
            if not self.pixmap_seal.isNull():
                seal_size = 230 if current_prof == "BALANCED" else 255
                painter.save()
                painter.translate(center_x, center_y + float_y)
                painter.rotate(self.rotation_angle)
                painter.setOpacity(0.85 if current_prof == "BALANCED" else 1.0)
                painter.drawPixmap(int(-seal_size / 2), int(-seal_size / 2), seal_size, seal_size, self.pixmap_seal)
                painter.restore()

            if not self.pixmap_avatar.isNull():
                avatar_size = 140
                painter.save()
                painter.translate(center_x, center_y + float_y)
                
                glow_color = QColor(245, 158, 11, 255) if current_prof == "MAX_PERFORMANCE" else QColor(239, 68, 68, 220)
                glow_pen = QPen(glow_color, 4.0 if current_prof == "MAX_PERFORMANCE" else 2.5)
                painter.setPen(glow_pen)
                painter.drawEllipse(QRectF(-avatar_size/2, -avatar_size/2, avatar_size, avatar_size))

                painter.drawPixmap(int(-avatar_size / 2), int(-avatar_size / 2), avatar_size, avatar_size, self.pixmap_avatar)
                painter.restore()

        # 4. Quick Control Dock (With 📎 File Attach Button)
        dock_rect = QRectF(25, 355, 310, 40)
        painter.setBrush(QColor(17, 24, 39, 230))
        painter.setPen(QPen(QColor(55, 65, 81, 180), 1))
        painter.drawRoundedRect(dock_rect, 20, 20)

        painter.setFont(QFont("Segoe UI", 7, QFont.Weight.Bold))
        
        # Mic Btn
        painter.setPen(QColor(239, 68, 68))
        painter.drawText(QRectF(30, 360, 50, 30), Qt.AlignmentFlag.AlignCenter, "🎤 Speak")

        # File Attach Btn
        painter.setPen(QColor(245, 158, 11))
        painter.drawText(QRectF(80, 360, 50, 30), Qt.AlignmentFlag.AlignCenter, "📎 File")

        # Voice Toggle Btn
        painter.setPen(QColor(245, 158, 11) if self.voice.voice_enabled else QColor(156, 163, 175))
        v_label = "🔊 Voice" if self.voice.voice_enabled else "🔇 Mute"
        painter.drawText(QRectF(130, 360, 55, 30), Qt.AlignmentFlag.AlignCenter, v_label)

        # Profile Btn
        painter.setPen(QColor(156, 163, 175))
        prof_text = f"⚡ {current_prof[:4]}"
        painter.drawText(QRectF(185, 360, 50, 30), Qt.AlignmentFlag.AlignCenter, prof_text)

        # Dash / Banish
        painter.setPen(QColor(156, 163, 175))
        painter.drawText(QRectF(235, 360, 45, 30), Qt.AlignmentFlag.AlignCenter, "📊 Web")

        painter.setPen(QColor(239, 68, 68))
        painter.drawText(QRectF(280, 360, 50, 30), Qt.AlignmentFlag.AlignCenter, "🌑 Hide")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            # Click buttons
            if 355 <= pos.y() <= 395:
                if 30 <= pos.x() <= 80:
                    self.trigger_listen()
                    return
                elif 80 <= pos.x() <= 130:
                    self.select_file_dialog()
                    return
                elif 130 <= pos.x() <= 185:
                    self.toggle_voice_output()
                    return
                elif 185 <= pos.x() <= 235:
                    self.toggle_profile()
                    return
                elif 235 <= pos.x() <= 280:
                    webbrowser.open("http://localhost:8000")
                    return
                elif 280 <= pos.x() <= 330:
                    self.hide_hud()
                    return

            if 110 <= pos.x() <= 250 and 140 <= pos.y() <= 280:
                self.trigger_listen()
                return

            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self.drag_position.isNull():
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def toggle_voice_output(self):
        is_on = self.voice.toggle_voice()
        status_msg = "Voice output ENABLED." if is_on else "Silent (Meeting) mode ACTIVATED. Voice muted."
        self.set_speech(status_msg, duration=3)
        if self.tray_icon:
            self.voice_action.setText(f"🔊 Voice Output: {'ON' if is_on else 'MUTED'}")
        if is_on:
            self.voice.speak("Voice output activated.", async_mode=True)

    def trigger_listen(self):
        self.state = "LISTENING"
        self.set_speech("Listening... Speak your command, Lord Ivine.", duration=4)
        QTimer.singleShot(400, self._perform_listen_async)

    def _perform_listen_async(self):
        try:
            text = self.voice.listen(timeout=4)
            if text:
                self.state = "THINKING"
                self.set_speech(f"You said: '{text}'...", duration=2)
                self.execute_intelligent_action(text)
            else:
                self.set_speech("I did not catch a command. Standing by.", duration=3)
        except Exception as e:
            self.set_speech(f"Error: {e}", duration=4)
        finally:
            self.state = "IDLE"

    def toggle_profile(self):
        self.profile_idx = (self.profile_idx + 1) % len(self.profiles)
        p = self.profiles[self.profile_idx]
        self.governor.set_profile(p)
        
        if p == "POWER_SAVER":
            self.set_speech("POWER SAVER: Collapsed to stealth sigil. 0% GPU load.", duration=4)
        elif p == "MAX_PERFORMANCE":
            self.set_speech("MAX PERFORMANCE: Demonic powers awakened to maximum.", duration=4)
        else:
            self.set_speech("BALANCED: Standard butler presence.", duration=3)

    def trigger_halt(self):
        self.state = "HALTED"
        self.governor.emergency_override()
        self.set_speech("EMERGENCY HALT TRIGGERED. System is in read-only idle.", duration=5)

def main():
    app = QApplication(sys.argv)
    hud = DiabloHUD()
    hud.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()