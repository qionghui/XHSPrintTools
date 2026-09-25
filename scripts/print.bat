@echo off
cd /d "%~dp0\.."
start "" pythonw.exe src\server.py
cmd /k python.exe src\main.py
