@echo off

if exist "%git_extract_path%" (
    goto :eof
)

if not exist %git_extract_path% (
    if not exist %python_extract_path% (
        echo.
        echo -------------
        echo Welcome!
        echo This installer will now proceed with the following steps:
        echo.
        echo 1. Install Git
        echo 2. Install Python and Pip
        echo 3. Install the required packages for the launcher.
        echo.
        echo These steps will all be performed inside of the current folder.
        echo We will not overwrite any existing installations you might currently have.
        echo.
        echo After installation is complete we will automatically start the launcher.
        echo In the future when starting ETS2LA please use the same start.bat file.
        echo -------------
        echo.
        pause
    )
)

echo Downloading Git from GitHub. Expect a file size of around 63000000 bytes (63 MB)...
echo %git_github_url%
powershell -Command "Invoke-WebRequest -Uri '%git_github_url%' -OutFile '%git_save_path%'"
if %errorlevel% neq 0 (
    echo GitHub download failed. Trying SourceForge, this will take a while...
    echo %git_sourceforge_url%
    powershell -Command "Invoke-WebRequest -Uri '%git_sourceforge_url%' -OutFile '%git_save_path%'"
    if %errorlevel% neq 0 (
        echo SourceForge also failed. Git installation failed!
        pause
        exit /b 1
    )
)

echo ^> Done.
echo Extracting Git, please DO NOT close the window that opened!

if exist "%git_extract_path%" (
    rmdir /s /q "%git_extract_path%"
)

%git_save_path%  -y -o "%git_extract_path%" >nul 2>&1

if exist "%git_save_path%" (
    del "%git_save_path%"
)

echo ^> Done.