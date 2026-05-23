
import os, sys, json, time, socket, threading, urllib.request, urllib.parse
from pathlib import Path
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QShortcut, QKeySequence
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QFileDialog, QLineEdit, QComboBox,
    QTabWidget, QTextEdit, QSlider, QSpinBox, QMessageBox, QFrame, QCheckBox
)

try:
    import vlc
except Exception:
    vlc = None

try:
    import qrcode
except Exception:
    qrcode = None

APP_VERSION = "v1.1 TRUE AUDIO SPLIT"
BASE = Path(__file__).resolve().parents[1]
CONFIG_DIR = BASE / "config"
CONFIG_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = CONFIG_DIR / "settings.json"
LOG_FILE = BASE / "iptv_debug.log"

DEFAULT_SETTINGS = {
    "network_cache_ms": 1500,
    "hardware_accel": "d3d11va",
    "main_volume": 80,
    "pip_volume": 30,
    "main_muted": False,
    "pip_muted": False,
    "auto_mute_main_when_pip": True,
    "pc_server_port": 8765,
    "last_playlist_url": "",
    "last_playlist_path": ""
}

CHANNELS = []
STATE = {
    "current_channel": "",
    "current_url": "",
    "current_group": "",
    "android_current_channel": "",
    "android_current_url": "",
    "pending_android_command": None,
    "cast_name": "",
    "cast_url": "",
    "cast_group": "",
    "cast_ts": 0
}
APP = None

TV_RECEIVER_HTML = """<!doctype html>
<html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>AHI IPTV TV Receiver</title>
<style>
html,body{margin:0;background:#000;color:white;font-family:Segoe UI,Arial;height:100%;overflow:hidden}
#bar{position:absolute;top:18px;left:18px;right:18px;background:rgba(0,0,0,.72);border:1px solid #1b78ff;border-radius:18px;padding:16px 22px;font-size:24px;font-weight:800;z-index:9;display:none}
#hint{position:absolute;bottom:22px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,.75);padding:12px 18px;border-radius:999px;z-index:9;color:#cdd8ef}
video{width:100vw;height:100vh;object-fit:contain;background:#000}
</style></head><body>
<div id='bar'></div><video id='v' controls autoplay playsinline></video><div id='hint'>AHI IPTV TV Receiver - cast from PC</div>
<script>
let last=''; const v=document.getElementById('v'); const bar=document.getElementById('bar');
function show(t){bar.innerText=t;bar.style.display='block';setTimeout(()=>bar.style.display='none',5000)}
async function poll(){try{let r=await fetch('/cast/state?x='+Date.now());let j=await r.json();
if(j.url && j.url!==last){last=j.url; v.src=j.url.split('|')[0]; v.load(); try{await v.play()}catch(e){} show((j.name||'Channel')+'\\n'+(j.group||''));}}
catch(e){}}
setInterval(poll,1500); poll();
document.body.ondblclick=()=>{let e=document.documentElement;if(e.requestFullscreen)e.requestFullscreen();}
</script></body></html>"""

def log(msg):
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"[{time.strftime('%H:%M:%S')}] {msg}\n")

def load_settings():
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            out = DEFAULT_SETTINGS.copy()
            out.update(data)
            return out
        except Exception as e:
            log("settings load failed " + str(e))
    return DEFAULT_SETTINGS.copy()

def save_settings(s):
    SETTINGS_FILE.write_text(json.dumps(s, indent=2), encoding="utf-8")

def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def parse_attrs(line):
    attrs = {}
    for key in ["group-title", "tvg-logo", "tvg-name", "tvg-id", "tvg-chno"]:
        token = key + '="'
        if token in line:
            attrs[key] = line.split(token,1)[1].split('"',1)[0]
    return attrs

def parse_m3u(text):
    out = []
    cur = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line: continue
        if line.startswith("#EXTINF"):
            attrs = parse_attrs(line)
            title = line.split(",",1)[1].strip() if "," in line else attrs.get("tvg-name","Unknown")
            cur = {
                "name": attrs.get("tvg-name") or title or "Unknown",
                "group": attrs.get("group-title") or "All",
                "url": "",
                "tvg_id": attrs.get("tvg-id",""),
                "channel_no": attrs.get("tvg-chno",""),
                "logo": attrs.get("tvg-logo","")
            }
        elif line.startswith("#EXTGRP:") and cur:
            cur["group"] = line.split(":",1)[1].strip() or "All"
        elif line.startswith("#"):
            continue
        else:
            if cur is None:
                cur = {"name": line[:45], "group":"All", "url":"", "tvg_id":"", "channel_no":"", "logo":""}
            cur["url"] = line
            out.append(cur)
            cur = None
    return out

def download_text(url):
    req = urllib.request.Request(url, headers={"User-Agent":"AHI-IPTV/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="ignore")

def clean_url(raw):
    raw = (raw or "").strip()
    opts = []
    if "|" in raw:
        url, pipe = raw.split("|",1)
        for part in pipe.replace("&","|").split("|"):
            if "=" in part:
                k,v = part.split("=",1)
                k=k.strip().lower(); v=urllib.parse.unquote(v.strip())
                if k == "user-agent": opts.append(f":http-user-agent={v}")
                elif k == "referer": opts.append(f":http-referrer={v}")
                elif k == "origin": opts.append(f":http-origin={v}")
        return url.strip(), opts
    return raw, opts

class Api(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type","application/json")
        self.send_header("Access-Control-Allow-Origin","*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)
    def do_GET(self):
        if self.path.startswith("/tv"):
            data = TV_RECEIVER_HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type","text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        elif self.path.startswith("/cast/state"):
            self._json({"name":STATE["cast_name"],"url":STATE["cast_url"],"group":STATE["cast_group"],"ts":STATE["cast_ts"]})
        elif self.path.startswith("/channels"):
            self._json({"channels":CHANNELS})
        elif self.path.startswith("/pair"):
            port = APP.settings["pc_server_port"] if APP else 8765
            self._json({"app":"AHI IPTV","version":APP_VERSION,"url":f"http://{get_lan_ip()}:{port}","tv":f"http://{get_lan_ip()}:{port}/tv"})
        elif self.path.startswith("/next_command"):
            cmd = STATE["pending_android_command"]
            STATE["pending_android_command"] = None
            self._json({"command":cmd})
        elif self.path.startswith("/state"):
            self._json(STATE)
        else:
            self._json({"error":"not found"},404)
    def do_POST(self):
        size = int(self.headers.get("Content-Length","0") or "0")
        body = self.rfile.read(size).decode() if size else "{}"
        try: data=json.loads(body)
        except: data={}
        if self.path.startswith("/command/play_pc"):
            if APP and data.get("url"):
                QTimer.singleShot(0, lambda: APP.play_url(data.get("url",""), data.get("name","Remote"), data))
            self._json({"ok":True})
        elif self.path.startswith("/command/cast_tv"):
            STATE["cast_name"] = data.get("name","")
            STATE["cast_url"] = data.get("url","")
            STATE["cast_group"] = data.get("group","")
            STATE["cast_ts"] = time.time()
            self._json({"ok":True})
        elif self.path.startswith("/android_state"):
            STATE["android_current_channel"] = data.get("name","")
            STATE["android_current_url"] = data.get("url","")
            self._json({"ok":True})
        else:
            self._json({"error":"not found"},404)
    def log_message(self,*args): pass

class VideoBox(QWidget):
    def __init__(self, text):
        super().__init__()
        self.setMinimumSize(640,360)
        self.setStyleSheet("background:#000;border:2px solid #1b78ff;border-radius:14px;")
        lay=QVBoxLayout(self); lay.setContentsMargins(0,0,0,0)
        self.label=QLabel(text); self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color:#60708a;font-size:24px;font-weight:900;")
        lay.addWidget(self.label)
        self.overlay=QLabel(self); self.overlay.hide(); self.overlay.setWordWrap(True)
        self.overlay.setStyleSheet("background:rgba(0,0,0,190);color:white;font-size:20px;font-weight:900;padding:12px;border-radius:12px;")
        self.timer=QTimer(self); self.timer.setSingleShot(True); self.timer.timeout.connect(self.overlay.hide)
    def resizeEvent(self,e):
        self.overlay.setGeometry(18,18,max(300,self.width()-36),78)
        super().resizeEvent(e)
    def show_overlay(self, text):
        self.overlay.setText(text); self.overlay.raise_(); self.overlay.show(); self.timer.start(4500)

class PiPDialog(QDialog):
    def __init__(self, owner):
        super().__init__(owner)
        self.owner=owner
        self.setWindowTitle("AHI IPTV - Android PiP Player")
        self.resize(720,430)
        lay=QVBoxLayout(self)

        self.video=VideoBox("Android PiP")
        lay.addWidget(self.video, 1)

        controls=QHBoxLayout()
        controls.addWidget(QLabel("PiP Vol"))

        self.pip_slider=QSlider(Qt.Orientation.Horizontal)
        self.pip_slider.setRange(0,100)
        self.pip_slider.setValue(int(owner.settings.get("pip_volume",30)))
        self.pip_slider.valueChanged.connect(owner.set_pip_volume)
        controls.addWidget(self.pip_slider, 1)

        self.mute_btn=QPushButton("Unmute PiP" if owner.settings.get("pip_muted") else "Mute PiP")
        self.mute_btn.clicked.connect(owner.toggle_pip_mute)
        controls.addWidget(self.mute_btn)

        fs=QPushButton("Fullscreen / F11")
        fs.clicked.connect(self.toggle_full)
        controls.addWidget(fs)

        close=QPushButton("Close PiP")
        close.clicked.connect(self.close)
        controls.addWidget(close)

        lay.addLayout(controls)

        QShortcut(QKeySequence("F11"), self, activated=self.toggle_full)
        QShortcut(QKeySequence("Esc"), self, activated=self.showNormal)

    def sync_mute_text(self):
        self.mute_btn.setText("Unmute PiP" if self.owner.settings.get("pip_muted") else "Mute PiP")

    def toggle_full(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def closeEvent(self,e):
        try:
            if self.owner.pip_player:
                self.owner.pip_player.stop()
                self.owner.pip_player.release()
        except Exception:
            pass
        self.owner.pip_player=None
        self.owner.pip_dialog=None
        e.accept()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        global APP
        APP = self
        self.settings = load_settings()
        self.channels = []
        self.filtered = []
        self.server = None
        self.main_vlc_instance = None
        self.pip_vlc_instance = None
        self.main_player = None
        self.pip_player = None
        self.pip_dialog = None
        self.setWindowTitle("AHI IPTV Paired Player v1.1 TRUE AUDIO SPLIT")
        self.resize(1600, 900)
        self.init_vlc()
        self.theme()
        self.ui()
        self.start_server()
        QShortcut(QKeySequence("F11"), self, activated=self.toggle_fullscreen)
        QShortcut(QKeySequence("Esc"), self, activated=self.showNormal)

    def theme(self):
        self.setStyleSheet("""
        QWidget,QMainWindow{background:#080b12;color:#eff6ff;font-family:Segoe UI;font-size:14px}
        QLabel#Brand{font-size:30px;font-weight:900;color:white}
        QLabel#Head{font-size:20px;font-weight:900;color:white}
        QLabel#Hint{color:#94a8c8}
        QFrame#Card{background:#0f1521;border:1px solid #263751;border-radius:16px}
        QPushButton{background:#17243a;border:1px solid #2e4b75;border-radius:10px;padding:9px;color:white;font-weight:800}
        QPushButton:hover{background:#1b78ff;border-color:#66d7ff}
        QLineEdit,QComboBox,QSpinBox{background:#05070d;border:1px solid #30445f;border-radius:9px;padding:9px;color:white}
        QListWidget,QTextEdit{background:#05070d;border:1px solid #263751;border-radius:12px;color:white}
        QListWidget::item{padding:10px;border-bottom:1px solid #1a2332}
        QListWidget::item:selected{background:#1b78ff}
        QTabBar::tab{background:#101827;border:1px solid #263751;padding:12px 18px;margin-right:4px;border-top-left-radius:10px;border-top-right-radius:10px}
        QTabBar::tab:selected{background:#1b78ff;color:white}
        """)

    def init_vlc(self):
        """
        Main and PiP use separate VLC instances now.
        This prevents PiP audio from being tied to main volume/mute.
        """
        if vlc is None:
            return
        args=["--quiet"]
        hw=self.settings.get("hardware_accel","d3d11va")
        if hw in ("d3d11va","dxva2"):
            args.append(f"--avcodec-hw={hw}")
        elif hw=="none":
            args.append("--avcodec-hw=none")

        self.main_vlc_instance = vlc.Instance(args)
        self.pip_vlc_instance = vlc.Instance(args)

        self.main_player = self.main_vlc_instance.media_player_new()
        self.main_player.audio_set_volume(int(self.settings.get("main_volume",80)))
        self.main_player.audio_set_mute(bool(self.settings.get("main_muted",False)))

        self.pip_player = None

    def ui(self):
        root=QWidget(); self.setCentralWidget(root)
        main=QVBoxLayout(root)
        top=QHBoxLayout()
        brand=QLabel("AHI IPTV  v1.1 TRUE AUDIO SPLIT"); brand.setObjectName("Brand"); top.addWidget(brand)
        top.addStretch()
        self.server_label=QLabel(""); self.server_label.setObjectName("Hint"); top.addWidget(self.server_label)
        main.addLayout(top)

        self.tabs=QTabWidget(); main.addWidget(self.tabs,1)
        self.tv_tab=QWidget(); self.settings_tab=QWidget(); self.audio_tab=QWidget(); self.pair_tab=QWidget(); self.cast_tab=QWidget()
        self.tabs.addTab(self.tv_tab,"TV Player")
        self.tabs.addTab(self.settings_tab,"M3U / Lists")
        self.tabs.addTab(self.audio_tab,"Fullscreen + Audio")
        self.tabs.addTab(self.pair_tab,"Pair Android")
        self.tabs.addTab(self.cast_tab,"WiFi TV Cast")
        self.build_tv()
        self.build_settings()
        self.build_audio()
        self.build_pair()
        self.build_cast()

    def build_tv(self):
        lay=QHBoxLayout(self.tv_tab)

        left=QFrame(); left.setObjectName("Card"); left.setFixedWidth(395); l=QVBoxLayout(left)
        h=QLabel("Channels"); h.setObjectName("Head"); l.addWidget(h)
        self.group=QComboBox(); self.group.currentTextChanged.connect(self.refresh_list); l.addWidget(self.group)
        self.search=QLineEdit(); self.search.setPlaceholderText("Search channels"); self.search.textChanged.connect(self.refresh_list); l.addWidget(self.search)
        self.list=QListWidget(); self.list.itemClicked.connect(self.item_clicked); self.list.itemDoubleClicked.connect(lambda i:self.play_channel(i.data(Qt.ItemDataRole.UserRole))); l.addWidget(self.list,1)
        row=QHBoxLayout()
        for txt,cb in [("Open M3U",self.open_m3u),("Send Phone",self.send_android),("Cast TV",self.cast_selected_tv)]:
            b=QPushButton(txt); b.clicked.connect(cb); row.addWidget(b)
        l.addLayout(row)

        center=QFrame(); center.setObjectName("Card"); c=QVBoxLayout(center)
        self.video=VideoBox("Embedded VLC Main Player")
        c.addWidget(self.video,1)
        controls=QHBoxLayout()
        for txt,cb in [("Stop",self.stop_main),("Fullscreen / F11",self.toggle_fullscreen),("Android PiP",self.open_pip),("PiP Fullscreen",self.pip_fullscreen)]:
            b=QPushButton(txt); b.clicked.connect(cb); controls.addWidget(b)
        c.addLayout(controls)

        right=QFrame(); right.setObjectName("Card"); right.setFixedWidth(390); r=QVBoxLayout(right)
        nh=QLabel("Now Playing"); nh.setObjectName("Head"); r.addWidget(nh)
        self.now=QLabel("Nothing playing"); self.now.setWordWrap(True); r.addWidget(self.now)
        self.urlbox=QTextEdit(); self.urlbox.setReadOnly(True); self.urlbox.setMaximumHeight(110); r.addWidget(self.urlbox)
        uh=QLabel("Load M3U URL"); uh.setObjectName("Head"); r.addWidget(uh)
        self.url_input=QLineEdit(); self.url_input.setPlaceholderText("Paste remote M3U/M3U8 playlist URL"); self.url_input.setText(self.settings.get("last_playlist_url","")); r.addWidget(self.url_input)
        b=QPushButton("Load URL Playlist"); b.clicked.connect(self.load_url_playlist); r.addWidget(b)
        self.meta=QLabel("Channel/EPG data appears over the video when channel changes."); self.meta.setObjectName("Hint"); self.meta.setWordWrap(True); r.addWidget(self.meta)
        r.addStretch()
        self.debug=QTextEdit(); self.debug.setReadOnly(True); self.debug.setMaximumHeight(180); r.addWidget(self.debug)

        lay.addWidget(left); lay.addWidget(center,1); lay.addWidget(right)

    def build_settings(self):
        l=QVBoxLayout(self.settings_tab)
        h=QLabel("M3U / Playlist Settings"); h.setObjectName("Head"); l.addWidget(h)
        self.remote2=QLineEdit(); self.remote2.setPlaceholderText("Remote M3U URL"); self.remote2.setText(self.settings.get("last_playlist_url","")); l.addWidget(self.remote2)
        b=QPushButton("Load Remote M3U URL"); b.clicked.connect(lambda:self.load_playlist_url(self.remote2.text().strip())); l.addWidget(b)
        b2=QPushButton("Open Local M3U File"); b2.clicked.connect(self.open_m3u); l.addWidget(b2)
        self.info=QTextEdit(); self.info.setReadOnly(True); self.info.setText("Loaded channels will appear in TV Player. Click a channel to play. Metadata overlay appears on top of video."); l.addWidget(self.info,1)

    def build_audio(self):
        l=QVBoxLayout(self.audio_tab)
        h=QLabel("Fullscreen + Separate Audio Controls"); h.setObjectName("Head"); l.addWidget(h)
        row=QHBoxLayout()
        b=QPushButton("Main Fullscreen / F11"); b.clicked.connect(self.toggle_fullscreen); row.addWidget(b)
        b=QPushButton("PiP Fullscreen"); b.clicked.connect(self.pip_fullscreen); row.addWidget(b)
        l.addLayout(row)

        l.addWidget(QLabel("Main Player Volume"))
        self.main_vol=QSlider(Qt.Orientation.Horizontal); self.main_vol.setRange(0,100); self.main_vol.setValue(int(self.settings.get("main_volume",80))); self.main_vol.valueChanged.connect(self.set_main_volume); l.addWidget(self.main_vol)
        self.main_mute=QPushButton("Unmute Main" if self.settings.get("main_muted") else "Mute Main"); self.main_mute.clicked.connect(self.toggle_main_mute); l.addWidget(self.main_mute)

        l.addWidget(QLabel("PiP Player Volume"))
        self.pip_vol=QSlider(Qt.Orientation.Horizontal); self.pip_vol.setRange(0,100); self.pip_vol.setValue(int(self.settings.get("pip_volume",30))); self.pip_vol.valueChanged.connect(self.set_pip_volume); l.addWidget(self.pip_vol)
        self.pip_mute=QPushButton("Unmute PiP" if self.settings.get("pip_muted") else "Mute PiP"); self.pip_mute.clicked.connect(self.toggle_pip_mute); l.addWidget(self.pip_mute)

        self.auto_mute=QCheckBox("Auto-mute main player when PiP opens")
        self.auto_mute.setChecked(bool(self.settings.get("auto_mute_main_when_pip",True)))
        self.auto_mute.stateChanged.connect(self.save_audio_settings)
        l.addWidget(self.auto_mute)

        l.addWidget(QLabel("Hardware decode"))
        self.hw=QComboBox(); self.hw.addItems(["d3d11va","dxva2","auto","none"]); self.hw.setCurrentText(self.settings.get("hardware_accel","d3d11va")); l.addWidget(self.hw)
        l.addWidget(QLabel("Network cache"))
        self.cache=QSpinBox(); self.cache.setRange(0,10000); self.cache.setValue(int(self.settings.get("network_cache_ms",1500))); self.cache.setSuffix(" ms"); l.addWidget(self.cache)
        b=QPushButton("Save Playback Settings + Restart VLC Engine"); b.clicked.connect(self.restart_engine); l.addWidget(b)
        l.addStretch()

    def build_pair(self):
        l=QHBoxLayout(self.pair_tab)
        left=QFrame(); left.setObjectName("Card"); ll=QVBoxLayout(left)
        h=QLabel("Android QR Pair"); h.setObjectName("Head"); ll.addWidget(h)
        self.qr=QLabel(); self.qr.setAlignment(Qt.AlignmentFlag.AlignCenter); self.qr.setMinimumSize(330,330); ll.addWidget(self.qr)
        b=QPushButton("Refresh QR"); b.clicked.connect(self.refresh_qr); ll.addWidget(b)
        right=QFrame(); right.setObjectName("Card"); rr=QVBoxLayout(right)
        self.pair_text=QTextEdit(); self.pair_text.setReadOnly(True); rr.addWidget(self.pair_text)
        l.addWidget(left); l.addWidget(right,1)
        self.refresh_qr()

    def build_cast(self):
        l=QVBoxLayout(self.cast_tab)
        h=QLabel("WiFi TV Cast"); h.setObjectName("Head"); l.addWidget(h)
        self.tv_url=QLineEdit(); self.tv_url.setReadOnly(True); self.tv_url.setText(f"http://{get_lan_ip()}:{self.settings.get('pc_server_port',8765)}/tv"); l.addWidget(self.tv_url)
        row=QHBoxLayout()
        b=QPushButton("Copy TV URL"); b.clicked.connect(lambda: QApplication.clipboard().setText(self.tv_url.text())); row.addWidget(b)
        b=QPushButton("Cast Selected Channel"); b.clicked.connect(self.cast_selected_tv); row.addWidget(b)
        b=QPushButton("Cast Current Playing"); b.clicked.connect(self.cast_current_tv); row.addWidget(b)
        l.addLayout(row)
        self.cast_log=QTextEdit(); self.cast_log.setReadOnly(True); self.cast_log.setText("Open the TV URL on a Smart TV/Android TV/Fire TV/Xbox browser on the same Wi-Fi, then cast a channel."); l.addWidget(self.cast_log,1)

    def start_server(self):
        port=int(self.settings.get("pc_server_port",8765))
        try:
            self.server=ThreadingHTTPServer(("0.0.0.0",port),Api)
            threading.Thread(target=self.server.serve_forever,daemon=True).start()
            self.server_label.setText(f"Pair: http://{get_lan_ip()}:{port}  |  TV: http://{get_lan_ip()}:{port}/tv")
        except Exception as e:
            self.server_label.setText("Server failed: "+str(e))

    def refresh_qr(self):
        url=f"http://{get_lan_ip()}:{self.settings.get('pc_server_port',8765)}"
        payload=json.dumps({"type":"AHI_IPTV_PAIR","url":url})
        self.pair_text.setText(f"Pair URL:\n{url}\n\nTV Cast URL:\n{url}/tv\n\nQR payload:\n{payload}")
        if qrcode:
            p=BASE/"pair_qr.png"
            qrcode.make(payload).save(p)
            self.qr.setPixmap(QPixmap(str(p)).scaled(330,330,Qt.AspectRatioMode.KeepAspectRatio))
        else:
            self.qr.setText(url)

    def open_m3u(self):
        path,_=QFileDialog.getOpenFileName(self,"Open M3U","","M3U (*.m3u *.m3u8);;All (*.*)")
        if path:
            self.settings["last_playlist_path"]=path; save_settings(self.settings)
            txt=Path(path).read_text(encoding="utf-8",errors="ignore")
            self.set_channels(parse_m3u(txt), "local file")

    def load_url_playlist(self):
        self.load_playlist_url(self.url_input.text().strip())

    def load_playlist_url(self,url):
        if not url:
            QMessageBox.warning(self,"Missing URL","Paste an M3U URL first.")
            return
        try:
            self.debug.append("Downloading playlist...")
            txt=download_text(url)
            self.settings["last_playlist_url"]=url
            save_settings(self.settings)
            self.url_input.setText(url); self.remote2.setText(url)
            self.set_channels(parse_m3u(txt), url)
            self.tabs.setCurrentWidget(self.tv_tab)
        except Exception as e:
            QMessageBox.critical(self,"M3U Load Failed",str(e))

    def set_channels(self, ch, source):
        global CHANNELS
        self.channels=ch; CHANNELS=ch
        groups=["All"]+sorted(set([c.get("group","All") or "All" for c in ch]))
        self.group.blockSignals(True); self.group.clear(); self.group.addItems(groups); self.group.blockSignals(False)
        self.refresh_list()
        self.debug.append(f"Loaded {len(ch)} channels from {source}")
        self.info.setText(f"Loaded {len(ch)} channels from {source}")

    def refresh_list(self):
        group=self.group.currentText() if self.group.count() else "All"
        q=self.search.text().lower() if hasattr(self,"search") else ""
        self.list.clear()
        for c in self.channels:
            if group!="All" and c.get("group","All")!=group: continue
            if q and q not in c.get("name","").lower(): continue
            it=QListWidgetItem(f"{c.get('name','Channel')}\n{c.get('group','All')}")
            it.setData(Qt.ItemDataRole.UserRole,c)
            self.list.addItem(it)

    def selected_channel(self):
        it=self.list.currentItem()
        return it.data(Qt.ItemDataRole.UserRole) if it else None

    def item_clicked(self,it):
        c=it.data(Qt.ItemDataRole.UserRole)
        self.show_channel(c)
        self.play_channel(c)

    def show_channel(self,c):
        if not c: return
        self.now.setText(c.get("name","Channel"))
        self.urlbox.setText(c.get("url",""))
        self.meta.setText(f"{c.get('group','All')} | TVG: {c.get('tvg_id','')} | CH: {c.get('channel_no','')}")

    def play_channel(self,c):
        if c: self.play_url(c.get("url",""), c.get("name","Channel"), c)

    def play_url(self, raw, name="Channel", channel=None):
        if vlc is None or self.pip_vlc_instance is None:
            QMessageBox.critical(self,"VLC missing","Install VLC and run install-requirements.bat")
            return
        url,opts=clean_url(raw)
        media=self.main_vlc_instance.media_new(url)
        media.add_option(f":network-caching={int(self.settings.get('network_cache_ms',1500))}")
        for o in opts: media.add_option(o)
        self.main_player.set_media(media)
        if sys.platform.startswith("win"): self.main_player.set_hwnd(int(self.video.winId()))
        elif sys.platform.startswith("linux"): self.main_player.set_xwindow(int(self.video.winId()))
        self.main_player.audio_set_volume(int(self.settings.get("main_volume",80)))
        self.main_player.audio_set_mute(bool(self.settings.get("main_muted",False)))
        self.main_player.play()
        group=channel.get("group","") if isinstance(channel,dict) else ""
        STATE.update({"current_channel":name,"current_url":raw,"current_group":group})
        self.now.setText(name); self.urlbox.setText(raw)
        self.video.show_overlay(f"{name}\n{group}")
        self.debug.append(f"Playing main: {name}")

    def stop_main(self):
        if self.main_player: self.main_player.stop()

    def open_pip(self):
        url=STATE.get("android_current_url")
        name=STATE.get("android_current_channel") or "Android PiP"
        if not url:
            QMessageBox.warning(self,"No Android stream","Android has not reported a current stream yet.")
            return
        if self.pip_dialog:
            self.pip_dialog.raise_()
            self.pip_dialog.activateWindow()
            return
        if vlc is None or self.pip_vlc_instance is None:
            QMessageBox.critical(self,"VLC missing","VLC/Python-VLC is not available.")
            return

        self.pip_dialog=PiPDialog(self)
        self.pip_player=self.pip_vlc_instance.media_player_new()

        clean,opts=clean_url(url)
        media=self.pip_vlc_instance.media_new(clean)
        media.add_option(f":network-caching={int(self.settings.get('network_cache_ms',1500))}")
        for o in opts:
            media.add_option(o)

        self.pip_player.set_media(media)
        if sys.platform.startswith("win"):
            self.pip_player.set_hwnd(int(self.pip_dialog.video.winId()))
        elif sys.platform.startswith("linux"):
            self.pip_player.set_xwindow(int(self.pip_dialog.video.winId()))

        # PiP-only audio. Main volume/mute no longer controls this.
        self.pip_player.audio_set_volume(int(self.settings.get("pip_volume",30)))
        self.pip_player.audio_set_mute(bool(self.settings.get("pip_muted",False)))

        if self.settings.get("auto_mute_main_when_pip",True) and self.main_player:
            self.settings["main_muted"]=True
            self.main_player.audio_set_mute(True)
            self.main_mute.setText("Unmute Main")
            save_settings(self.settings)

        self.pip_dialog.show()
        self.pip_dialog.video.show_overlay(name)
        QTimer.singleShot(250,self.pip_player.play)

    def pip_fullscreen(self):
        if not self.pip_dialog:
            self.open_pip()
        if self.pip_dialog:
            self.pip_dialog.toggle_full()

    def toggle_fullscreen(self):
        self.showNormal() if self.isFullScreen() else self.showFullScreen()

    def set_main_volume(self,v):
        self.settings["main_volume"]=int(v); save_settings(self.settings)
        if self.main_player: self.main_player.audio_set_volume(int(v))

    def set_pip_volume(self,v):
        self.settings["pip_volume"]=int(v)
        save_settings(self.settings)
        if self.pip_player:
            self.pip_player.audio_set_volume(int(v))
        try:
            if hasattr(self,"pip_vol") and self.pip_vol.value()!=int(v):
                self.pip_vol.blockSignals(True)
                self.pip_vol.setValue(int(v))
                self.pip_vol.blockSignals(False)
            if self.pip_dialog and hasattr(self.pip_dialog,"pip_slider") and self.pip_dialog.pip_slider.value()!=int(v):
                self.pip_dialog.pip_slider.blockSignals(True)
                self.pip_dialog.pip_slider.setValue(int(v))
                self.pip_dialog.pip_slider.blockSignals(False)
        except Exception:
            pass

    def toggle_main_mute(self):
        self.settings["main_muted"]=not self.settings.get("main_muted",False)
        if self.main_player: self.main_player.audio_set_mute(self.settings["main_muted"])
        self.main_mute.setText("Unmute Main" if self.settings["main_muted"] else "Mute Main")
        save_settings(self.settings)

    def toggle_pip_mute(self):
        self.settings["pip_muted"]=not self.settings.get("pip_muted",False)
        if self.pip_player:
            self.pip_player.audio_set_mute(bool(self.settings["pip_muted"]))
        self.pip_mute.setText("Unmute PiP" if self.settings["pip_muted"] else "Mute PiP")
        if self.pip_dialog:
            self.pip_dialog.sync_mute_text()
        save_settings(self.settings)

    def save_audio_settings(self):
        self.settings["auto_mute_main_when_pip"]=self.auto_mute.isChecked()
        save_settings(self.settings)

    def restart_engine(self):
        self.settings["hardware_accel"]=self.hw.currentText()
        self.settings["network_cache_ms"]=self.cache.value()
        self.save_audio_settings()
        try:
            if self.main_player:
                self.main_player.stop()
                self.main_player.release()
            if self.pip_player:
                self.pip_player.stop()
                self.pip_player.release()
        except Exception:
            pass
        self.pip_player=None
        if self.pip_dialog:
            self.pip_dialog.close()
        self.init_vlc()
        QMessageBox.information(self,"Restarted","Separate main/PiP VLC engines restarted.")

    def send_android(self):
        c=self.selected_channel()
        if not c or not c.get("url"):
            QMessageBox.warning(self,"No channel","Select a valid channel first.")
            return
        STATE["pending_android_command"]={"action":"play","name":c.get("name","Channel"),"url":c.get("url","")}
        self.debug.append("Queued for Android: "+c.get("name","Channel"))

    def cast_selected_tv(self):
        self.cast_channel(self.selected_channel())

    def cast_current_tv(self):
        if STATE.get("current_url"):
            self.cast_channel({"name":STATE.get("current_channel","Current"),"url":STATE["current_url"],"group":STATE.get("current_group","")})
        else:
            QMessageBox.warning(self,"Nothing playing","No current channel is playing.")

    def cast_channel(self,c):
        if not c or not c.get("url"):
            QMessageBox.warning(self,"No channel","Select a valid channel first.")
            return
        STATE["cast_name"]=c.get("name","Channel")
        STATE["cast_url"]=c.get("url","")
        STATE["cast_group"]=c.get("group","")
        STATE["cast_ts"]=time.time()
        self.cast_log.append(f"Cast TV: {STATE['cast_name']}")
        self.debug.append(f"Cast TV: {STATE['cast_name']}")

    def closeEvent(self,e):
        try:
            if self.main_player: self.main_player.stop()
            if self.pip_player: self.pip_player.stop()
            if self.server: self.server.shutdown()
        except Exception: pass
        e.accept()

if __name__=="__main__":
    app=QApplication(sys.argv)
    w=MainWindow()
    w.show()
    sys.exit(app.exec())
