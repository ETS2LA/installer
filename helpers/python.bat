@echo off

if exist "%python_extract_path%" (
    goto :eof
)

echo Downloading Python from %python_url%...
powershell -Command "Invoke-WebRequest -Uri '%python_url%' -OutFile '%python_save_path%' -UseBasicParsing"
if %errorlevel% neq 0 (
   echo Python download failed!
   goto :eof
)

echo ^> Done.
echo Extracting Python...

if exist "%python_extract_path%" (
    rmdir /s /q "%python_extract_path%"
)

mkdir "%python_extract_path%" >nul 2>&1
powershell -Command "Expand-Archive -Path '%python_zip_path%' -DestinationPath '%python_extract_path%' -Force"

if exist "%python_zip_path%" (
    del "%python_zip_path%"
)

echo ^> Done.
echo Getting pip...

powershell -Command "Invoke-WebRequest -Uri '%pip_url%' -OutFile '%pip_save_path%' -UseBasicParsing"
if %errorlevel% neq 0 (
   echo Pip download failed!
   goto :eof
)

echo ^> Done.
echo Installing pip...

"%python_extract_path%\python.exe" "%pip_save_path%"

echo ^> Done.
echo Preparing python...

if exist "%pth_file_path%" (
    echo Lib\site-packages >> "%pth_file_path%"
    echo DLLs >> "%pth_file_path%"
    powershell -Command "(gc '%pth_file_path%') -replace '#import site','import site' | Out-File -encoding ASCII '%pth_file_path%'"
) else (
    echo ERROR: File not found: %pth_file_path%
    pause
)

if exist "%python_save_path%" (
    del "%python_save_path%"
)

echo ^> Done.
echo Copying tkinter...
xcopy /E /Y "%tkinter_path%" "%python_extract_path%" >nul 2>&1
echo ^> Done.

echo Downloading build requirements...
:: Install wheel, setuptools and poetry in addition to the launcher requirements
if "%USE_TSINGHUA%"=="1" (
    "%python_extract_path%\python.exe" -m pip install --no-warn-script-location wheel setuptools poetry -i https://mirrors.aliyun.com/pypi/simple

    echo Downloading launcher requirements...
    "%python_extract_path%\python.exe" -m pip install --no-warn-script-location psutil dearpygui GitPython pygetwindow -i https://mirrors.aliyun.com/pypi/simple

    echo Installing DearPyGui-Markdown...
    "%python_extract_path%\python.exe" -m pip install -e "%dpg_markdown%" -i https://mirrors.aliyun.com/pypi/simple
    
) else (
    "%python_extract_path%\python.exe" -m pip install --no-warn-script-location wheel setuptools poetry

    echo Downloading launcher requirements...
    "%python_extract_path%\python.exe" -m pip install --no-warn-script-location psutil dearpygui GitPython pygetwindow

    echo Installing DearPyGui-Markdown...
    "%python_extract_path%\python.exe" -m pip install -e "%dpg_markdown%"
)

echo ^> Done.
echo.