@echo off
title GARGUEL v1.3 - Instalador

cls
echo ==========================================
echo    GARGUEL v1.3 - INSTALADOR
echo ==========================================
echo.

py --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no instalado
    pause
    exit /b 1
)

py --version
echo.
echo Instalando paquetes...

py -m pip install customtkinter pyautogui

echo.
echo ==========================================
echo    COMPLETADO
echo ==========================================
pause
