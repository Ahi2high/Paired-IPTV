# Network API

The PC app starts a local HTTP server, default port:

```text
8765
```

Base URL:

```text
http://YOUR-PC-IP:8765
```

---

## GET /pair

Returns pairing information.

Example response:

```json
{
  "app": "AHI IPTV",
  "version": "v1.1 TRUE AUDIO SPLIT",
  "url": "http://192.168.1.25:8765",
  "tv": "http://192.168.1.25:8765/tv"
}
```

---

## GET /channels

Returns loaded channels.

```json
{
  "channels": []
}
```

---

## GET /state

Returns current PC, Android, and cast state.

---

## GET /next_command

Android polling endpoint. Returns pending command, if one exists.

---

## POST /command/play_pc

Ask PC to play a stream.

```json
{
  "name": "Example Channel",
  "url": "https://example.com/live.m3u8"
}
```

---

## POST /android_state

Android reports its current channel/URL to the PC app.

```json
{
  "name": "Android Channel",
  "url": "https://example.com/live.m3u8"
}
```

---

## POST /command/cast_tv

Set the active cast target for the TV web receiver.

```json
{
  "name": "Example Channel",
  "url": "https://example.com/live.m3u8",
  "group": "News"
}
```

---

## GET /tv

Browser-based TV receiver page.

---

## GET /cast/state

TV receiver polling endpoint.

```json
{
  "name": "Example Channel",
  "url": "https://example.com/live.m3u8",
  "group": "News",
  "ts": 1710000000
}
```
