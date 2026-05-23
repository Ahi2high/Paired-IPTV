# Troubleshooting

## App opens but video does not play

Check:

1. VLC desktop is installed.
2. VLC is in the default path:

```text
C:\Program Files\VideoLAN\VLC\vlc.exe
```

3. Run:

```bat
Windows\install-requirements.bat
```

4. Try a known-good HLS `.m3u8` stream.

---

## PiP audio depends on Main volume

Make sure the title bar says:

```text
AHI IPTV Paired Player v1.1 TRUE AUDIO SPLIT
```

Older versions did not fully separate VLC instances.

---

## I cannot hear PiP

Try:

1. Open **Fullscreen + Audio**.
2. Raise **PiP Player Volume**.
3. Click **Unmute PiP** if needed.
4. In the PiP window, raise the PiP volume slider.
5. Confirm Windows Volume Mixer is not muting Python/VLC.

---

## TV Cast page loads but stream does not play

Some TV browsers cannot play all IPTV formats.

Try:

- HLS `.m3u8` streams
- Android TV / Google TV browser
- Fire TV browser
- Xbox Edge
- a different stream codec

This app does not currently transcode streams.

---

## Android cannot connect to PC

Check:

1. PC and Android are on the same Wi-Fi.
2. Windows Firewall allows Python.
3. Use the LAN IP shown in the app.
4. Try opening this from the phone browser:

```text
http://YOUR-PC-IP:8765/pair
```

---

## Port already in use

Change the port in:

```text
Windows/config/settings.json
```

Edit:

```json
"pc_server_port": 8765
```

Then restart the app.
