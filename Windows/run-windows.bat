@echo off
title AHI IPTV v1.1 TRUE AUDIO SPLIT
cd /d "%~dp0"
set PATH=C:\Program Files\VideoLAN\VLC;%PATH%
py app\ahi_iptv_pc_v1.py
pause
