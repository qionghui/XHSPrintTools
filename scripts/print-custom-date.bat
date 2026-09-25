@echo off
cd /d "%~dp0\.."
cmd /k python.exe src\main.py --diy_date
