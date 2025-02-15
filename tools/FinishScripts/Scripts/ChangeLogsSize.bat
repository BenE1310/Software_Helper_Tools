@echo off
echo Change Logs Size & Clear Logs
WEVTUtil.exe SL Application /MS:536870912
WEVTUtil.exe SL System /MS:536870912
WEVTUtil.exe SL Security /MS:536870912
WEVTUtil.exe CL Application
WEVTUtil.exe CL System
WEVTUtil.exe CL Security