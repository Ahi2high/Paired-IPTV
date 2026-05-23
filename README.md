# AHI IPTV Paired Player

**AHI IPTV Paired Player** is a local-network IPTV player system for Windows with Android/TV pairing support.  
The Windows app can load IPTV M3U/M3U8 playlists, play streams through an embedded VLC player, pair with an Android device, open an Android stream in PiP, and cast selected IPTV streams to a TV receiver page over Wi-Fi.

This app is in conjuction with[https://github.com/Ahi2high/Paired-IPTV-Android]

> Current release: **v1.1 TRUE AUDIO SPLIT**

---

## Features

### Windows PC App

- Embedded VLC video playback inside the app window
- Load remote M3U / M3U8 playlist URLs
- Load local M3U / M3U8 playlist files
- Channel list with group filtering and search
- Channel metadata overlay on video when changing channels
- Fullscreen mode with **F11**
- Wi-Fi TV receiver page served from the PC
- QR pairing page for Android
- Send selected channel to Android
- Receive Android current stream and open it as PC PiP
- Separate audio handling for main player and PiP player
- Separate Main Volume and PiP Volume controls
- Separate Main Mute and PiP Mute controls
- Optional auto-mute main player when PiP opens
- GPU decode settings:
  - `d3d11va`
  - `dxva2`
  - `auto`
  - `none`
- Network cache setting

### Android / TV Concept

The Android side is intended to pair with the PC app over Wi-Fi and use the PC server API to exchange channel URLs.  
The current repo focuses on the Windows app package. The Android folder currently contains notes from the paired-app plan and should be rebuilt/tested separately before release.

### Wi-Fi TV Cast

The PC app serves a simple TV receiver web page:

```text
http://YOUR-PC-IP:8765/tv
```

Open that page on a Smart TV browser, Android TV browser, Fire TV browser, Xbox Edge, or another device on the same Wi-Fi. Then select a channel in the PC app and click **Cast TV**.

This is **URL-based casting**, not desktop mirroring. The TV device plays the IPTV stream URL directly.

---

## Folder Structure

```text
AHI-IPTV-Paired-Player/
├── Windows/
│   ├── app/
│   │   └── ahi_iptv_pc_v1.py
│   ├── config/
│   │   └── settings.json
│   ├── install-requirements.bat
│   ├── run-windows.bat
│   ├── build-exe.bat
│   └── requirements.txt
├── Android/
│   └── README_ANDROID.md
├── Shared/
│   └── docs/
├── docs/
│   ├── USAGE.md
│   ├── FUNCTIONALITY.md
│   ├── NETWORK_API.md
│   └── TROUBLESHOOTING.md
├── LICENSE
├── .gitignore
├── CHANGELOG.md
└── README.md
```

---

## Requirements

### Windows

- Windows 10 or Windows 11
- Python 3.10+
- VLC Media Player desktop install
- Same Wi-Fi/LAN for pairing and TV casting

Install VLC from VideoLAN and keep the default path if possible:

```text
C:\Program Files\VideoLAN\VLC\vlc.exe
```

Python packages are installed by the provided batch file:

```text
PyQt6
python-vlc
qrcode[pil]
```

---

## Quick Start

### 1. Install VLC

Install the regular desktop version of VLC.

### 2. Install Python requirements

Open the repo folder and run:

```bat
cd Windows
install-requirements.bat
```

### 3. Run the app

```bat
run-windows.bat
```

The app title should show:

```text
AHI IPTV Paired Player v1.1 TRUE AUDIO SPLIT
```

### 4. Load an IPTV playlist

Use either:

- **TV Player → Load M3U URL**
- **M3U / Lists → Load Remote M3U URL**
- **TV Player → Open M3U**

Paste your playlist URL or choose a local `.m3u` / `.m3u8` file.

### 5. Play a channel

Click a channel in the list. The embedded VLC player should begin playback.

---

## Fullscreen

- Press **F11** in the main app to toggle fullscreen.
- Press **Esc** to exit fullscreen.
- Use the **Fullscreen / F11** button on the TV Player tab.
- Use **PiP Fullscreen** for the Android PiP window.

---

## Separate Audio / PiP Audio

Release **v1.1 TRUE AUDIO SPLIT** separates the VLC backend used for the main player and the PiP player.

This means:

- Main volume controls only the main player.
- PiP volume controls only PiP.
- Main mute does not mute PiP.
- PiP mute does not mute Main.
- PiP has its own volume slider inside the PiP window.

Recommended test:

```text
1. Play a channel on PC.
2. Open Android PiP.
3. Main should auto-mute by default.
4. Raise PiP volume inside the PiP window.
5. PiP should stay audible even while Main is muted or low.
```

---

## Wi-Fi TV Cast Usage

1. Start the PC app.
2. Go to **WiFi TV Cast**.
3. Copy the TV receiver URL:

```text
http://YOUR-PC-IP:8765/tv
```

4. Open that URL on your TV browser or another device on the same Wi-Fi.
5. Load your M3U playlist on the PC app.
6. Select a channel.
7. Click **Cast TV**.

### Notes

- HLS `.m3u8` streams are usually the most browser-friendly.
- Some TVs cannot play certain codecs or raw transport streams.
- If your Smart TV browser fails, try:
  - Android TV / Google TV browser
  - Fire TV browser
  - Xbox Edge
  - a browser-capable streaming device

---

## Build EXE

To build a Windows EXE:

```bat
cd Windows
build-exe.bat
```

The output should be placed in:

```text
Windows/dist/AHI_IPTV_PC_v1_1/
```

---

## GitHub Upload

To push this repo to GitHub:

```bat
git init
git add .
git commit -m "Initial release: AHI IPTV Paired Player v1.1"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/AHI-IPTV-Paired-Player.git
git push -u origin main
```

---

## Legal / Content Notice

This project is an IPTV player/client. It does **not** include IPTV channels, playlists, copyrighted streams, or subscription content.

Only use playlists and streams you own, created, or are authorized to access.

---

## License

MIT License. See [LICENSE](LICENSE).
