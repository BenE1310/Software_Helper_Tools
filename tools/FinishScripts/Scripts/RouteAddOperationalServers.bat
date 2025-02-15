@echo off
echo Don't start manually, Only through main menu!!
echo Add Route Operational Servers
Route add 10.12.0.0 mask 255.255.0.0 10.12.%Batt%8.254 /p
Route add 10.11.%Batt%3.0 mask 255.255.255.0 10.11.%Batt%8.254 /p