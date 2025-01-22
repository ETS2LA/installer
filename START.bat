@echo off
set FILE_PATH="checked.txt"

if not exist %FILE_PATH% (
    echo You didnt run the RUN_THIS_FIRST.bat ! Please exit and run the RUN_THIS_FIRST.bat !
    pause
    exit
)



if NOT EXIST code (
    echo - Error: code folder not found
    echo.
    echo Please make sure the file is being run from the correct directory.
    echo.
    pause
    exit
)

IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
    venv\Scripts\python.exe -m pip install --upgrade pip
    echo Virtual environment created
)

echo Activating virtual environment...
cd venv\Scripts
call activate
cd ..
cd ..
echo + Done

echo Checking requirements...
pip install -q -r code/requirements.txt
echo + Done

echo Running the installer / app...
timeout /t 1 /nobreak >nul
cls

cd code
python installer.py
