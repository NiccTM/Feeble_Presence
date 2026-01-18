import tkinter as tk
from tkinter import scrolledtext
import sys
import threading
import time
import urllib.parse
import requests
import re  # <--- NEW: For cleaning text
import win32com.client
from pypresence import Presence

# --- CONFIGURATION ---
CLIENT_ID = '1462375131782447321' 

class MM5RPCApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MM5 Discord Bridge (v1.2)")
        self.root.geometry("450x350")
        self.root.configure(bg="#2C2F33")

        self.rpc = None
        self.mm = None
        self.last_track = ""
        self.is_running = False
        self.current_art_url = "logo"

        # --- UI SETUP ---
        self.status_label = tk.Label(root, text="Status: READY", fg="#99AAB5", bg="#2C2F33", font=("Segoe UI", 12, "bold"))
        self.status_label.pack(pady=10)

        self.track_label = tk.Label(root, text="Click Start to connect", fg="#FFFFFF", bg="#2C2F33", font=("Segoe UI", 10))
        self.track_label.pack(pady=5)

        btn_frame = tk.Frame(root, bg="#2C2F33")
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(btn_frame, text="Start Bridge", command=self.start_bridge, bg="#5865F2", fg="white", width=15, font=("Segoe UI", 9, "bold"), relief="flat")
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(btn_frame, text="Stop", command=self.stop_bridge, bg="#ED4245", fg="white", width=15, font=("Segoe UI", 9, "bold"), relief="flat", state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.log_area = scrolledtext.ScrolledText(root, height=10, bg="#23272A", fg="#00FF00", font=("Consolas", 9))
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def log(self, message):
        self.log_area.insert(tk.END, f">> {message}\n")
        self.log_area.see(tk.END)

    def start_bridge(self):
        if self.is_running: return
        self.log("Connecting to Discord...")
        try:
            self.rpc = Presence(CLIENT_ID)
            self.rpc.connect()
            self.is_running = True
            self.start_btn.config(state=tk.DISABLED, bg="#4f545c")
            self.stop_btn.config(state=tk.NORMAL, bg="#ED4245")
            self.status_label.config(text="Status: ACTIVE", fg="#57F287")
            self.log("Connected! Polling MediaMonkey...")
            self.poll_mediamonkey() 
        except Exception as e:
            self.log(f"Discord Connection Failed: {e}")

    def stop_bridge(self):
        self.is_running = False
        self.start_btn.config(state=tk.NORMAL, bg="#5865F2")
        self.stop_btn.config(state=tk.DISABLED, bg="#4f545c")
        self.status_label.config(text="Status: STOPPED", fg="#ED4245")
        if self.rpc:
            try: self.rpc.clear()
            except: pass
        self.log("Bridge stopped.")

    def clean_string(self, text):
        """Removes [...], (...), and extra junk to help iTunes find matches"""
        # Remove text in brackets [ ] and parentheses ( )
        text = re.sub(r"[\(\[].*?[\)\]]", "", text)
        return text.strip()

    def fetch_album_art(self, artist, album):
        """Searches iTunes API with a CLEANED string"""
        try:
            # Clean the names first!
            clean_artist = self.clean_string(artist)
            clean_album = self.clean_string(album)
            
            query = f"{clean_artist} {clean_album}"
            encoded_query = urllib.parse.quote(query)
            
            # iTunes API Search
            url = f"https://itunes.apple.com/search?term={encoded_query}&media=music&entity=album&limit=1"
            response = requests.get(url, timeout=2)
            data = response.json()
            
            if data['resultCount'] > 0:
                art_url = data['results'][0]['artworkUrl100'].replace("100x100", "512x512")
                self.current_art_url = art_url
                self.log(f"Art Found for: {clean_album}")
            else:
                self.current_art_url = "logo"
                self.log(f"Art NOT found. Searched: '{query}'")
        except Exception as e:
            self.current_art_url = "logo"
            # self.log(f"Art Error: {e}") # Uncomment to debug

    def update_discord(self, artist, title, album):
        if not self.rpc: return
        try:
            self.rpc.update(
                state=f"by {artist}",
                details=f"{title}",
                large_image=self.current_art_url,
                large_text=album,
                small_image="play",
                small_text="Playing"
            )
        except: pass

    def poll_mediamonkey(self):
        if not self.is_running: return

        try:
            if self.mm is None:
                self.mm = win32com.client.Dispatch("SongsDB5.SDBApplication")
        except Exception:
            self.mm = None 
            self.status_label.config(text="Status: SEARCHING...", fg="#FEE75C")

        try:
            if self.mm and self.mm.Player.IsPlaying:
                song = self.mm.Player.CurrentSong
                if song:
                    track_key = f"{song.ArtistName} - {song.Title}"
                    
                    if track_key != self.last_track:
                        self.last_track = track_key
                        self.log(f"Playing: {track_key}")
                        self.status_label.config(text="Status: BROADCASTING", fg="#57F287")
                        self.track_label.config(text=track_key)
                        
                        self.current_art_url = "logo"
                        
                        # Start background search with the raw data (cleaning happens inside)
                        threading.Thread(target=self.fetch_album_art, args=(song.ArtistName, song.AlbumName), daemon=True).start()
                        
                        self.update_discord(song.ArtistName, song.Title, song.AlbumName)
                    
                    # If art was found after the first update, refresh Discord
                    if self.current_art_url != "logo":
                         self.update_discord(song.ArtistName, song.Title, song.AlbumName)

            else:
                if self.last_track != "PAUSED":
                    try: self.rpc.clear()
                    except: pass
                    self.last_track = "PAUSED"
                    self.status_label.config(text="Status: IDLE", fg="#FEE75C")
                    self.track_label.config(text="Paused / Stopped")

        except Exception:
            self.mm = None

        self.root.after(5000, self.poll_mediamonkey)

    def on_close(self):
        self.is_running = False
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = tk.Tk()
    app = MM5RPCApp(root)
    root.mainloop()