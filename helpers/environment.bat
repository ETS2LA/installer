@echo off

:: Git
set "git_github_url=https://github.com/git-for-windows/git/releases/download/v2.47.1.windows.2/PortableGit-2.47.1.2-64-bit.7z.exe"
set "git_sourceforge_url=https://cyfuture.dl.sourceforge.net/project/git-for-windows.mirror/v2.47.1.windows.2/PortableGit-2.47.1.2-64-bit.7z.exe?viasf=1"

set git_save_path="%cd%\PortableGit-2.47.1.2-64-bit.7z.exe"
set git_zip_path="%git_save_path%"
set git_extract_path="%cd%\system\git"

:: Python
set "python_url=https://www.python.org/ftp/python/3.12.8/python-3.12.8-embed-amd64.zip"
set "python_save_path=%cd%\Python-3.12.8.zip"

set "python_zip_path=%python_save_path%"
set "python_extract_path=%cd%\system\python"

set "pth_file_path=%python_extract_path%\python312._pth"

:: Pip
set "pip_url=https://bootstrap.pypa.io/get-pip.py"
set "pip_save_path=%python_extract_path%\get-pip.py"

:: PATH
set PATH=%cd%\system\git\bin;%cd%\system\python;%cd%\system\python\Scripts;%cd%\app;%PATH%

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