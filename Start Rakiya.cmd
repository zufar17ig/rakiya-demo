@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Please follow the one-time setup in README.md first.
  pause
  exit /b 1
)
title Rakiya - Local Preview
.venv\Scripts\python.exe -u launch.py
if errorlevel 1 (
  echo.
  echo Rakiya could not start. Please share the message above.
  pause
)
