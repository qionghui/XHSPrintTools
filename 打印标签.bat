@echo off
cd /d "%~dp0"
start "" pythonw.exe server.py
cmd /k python.exe main.py