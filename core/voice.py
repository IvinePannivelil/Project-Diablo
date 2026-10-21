import asyncio
import os
import threading
import edge_tts
import pygame
import speech_recognition as sr
import pyttsx3

VOICE_DIR = "ui/assets/cache_audio"
ANIME_VOICES_DIR = "ui/assets/anime_voices"

class VoiceInterface:
    def __init__(self):
        os.makedirs(VOICE_DIR, exist_ok=True)
        os.makedirs(ANIME_VOICES_DIR, exist_ok=True)
        self.voice_enabled = True
        
        # Switched to Christopher (Theatrical, deep, velvety American demon butler - Daman Mills profile)
        self.voice_name = "en-US-ChristopherNeural"
        self.rate = "-8%"
        self.pitch = "-4Hz"
        self.recognizer = sr.Recognizer()
        
        try:
            pygame.mixer.init()
        except Exception:
            pass

    def toggle_voice(self) -> bool:
        self.voice_enabled = not self.voice_enabled
        return self.voice_enabled

    def set_voice_profile(self, voice_name: str, rate: str = "-8%", pitch: str = "-4Hz"):
        self.voice_name = voice_name
        self.rate = rate
        self.pitch = pitch

    def play_anime_sound_clip(self, clip_filename: str) -> bool:
        """Plays authentic anime audio clip if available."""
        clip_path = os.path.join(ANIME_VOICES_DIR, clip_filename)
        if os.path.exists(clip_path) and pygame.mixer.get_init():
            try:
                pygame.mixer.music.load(clip_path)
                pygame.mixer.music.play()
                return True
            except Exception:
                pass
        return False

    def speak(self, text: str, async_mode: bool = True):
        print(f"Diablo: {text}")
        if not self.voice_enabled:
            return

        def _run():
            try:
                # Authentic anime sound triggers
                if "kufufufu" in text.lower() and self.play_anime_sound_clip("laugh.mp3"):
                    return
                if ("at your service" in text.lower() or "welcome" in text.lower()) and self.play_anime_sound_clip("greeting.mp3"):
                    return

                clean_text = text.replace("Kufufufu...", "Kufufufu.")
                audio_path = os.path.join(VOICE_DIR, "speech.mp3")
                
                async def _gen():
                    comm = edge_tts.Communicate(clean_text, self.voice_name, rate=self.rate, pitch=self.pitch)
                    await comm.save(audio_path)

                asyncio.run(_gen())

                if pygame.mixer.get_init():
                    pygame.mixer.music.load(audio_path)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
            except Exception:
                try:
                    engine = pyttsx3.init()
                    engine.setProperty('rate', 150)
                    engine.say(text)
                    engine.runAndWait()
                except Exception:
                    pass

        if async_mode:
            threading.Thread(target=_run, daemon=True).start()
        else:
            _run()

    def greet(self):
        if self.voice_enabled:
            if not self.play_anime_sound_clip("greeting.mp3"):
                self.speak("Kufufufu... At your service, Lord Ivine.", async_mode=True)

    def listen(self, timeout=4) -> str:
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.4)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=8)
                return self.recognizer.recognize_google(audio)
        except Exception:
            return ""