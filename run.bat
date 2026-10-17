@echo off
taskkill /F /IM python.exe /FI "WINDOWTITLE eq CodeCast*" >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
start "" "C:\Python314\pythonw.exe" "%~dp0main.py"
