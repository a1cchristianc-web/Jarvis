"""
JARVIS desktop assistant — main GUI.

Run with:  python3 main.py

Type commands (or click the mic button if you've installed the optional
voice dependencies — see README.md). Say 'help' to see what it can do.
"""

import tkinter as tk
from tkinter import scrolledtext
import datetime

from brain import interpret
from config import ASSISTANT_NAME

# Optional voice support — only loads if the packages are installed.
try:
    import speech_recognition as sr
    import pyttsx3
    VOICE_AVAILABLE = True
except ImportError:
    VOICE_AVAILABLE = False

BG = "#050912"
PANEL = "#0b1220"
ACCENT = "#39d0ff"
ACCENT_DIM = "#1a5f75"
TEXT = "#d7f4ff"
FONT = ("Consolas", 11)
FONT_BOLD = ("Consolas", 12, "bold")


class JarvisApp:
    def __init__(self, root):
        self.root = root
        root.title(ASSISTANT_NAME)
        root.geometry("640x520")
        root.configure(bg=BG)

        if VOICE_AVAILABLE:
            self.tts = pyttsx3.init()
        else:
            self.tts = None

        # Header
        header = tk.Frame(root, bg=BG)
        header.pack(fill="x", padx=16, pady=(16, 8))
        tk.Label(
            header, text=ASSISTANT_NAME, fg=ACCENT, bg=BG, font=("Consolas", 20, "bold")
        ).pack(side="left")
        self.status = tk.Label(header, text="● online", fg="#39ff88", bg=BG, font=FONT)
        self.status.pack(side="right")

        # Output log
        self.log = scrolledtext.ScrolledText(
            root, bg=PANEL, fg=TEXT, insertbackground=TEXT, font=FONT,
            relief="flat", borderwidth=0, wrap="word"
        )
        self.log.pack(fill="both", expand=True, padx=16, pady=8)
        self.log.configure(state="disabled")

        # Input row
        input_row = tk.Frame(root, bg=BG)
        input_row.pack(fill="x", padx=16, pady=(0, 16))

        self.entry = tk.Entry(
            input_row, bg=PANEL, fg=TEXT, insertbackground=TEXT,
            font=FONT, relief="flat"
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=8, padx=(0, 8))
        self.entry.bind("<Return>", self.on_submit)
        self.entry.focus()

        send_btn = tk.Button(
            input_row, text="Send", command=self.on_submit,
            bg=ACCENT_DIM, fg=TEXT, activebackground=ACCENT, relief="flat",
            font=FONT_BOLD, padx=14
        )
        send_btn.pack(side="left")

        if VOICE_AVAILABLE:
            mic_btn = tk.Button(
                input_row, text="🎤", command=self.on_voice,
                bg=ACCENT_DIM, fg=TEXT, activebackground=ACCENT, relief="flat",
                font=FONT_BOLD, padx=10
            )
            mic_btn.pack(side="left", padx=(8, 0))

        self._print(f"{ASSISTANT_NAME} online. Type 'help' to see what I can do.", tag="jarvis")

    def _print(self, text, tag="user"):
        self.log.configure(state="normal")
        ts = datetime.datetime.now().strftime("%H:%M")
        prefix = "you" if tag == "user" else ASSISTANT_NAME
        color = TEXT if tag == "user" else ACCENT
        self.log.insert("end", f"[{ts}] {prefix}: ", ("prefix",))
        self.log.tag_config("prefix", foreground=color, font=FONT_BOLD)
        self.log.insert("end", f"{text}\n\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def handle(self, text):
        if not text.strip():
            return
        self._print(text, tag="user")
        response = interpret(text)
        self._print(response, tag="jarvis")
        if self.tts:
            try:
                self.tts.say(response)
                self.tts.runAndWait()
            except Exception:
                pass

    def on_submit(self, event=None):
        text = self.entry.get()
        self.entry.delete(0, "end")
        self.handle(text)

    def on_voice(self):
        if not VOICE_AVAILABLE:
            return
        r = sr.Recognizer()
        self.status.config(text="● listening", fg="#ffcf39")
        self.root.update()
        try:
            with sr.Microphone() as source:
                audio = r.listen(source, timeout=5, phrase_time_limit=6)
            text = r.recognize_google(audio)
            self.handle(text)
        except Exception as e:
            self._print(f"(couldn't hear you: {e})", tag="jarvis")
        finally:
            self.status.config(text="● online", fg="#39ff88")


if __name__ == "__main__":
    root = tk.Tk()
    app = JarvisApp(root)
    root.mainloop()
