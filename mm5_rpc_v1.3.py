import customtkinter as ctk
import threading
import sys
import urllib.parse
import requests
import re
import time
import win32com.client
from pypresence import Presence
from PIL import Image

# --- CONFIGURATION ---
CLIENT_ID = '1462375131782447321'

# --- THEME SETUP ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class ModernBridgeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window Setup
        self.title("MediaMonkey 5 Bridge (v2.2)")
        self.geometry("500x600")
        self.resizable(False, False)

        # State Variables
        self.rpc = None
        self.mm = None
        self.last_track = ""
        self.is_running = False
        self.current_art_url = "logo"

        # --- GRID LAYOUT ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # 1. HEADER CARD
        self.header_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="#1e1e2e")
        self.header_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        self.status_indicator = ctk.CTkLabel(
            self.header_frame, 
            text="● DISCONNECTED", 
            text_color="#ED4245", 
            font=("Roboto Medium", 14)
        )
        self.status_indicator.pack(pady=(15, 5))

        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="Ready to Connect", 
            font=("Roboto", 20, "bold"),
            text_color="white",
            wraplength=400
        )
        self.title_label.pack(pady=5)

        self.artist_label = ctk.CTkLabel(
            self.header_frame, 
            text="Open MediaMonkey to begin", 
            font=("Roboto", 14), 
            text_color="#a6a6a6"
        )
        self.artist_label.pack(pady=(0, 20))

        # 2. CONTROLS FRAME
        self.btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_frame.grid(row=1, column=0, padx=20, pady=0, sticky="ew")
        
        self.start_btn = ctk.CTkButton(
            self.btn_frame, 
            text="START BRIDGE", 
            command=self.start_bridge,
            font=("Roboto", 14, "bold"),
            fg_color="#5865F2", 
            hover_color="#4752C4",
            height=40,
            corner_radius=20
        )
        self.start_btn.pack(side="left", expand=True, padx=5, fill="x")

        self.stop_btn = ctk.CTkButton(
            self.btn_frame, 
            text="STOP", 
            command=self.stop_bridge,
            font=("Roboto", 14, "bold"),
            fg_color="#2b2d31",
            hover_color="#ed4245",
            state="disabled",
            height=40,
            corner_radius=20
        )
        self.stop_btn.pack(side="right", expand=True, padx=5, fill="x")

        # 3. CONSOLE LOG
        self.log_label = ctk.CTkLabel(self, text="Connection Log", font=("Roboto", 12, "bold"), text_color="#a6a6a6")
        self.log_label.grid(row=2, column=0, padx=25, pady=(20, 0), sticky="w")

        self.log_area = ctk.CTkTextbox(
            self, 
            fg_color="#11111b", 
            text_color="#00ff9d", 
            font=("Consolas", 11),
            corner_radius=10
        )
        self.log_area.grid(row=3, column=0, padx=20, pady=(5, 20), sticky="nsew")

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def log(self, message):
        self.log_area.insert("end", f">> {message}\n")
        self.log_area.see("end")

    def set_status(self, status, color):
        self.status_indicator.configure(text=f"● {status}", text_color=color)

    # --- LOGIC ---
    def start_bridge(self):
        if self.is_running: return
        self.log("Initializing Bridge...")
        try:
            self.rpc = Presence(CLIENT_ID)
            self.rpc.connect()
            self.is_running = True
            
            self.start_btn.configure(state="disabled", fg_color="#2b2d31")
            self.stop_btn.configure(state="normal", fg_color="#ED4245")
            self.set_status("CONNECTED", "#57F287")
            self.log("Discord Connected. Listening for MediaMonkey...")
            self.poll_mediamonkey() 
        except Exception as e:
            self.log(f"Connection Error: {e}")
            self.set_status("ERROR", "#ED4245")

    def stop_bridge(self):
        self.is_running = False
        self.start_btn.configure(state="normal", fg_color="#5865F2")
        self.stop_btn.configure(state="disabled", fg_color="#2b2d31")
        self.set_status("DISCONNECTED", "#ED4245")
        self.title_label.configure(text="Ready to Connect")
        self.artist_label.configure(text="---")
        if self.rpc:
            try: self.rpc.clear()
            except: pass
        self.log("Bridge stopped.")

    def clean_string(self, text):
        return re.sub(r"[\(\[].*?[\)\]]", "", text).strip()

    def fetch_album_art(self, artist, album):
        try:
            clean_artist = self.clean_string(artist)
            clean_album = self.clean_string(album)
            query = urllib.parse.quote(f"{clean_artist} {clean_album}")
            url = f"https://itunes.apple.com/search?term={query}&media=music&entity=album&limit=1"
            response = requests.get(url, timeout=2)
            data = response.json()
            if data['resultCount'] > 0:
                self.current_art_url = data['results'][0]['artworkUrl100'].replace("100x100", "512x512")
                self.log(f"Art Found: {clean_album}")
            else:
                self.current_art_url = "logo"
        except:
            self.current_art_url = "logo"

    def update_discord(self, artist, title, album, start_time=None):
        if not self.rpc: return
        try:
            self.rpc.update(
                state=f"by {artist}",
                details=f"{title}",
                large_image=self.current_art_url,
                large_text=album,
                small_image="play",
                small_text="Playing",
                start=start_time # Only sending Start Time creates "Elapsed" timer
            )
        except: pass

    def poll_mediamonkey(self):
        if not self.is_running: return

        try:
            if self.mm is None:
                self.mm = win32com.client.Dispatch("SongsDB5.SDBApplication")
        except:
            self.mm = None 
            self.set_status("SEARCHING FOR MM5...", "#FEE75C")

        try:
            if self.mm and self.mm.Player.IsPlaying:
                song = self.mm.Player.CurrentSong
                if song:
                    # 1. Get Elapsed Time
                    current_pos_ms = self.mm.Player.PlaybackTime
                    current_pos_sec = current_pos_ms / 1000
                    
                    # 2. Calculate Start Timestamp
                    # (Current Time - Position = Time it started)
                    start_timestamp = int(time.time() - current_pos_sec)

                    track_key = f"{song.ArtistName} - {song.Title}"
                    
                    if track_key != self.last_track:
                        self.last_track = track_key
                        self.log(f"Now Playing: {track_key}")
                        
                        # UI Updates
                        self.set_status("BROADCASTING", "#57F287")
                        self.title_label.configure(text=song.Title)
                        self.artist_label.configure(text=song.ArtistName)
                        
                        self.current_art_url = "logo"
                        threading.Thread(target=self.fetch_album_art, args=(song.ArtistName, song.AlbumName), daemon=True).start()
                    
                    # 3. Send Update
                    self.update_discord(song.ArtistName, song.Title, song.AlbumName, start_time=start_timestamp)

            else:
                if self.last_track != "PAUSED":
                    try: self.rpc.clear()
                    except: pass
                    self.last_track = "PAUSED"
                    self.set_status("IDLE", "#FEE75C")
                    self.title_label.configure(text="Paused")

        except Exception:
            self.mm = None

        self.after(5000, self.poll_mediamonkey)

    def on_close(self):
        self.is_running = False
        self.destroy()
        sys.exit()

if __name__ == "__main__":
    app = ModernBridgeApp()
    app.mainloop()