# Functionality

## Main Modules

### Embedded PC Player

The PC app uses:

- PyQt6 for the UI
- python-vlc for embedded VLC playback
- VLC desktop as the playback engine

The video is embedded into a Qt widget using VLC window handle binding.

---

## Playlist Handling

The app supports:

- Remote M3U URL loading
- Local M3U/M3U8 file loading
- Basic parsing of:
  - Channel name
  - Group title
  - TVG ID
  - TVG channel number
  - Logo URL
  - Stream URL

---

## Metadata Overlay

When a channel changes, the app displays a temporary overlay on the video with available M3U metadata.

Example:

```text
Channel Name
Group Name
```

---

## True Audio Split

v1.1 creates two separate VLC instances:

- One VLC instance for Main player
- One VLC instance for PiP player

This prevents PiP audio from being dependent on Main volume/mute.

---

## Android Pairing

The PC app exposes a local HTTP API for Android/TV devices.

Main uses:

```text
http://PC-IP:8765
```

Android can poll commands and report current stream state.

---

## Wi-Fi TV Cast

The PC app serves a browser-based TV receiver at:

```text
/tv
```

The TV page polls:

```text
/cast/state
```

When the PC app sends a new channel, the TV receiver swaps its video source.

---

## Not Implemented Yet

These are planned but not fully completed:

- Full Android app production release
- True screen mirroring
- Transcoding streams for incompatible TVs
- Complete XMLTV EPG parser
- Chromecast protocol integration
- DLNA renderer discovery
