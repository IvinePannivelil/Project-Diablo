@echo off
title Project Diablo - Desktop HUD
cd /d "%~dp0"
"venv\Scripts\python.exe" ui\desktop_overlay.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Diablo encountered an error.
    pause
)