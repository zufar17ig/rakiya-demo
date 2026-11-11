@echo off
cd /d "%~dp0"
title Rakiya - Phone Backend
.venv\Scripts\python.exe -u launch_phone.py
if errorlevel 1 pause
