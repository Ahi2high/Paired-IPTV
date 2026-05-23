@echo off
title AHI IPTV v1.0 - Install Requirements
cd /d "%~dp0"
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
echo.
echo Install VLC desktop if not installed:
echo C:\Program Files\VideoLAN\VLC\vlc.exe
pause
