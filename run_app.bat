@echo off
cd /d "%~dp0app"
python main.py
if errorlevel 1 pause
