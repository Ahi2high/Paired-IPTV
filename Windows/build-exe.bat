@echo off
title Build AHI IPTV v1.1 EXE
cd /d "%~dp0"
py -m pip install pyinstaller -r requirements.txt
set PATH=C:\Program Files\VideoLAN\VLC;%PATH%
py -m PyInstaller --noconfirm --windowed --name AHI_IPTV_PC_v1_1 app\ahi_iptv_pc_v1.py
echo Built at dist\AHI_IPTV_PC_v1_1\AHI_IPTV_PC_v1_1.exe
pause
