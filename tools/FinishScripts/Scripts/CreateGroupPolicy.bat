@echo off
setlocal enabledelayedexpansion
PowerShell.Exe import-module GroupPolicy; New-GPO -Name \"Domain Controller Policy\"
PowerShell.Exe import-module GroupPolicy; New-GPO -Name \"Operational Disabled Share Policy\"
PowerShell.Exe import-module GroupPolicy; New-GPO -Name \"Operational Servers Policy\"
PowerShell.Exe import-module GroupPolicy; New-GPO -Name \"Security Servers Policy\"
PowerShell.Exe import-module GroupPolicy; New-GPO -Name \"Clients Computers Policy\"
PowerShell.Exe import-module GroupPolicy; New-GPO -Name \"Technical Users Policy\"
PowerShell.Exe import-module GroupPolicy; New-GPO -Name \"Operational Users Policy\"