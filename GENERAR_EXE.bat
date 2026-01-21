@echo off
title GARGUEL v1.1 - Generador de EXE

echo.
echo ════════════════════════════════════════════════════════════
echo   GARGUEL v1.1 - Generador de Ejecutable
echo   Copyright (c) 2026 kazah-png
echo   GitHub: https://github.com/kazah-png/GARGUEL
echo ════════════════════════════════════════════════════════════
echo.
echo [INFO] Instalando PyInstaller...
py -m pip install pyinstaller --quiet

echo.
echo [INFO] Generando GARGUEL_v1.1_Simple.exe ...
echo        (Esto puede tardar 3-5 minutos)
echo.

py -m PyInstaller --noconfirm --onefile --windowed ^
    --name GARGUEL_v1.1_Simple ^
    --icon logo.png ^
    --add-data "templates;templates" ^
    --add-data "config.json;." ^
    --add-data "logo.png;." ^
    garguel_simple.py

echo.
echo [INFO] Copiando archivos necesarios...

if exist dist\templates rmdir /s /q dist\templates
xcopy /E /I /Y templates dist\templates >nul
copy /Y config.json dist\ >nul
copy /Y logo.png dist\ >nul
copy /Y README.md dist\ >nul
copy /Y LEEME.txt dist\ >nul
copy /Y INICIO_RAPIDO.txt dist\ >nul

echo.
echo ════════════════════════════════════════════════════════════
echo   COMPLETADO
echo ════════════════════════════════════════════════════════════
echo.
echo   Ejecutable: dist\GARGUEL_v1.1_Simple.exe
echo.
echo   Distribuye la carpeta "dist" completa.
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
