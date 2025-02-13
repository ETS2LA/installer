@echo off
setlocal

call helpers\environment.bat

echo Checking requirements...

call helpers\ensure_requirements.bat

echo Requirements are met, starting the app...

python launcher/main.py