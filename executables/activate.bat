@echo off
:: Make sure the current directory is the same
:: as where the script is located.
cd /d %~dp0

cmd /K "call environment.bat"
echo "Environment activated"