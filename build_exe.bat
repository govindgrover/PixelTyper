@echo off
echo Building PixelTyper executable...
echo.

REM Clean previous builds
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist PixelTyper.spec del PixelTyper.spec

REM Run PyInstaller with options
pyinstaller --name=PixelTyper ^
    --onefile ^
    --windowed ^
    --icon=icon.ico ^
    --add-data "config.json;." ^
    --add-data "fonts;fonts" ^
    --add-data "icon.ico;." ^
    --collect-all ctk_colorpicker_plus ^
    --hidden-import=PIL ^
    --hidden-import=PIL._tkinter_finder ^
    --hidden-import=cv2 ^
    --hidden-import=customtkinter ^
    --hidden-import=ctk_colorpicker_plus ^
    UI.py

echo.
echo Build complete! Executable is in the dist folder.
pause
