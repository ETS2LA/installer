@echo off
:: Check if python is version 3.11 or 3.12
python --version 2>&1 | findstr /R /C:"Python 3\.[1][12]\." >nul
if errorlevel 1 goto errorNoPython
    echo + Compatible python version found

:: Check if npm is installed
where npm >nul 2>nul
if errorlevel 1 goto errorNoNPM
    echo + Compatible npm version found    

:: Check if git is installed
where git >nul 2>nul
if errorlevel 1 goto errorNoGit
    echo + Compatible git version found

goto:end

:errorNoPython
echo - Error^: Python not installed
echo.
echo Please install either python 3.11 or 3.12 and make sure it is set as the default python installation.
echo https://www.python.org/downloads/release/python-3119/  -  Scroll down and download "Windows installer (64-bit)"
echo Make sure to toggle "Add Python to PATH" during installation.
echo.
pause
exit

:errorNoNPM
echo - Error^: NPM not installed
echo ? Continuing will try and install Node automatically, CTRL+C to cancel
pause
python helpers/download_node.py
echo.
echo Please restart the script to check if Node was installed correctly.
echo If it's not working then you can install it manually from https://nodejs.org/en
pause
exit

:errorNoGit
echo - Error^: Git not installed
echo ? Continuing will try and install Git automatically, CTRL+C to cancel
pause
python helpers/download_git.py
echo.
echo Please restart the script to check if Git was installed correctly.
echo If it's not working then you can install it manually from https://git-scm.com/downloads
pause
exit

:end
echo.
echo All prerequisites are installed, you can now run the START file.
pause
