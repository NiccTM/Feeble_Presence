<p align="center">
  <img src="logo.ico" alt="Feeble Presence Logo" width="128"/>
</p>

# 🎵 Feeble Presence (v1.5)
**A High-Performance MediaMonkey 5 to Discord Rich Presence Bridge**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MediaMonkey 5](https://img.shields.io/badge/MediaMonkey-5.0%2B-orange.svg)](https://www.mediamonkey.com/)

---

## 🚀 Overview
**Feeble Presence** is an engineering-focused utility that bridges your local **MediaMonkey 5** playback with **Discord Rich Presence**. It monitors your media library via the COM interface and dynamically updates your profile with high-quality metadata and artwork.

## ✨ Key Features
* **Dynamic Metadata Sync:** Real-time broadcasting of Track Title, Artist, and Album info.
* **Intelligent Artwork Discovery:** Automatically fetches high-resolution album covers via the iTunes Search API.
* **Unobtrusive Design:** Minimizes completely to the Windows System Tray to keep your workspace clean.
* **Interactive Rich Presence:** Includes "Listen on YouTube" and "Search Apple Music" buttons for your Discord friends.
* **Robust Configuration:** Persistent `config.json` allows for auto-connect and customizable update intervals.

## 🛠️ Technical Specifications
* **Frontend:** `CustomTkinter` for a modern, hardware-accelerated dark theme UI.
* **Automation:** Interfaces with the `SongsDB5.SDBApplication` COM object via `pywin32`.
* **Network:** Asynchronous threading for artwork fetching to ensure zero UI lag.
* **Asset Management:** Custom multi-layer `.ico` handling (16px to 256px) for native Windows title bar and taskbar compatibility.

## 📦 Getting Started

### Installation
1.  **Clone the Repository:**
    ```powershell
    git clone [https://github.com/NiccTM/MediaMonkey5-Discord-RPC.git](https://github.com/NiccTM/MediaMonkey5-Discord-RPC.git)
    ```
2.  **Install Dependencies:**
    ```powershell
    pip install -r requirements.txt
    ```

### Running the App
Launch the bridge directly from source:
```powershell
python feeble_presence_v1.5.py
