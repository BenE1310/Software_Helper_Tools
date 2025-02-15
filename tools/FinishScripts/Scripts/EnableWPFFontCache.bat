@echo off
echo Enable Windows Presentation Foundation Font Cache 3.0.0.0
Sc.exe Config FontCache3.0.0.0 Start= Auto
Sc.exe Start FontCache3.0.0.0