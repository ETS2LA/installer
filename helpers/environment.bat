@echo off

:: Git
set "git_github_url=https://github.com/git-for-windows/git/releases/download/v2.47.1.windows.2/PortableGit-2.47.1.2-64-bit.7z.exe"
set "git_sourceforge_url=https://cyfuture.dl.sourceforge.net/project/git-for-windows.mirror/v2.47.1.windows.2/PortableGit-2.47.1.2-64-bit.7z.exe?viasf=1"
:: Mirror provided by NJU, see https://mirror.nju.edu.cn/ for more information
:: Why no Tsinghua or BFSU mirror: can block the download if used too much.
set "git_tsinghua_url=https://mirror.nju.edu.cn/github-release/git-for-windows/git/Git for Windows v2.48.1.windows.1/PortableGit-2.48.1-64-bit.7z.exe"

set git_save_path="%cd%\PortableGit.7z.exe"
set git_zip_path="%git_save_path%"
set git_extract_path="%cd%\system\git"

:: Python
set "python_url=https://www.python.org/ftp/python/3.12.8/python-3.12.8-embed-amd64.zip"
:: Mirror provided by NJU, see https://mirror.nju.edu.cn/ for more information
:: Why no Tsinghua mirror: it didn't provide python releases mirror.
:: Why no USTC: it will trigger browser verification.
set "python_tsinghua_url=https://mirror.nju.edu.cn/python/3.12.8/python-3.12.8-embed-amd64.zip"
set "python_save_path=%cd%\Python-3.12.8.zip"

set "python_zip_path=%python_save_path%"
set "python_extract_path=%cd%\system\python"

set "pth_file_path=%python_extract_path%\python312._pth"

set "tkinter_path=%cd%\additional_modules\tkinter-standalone-main\3.12\python_embedded"

:: Additional Modules
set "dpg_markdown=%cd%\additional_modules\DearPyGui-Markdown-main"

:: Pip
:: I didn't find any mirror provide get-pip.py
set "pip_url=https://bootstrap.pypa.io/get-pip.py"
set "pip_save_path=%python_extract_path%\get-pip.py"

:: PATH
set PATH=%cd%\system\git\bin;%cd%\system\python;%cd%\system\python\Scripts;%cd%\app;%PATH%

:: Mirror (handle %USE_TSINGHUA%)
:: Git url handle by git.bat
if "%USE_TSINGHUA%"=="1" (
    set "python_url=%python_tsinghua_url%"
)