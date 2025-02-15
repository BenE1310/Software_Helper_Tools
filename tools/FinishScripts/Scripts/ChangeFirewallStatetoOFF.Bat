@echo off
echo Change Firewall State to OFF
Netsh Firewall Set OPMODE MODE = Disable
Netsh Firewall Set OPMODE MODE = Disable Profile = ALL