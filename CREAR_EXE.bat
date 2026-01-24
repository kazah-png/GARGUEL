@echo off
title GARGUEL v1.3 - Generador EXE

cls
echo ==========================================
echo    GENERAR GARGUEL.EXE
echo ==========================================
echo.
echo Genera ejecutable con icono personalizado
echo Tiempo estimado: 3-5 minutos
echo.
pause

echo.
echo [1/3] Instalando PyInstaller...
py -m pip install pyinstaller pillow

echo.
echo [2/3] Compilando con icono...
echo.

py -m PyInstaller ^
    --noconfirm ^
    --clean ^
    --onefile ^
    --windowed ^
    --name GARGUEL ^
    --icon icon.png ^
    --add-data "icon.png;." ^
    --hidden-import customtkinter ^
    --hidden-import pyautogui ^
    --hidden-import sqlite3 ^
    --hidden-import PIL ^
    --hidden-import PIL.Image ^
    --collect-all customtkinter ^
    GARGUEL_v1.3.py

if errorlevel 1 (
    echo.
    echo ERROR: Compilacion fallida
    pause
    exit /b 1
)

echo.
echo [3/3] Copiando icono al dist...
copy /Y icon.png dist\icon.png >nul

echo.
echo Limpiando archivos temporales...
rmdir /s /q build 2>nul
del /q GARGUEL.spec 2>nul

echo.
echo ==========================================
echo    EJECUTABLE CREADO
echo ==========================================
echo.
echo Ubicacion: dist\GARGUEL.exe
echo Icono: Incluido
echo Tamano: ~25MB
echo.
echo CARACTERISTICAS:
echo - Icono personalizado
echo - Ventana maximizada
echo - Sin subtitulo
echo - Standalone completo
echo.
echo DISTRIBUIR:
echo Copia dist\GARGUEL.exe e dist\icon.png
echo.
pause
