@echo off

if exist "%git_extract_path%" (
    goto :eof
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

echo ^> Done.