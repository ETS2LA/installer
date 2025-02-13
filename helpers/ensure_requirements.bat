@echo off

call helpers\environment.bat
call helpers\git.bat
call helpers\python.bat

echo Git Version:
%git_extract_path%\bin\git.exe --version
echo.

echo Python Version:
%python_extract_path%\python.exe  --version
echo.

echo Pip Version:
%python_extract_path%\python.exe -m pip --version
echo.

echo Pip Packages:
%python_extract_path%\python.exe -m pip list
echo.