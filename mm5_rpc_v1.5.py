import customtkinter as ctk
import threading
import sys
import urllib.parse
import requests
import re
import time
import json
import os
import psutil
import win32com.client
from pypresence import Presence
from PIL import Image
import pystray 

# --- CONFIG ---
DEFAULT_CONFIG = {
    "client_id": "1462375131782447321",
    "update_interval": 3, 
    "plexamp_port": 32500,
    "minimize_to_tray": True,
    "auto_connect": True
}

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

def resource_path(relative_path):
    try: base_path = sys._MEIPASS
    except: base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class FeeblePresenceV21(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config = self.load_config()
        self.title("Feeble Presence v2.1 (Hybrid)")
        self.geometry("500x750")
        self.resizable(False, False)

        # Assets
        self.icon_path = resource_path("logo.ico")
        self.rpc = None
        self.mm = None
        self.last_track = ""
        self.is_running = False
        self.default_art = ctk.CTkImage(Image.new("RGB", (200, 200), (30,30,30)), size=(200, 200))

        self.setup_ui()
        if self.config.get("auto_connect"): self.after(1000, self.start_bridge)

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.header = ctk.CTkFrame(self, corner_radius=15, fg_color="#1e1e2e")
        self.header.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.source_label = ctk.CTkLabel(self.header, text="READY", text_color="#5865F2", font=("Roboto", 10, "bold"))
        self.source_label.pack(pady=10)
        self.art_label = ctk.CTkLabel(self.header, text="", image=self.default_art)
        self.art_label.pack(pady=5)
        self.title_label = ctk.CTkLabel(self.header, text="Media Bridge", font=("Roboto", 20, "bold"))
        self.title_label.pack(pady=5)
        self.artist_label = ctk.CTkLabel(self.header, text="---", text_color="#a6a6a6")
        self.artist_label.pack(pady=2)
        
        self.log_area = ctk.CTkTextbox(self, height=200, fg_color="#11111b", text_color="#00ff9d", font=("Consolas", 11))
        self.log_area.grid(row=3, column=0, padx=20, pady=20, sticky="nsew")
        self.start_btn = ctk.CTkButton(self, text="START BRIDGE", command=self.start_bridge, fg_color="#5865F2")
        self.start_btn.grid(row=1, column=0, pady=5)

    def load_config(self):
        if os.path.exists("config.json"):
            with open("config.json", "r") as f: return json.load(f)
        return DEFAULT_CONFIG

    def log(self, msg):
        self.log_area.insert("end", f">> {msg}\n"); self.log_area.see("end")

    def is_plexamp_running(self):
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] and 'plexamp' in proc.info['name'].lower():
                return True
        return False

    def get_plexamp_info(self):
        try:
            # Direct debug poll (Bypasses the status 404)
            r = requests.get(f"http://127.0.0.1:{self.config['plexamp_port']}/remote/debug/playing", timeout=0.8)
            if r.status_code == 200:
                d = r.json()
                return {"title": d.get('title'), "artist": d.get('artist'), "album": d.get('album')}
        except: pass
        return None

    def start_bridge(self):
        try:
            self.rpc = Presence(self.config["client_id"])
            self.rpc.connect()
            self.is_running = True
            self.log("Feeble Presence Started. Priority: MM5 -> Plexamp")
            self.poll_loop()
        except: self.log("Discord is closed.")

    def poll_loop(self):
        if not self.is_running: return
        found = False

        # 1. MM5 Safe Poll
        try:
            self.mm = win32com.client.GetActiveObject("SongsDB5.SDBApplication")
            if self.mm.Player.IsPlaying:
                song = self.mm.Player.CurrentSong
                self.update_presence("MediaMonkey 5", song.ArtistName, song.Title)
                found = True
        except: self.mm = None

        # 2. Plexamp Direct Poll
        if not found and self.is_plexamp_running():
            data = self.get_plexamp_info()
            if data and data.get('title'):
                self.update_presence("Plexamp", data['artist'], data['title'])
                found = True

        if not found and self.last_track != "IDLE":
            self.rpc.clear(); self.last_track = "IDLE"
            self.source_label.configure(text="IDLE")

        self.after(3000, self.poll_loop)

    def update_presence(self, source, artist, title):
        if f"{artist}{title}" != self.last_track:
            self.last_track = f"{artist}{title}"
            self.log(f"[{source}] {title}")
            self.source_label.configure(text=f"SOURCE: {source.upper()}")
            self.title_label.configure(text=title)
            self.artist_label.configure(text=artist)
            self.rpc.update(state=f"by {artist}", details=title, large_image="logo", small_image="play")

if __name__ == "__main__":
    app = FeeblePresenceV21()
    app.mainloop()