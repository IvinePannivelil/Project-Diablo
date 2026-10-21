@echo off
title Project Diablo
cd /d "%~dp0"
"venv\Scripts\python.exe" main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Diablo encountered an error.
    pause
)