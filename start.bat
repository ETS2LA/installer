@echo off
setlocal

set "USE_TSINGHUA=%~1"

if "%USE_TSINGHUA%"=="" (
    echo No mirror specified. Using default PyPI servers.
) else if "%USE_TSINGHUA%"=="1" (
    echo Using Tsinghua mirror...
) else (
    echo Invalid mirror option: %USE_TSINGHUA%
)

echo Checking requirements...

call helpers\ensure_requirements.bat

echo Requirements are met, starting the app...

python launcher/main.py

echo The ETS2LA launcher has closed.