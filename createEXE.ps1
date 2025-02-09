pyinstaller --onefile --console --icon=icon.ico --version-file version.txt `
  --add-data "Scripts;Scripts" `
  --add-data "functions.py;." `
  --add-data "logo1.png;." `
  --add-data "icon.ico;." `
  --hidden-import=wmi `
  --hidden-import=win32file `
  --hidden-import=win32api `
  --hidden-import=win32con `
  main.py
