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


Requirements
Windows
Windows 10 or Windows 11
Python 3.10 or newer
VLC Media Player desktop version
Same Wi-Fi/LAN for Android or TV pairing

VLC should be installed in the default location:

C:\Program Files\VideoLAN\VLC\vlc.exe

Python packages used:

PyQt6
python-vlc
qrcode[pil]
Installation
1. Download or clone the repo
git clone https://github.com/YOUR_USERNAME/AHI-IPTV-Paired-Player.git
cd AHI-IPTV-Paired-Player

Or download the ZIP and extract it.

2. Install VLC

Install VLC Media Player from VideoLAN.

3. Install Python requirements
cd Windows
install-requirements.bat
4. Run the app
run-windows.bat

The title bar should show:

AHI IPTV Paired Player v1.1 TRUE AUDIO SPLIT
How to Use
Load an IPTV playlist

You can load a playlist in two ways.

Remote M3U URL
Open the app.
Go to TV Player.
Paste your M3U/M3U8 playlist URL into the Load M3U URL box.
Click Load URL Playlist.
Local M3U file
Go to TV Player.
Click Open M3U.
Select a .m3u or .m3u8 file.
Playing Channels

After loading a playlist:

Channels appear on the left side.
Use the search box or group filter to find a channel.
Click a channel to play it.
The stream plays inside the embedded VLC player.

When a channel changes, available M3U metadata appears as an overlay on top of the video.

Fullscreen

Main player:

F11 = Toggle fullscreen
Esc = Exit fullscreen

You can also use the Fullscreen / F11 button in the app.

PiP window:

F11 = Toggle PiP fullscreen
Esc = Exit PiP fullscreen
Separate Audio / PiP Audio

Version v1.1 TRUE AUDIO SPLIT uses separate VLC engines for the Main player and PiP player.

This means:

Main volume controls only the main player.
PiP volume controls only the PiP player.
Main mute does not mute PiP.
PiP mute does not mute Main.
PiP has its own volume slider inside the PiP window.

Recommended test:

1. Play a channel on PC.
2. Open Android PiP.
3. Main should auto-mute by default.
4. Raise PiP volume inside the PiP window.
5. PiP should be audible even while Main is muted or low.
Pairing Android

The PC app exposes a local pairing server.

Default address:

http://YOUR-PC-IP:8765

To pair:

Start the PC app.
Go to Pair Android.
Use the QR code or pairing URL.
Android should connect to the PC pairing URL.
Android can receive channel commands and report its current stream back to PC.

The Android side is experimental and should be rebuilt/tested separately before production use.

Wi-Fi TV Cast

To cast a channel to a TV browser:

Start the PC app.
Go to WiFi TV Cast.
Copy the TV receiver URL:
http://YOUR-PC-IP:8765/tv
Open that URL on your TV browser or another device on the same Wi-Fi.
Load your M3U playlist on the PC app.
Select a channel.
Click Cast TV.
Notes
HLS .m3u8 streams usually work best.
Some Smart TV browsers cannot play certain IPTV codecs.
If your TV browser fails, try:
Android TV / Google TV browser
Fire TV browser
Xbox Edge
Another browser-capable streaming device
Build EXE

To package the Windows app as an EXE:

cd Windows
build-exe.bat

The output should appear in:

Windows\dist\AHI_IPTV_PC_v1_1\
Network API

The PC app starts a local HTTP server on port 8765.

Main endpoints:

GET  /pair
GET  /channels
GET  /state
GET  /next_command
GET  /tv
GET  /cast/state
POST /command/play_pc
POST /command/cast_tv
POST /android_state

Example pair URL:

http://192.168.1.25:8765/pair

Example TV receiver URL:

http://192.168.1.25:8765/tv
Troubleshooting
Video does not play

Check that VLC is installed:

C:\Program Files\VideoLAN\VLC\vlc.exe

Then run:

Windows\install-requirements.bat

Try a known-good .m3u8 stream.

PiP has no sound
Go to Fullscreen + Audio.
Raise PiP Player Volume.
Click Unmute PiP.
Check the PiP window’s own volume slider.
Check Windows Volume Mixer.
TV Cast page opens but video does not play

Your TV browser may not support that stream codec. Try a different .m3u8 stream or use Android TV, Fire TV, or Xbox Edge.

Android cannot connect

Check:

- PC and Android are on the same Wi-Fi
- Windows Firewall allows Python
- The PC pairing URL opens from the Android browser

Test from Android browser:

http://YOUR-PC-IP:8765/pair
Legal Notice

This app does not include IPTV channels, playlists, paid streams, or copyrighted content.

Only use playlists and streams that you own, created, or are authorized to access.
