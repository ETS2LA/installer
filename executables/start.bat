@echo off
:: Make sure the current directory is the same
:: as where the script is located.
cd /d %~dp0

call environment.bat
cd app && python main.py

pause