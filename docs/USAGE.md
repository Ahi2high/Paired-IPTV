# Usage Guide

## Running the Windows App

```bat
cd Windows
install-requirements.bat
run-windows.bat
```

The title bar must say:

```text
AHI IPTV Paired Player v1.1 TRUE AUDIO SPLIT
```

If it does not, you are running an older folder.

---

## Loading a Playlist

### Remote URL

1. Go to **TV Player**.
2. Paste a remote M3U/M3U8 playlist URL into **Load M3U URL**.
3. Click **Load URL Playlist**.

### Local File

1. Go to **TV Player**.
2. Click **Open M3U**.
3. Select a `.m3u` or `.m3u8` file.

---

## Playing Channels

Click a channel in the left-side list. Playback starts in the embedded VLC player.

Double-click can also play the selected channel.

---

## Fullscreen

Main app:

```text
F11 = fullscreen
Esc = exit fullscreen
```

PiP window:

```text
F11 = fullscreen
Esc = exit fullscreen
```

---

## Audio Controls

Go to **Fullscreen + Audio**.

Controls:

- Main Player Volume
- PiP Player Volume
- Mute Main
- Mute PiP
- Auto-mute main player when PiP opens

PiP also has its own volume and mute controls inside the PiP window.

---

## Pair Android

1. Start the PC app.
2. Go to **Pair Android**.
3. Use the QR code or Pair URL.
4. Android should connect to:

```text
http://YOUR-PC-IP:8765
```

The Android side is planned/experimental in this repo.

---

## Wi-Fi TV Cast

1. Start PC app.
2. Go to **WiFi TV Cast**.
3. Open the TV URL on your TV browser:

```text
http://YOUR-PC-IP:8765/tv
```

4. Select a channel on PC.
5. Click **Cast TV**.

This sends the stream URL to the TV receiver page.
