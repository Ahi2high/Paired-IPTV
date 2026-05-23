# AHI IPTV Paired Player

AHI IPTV Paired Player is a Windows IPTV player with local-network pairing features for Android and TV devices. It can load M3U/M3U8 IPTV playlists, play channels through an embedded VLC player, manage main/PiP audio separately, and cast selected channels to a TV browser over Wi-Fi.

This project is built for experimenting with a paired IPTV setup where a PC, Android device, and TV can communicate over the same local network.

---

## Features

### Windows IPTV Player

- Embedded VLC video playback inside the app window
- Load remote M3U / M3U8 playlist URLs
- Load local M3U / M3U8 playlist files
- Channel list with search and group filtering
- Channel metadata overlay when switching channels
- Fullscreen support with `F11`
- Separate Main player and PiP player audio
- Main volume and mute controls
- PiP volume and mute controls
- Optional auto-mute main player when PiP opens
- GPU decode options:
  - `d3d11va`
  - `dxva2`
  - `auto`
  - `none`
- Network cache settings

### Pairing / Network Features

- Local HTTP pairing server
- QR pairing page for Android
- Send selected PC channel to Android
- Receive Android stream state on PC
- Open Android stream as PiP on PC
- Wi-Fi TV Cast receiver page
- Cast selected IPTV stream to a TV browser on the same Wi-Fi

### Wi-Fi TV Cast

The PC app hosts a browser receiver page at:

```text
http://YOUR-PC-IP:8765/tv
