@echo off
cd /d "%~dp0mobile"
title Rakiya - Native App Preview
if not exist "node_modules" (
  echo Run npm install in the mobile folder first.
  pause
  exit /b 1
)
echo Keep this window open. Scan the QR code using Expo Go on your phone.
call npm.cmd start -- --lan
if errorlevel 1 pause
