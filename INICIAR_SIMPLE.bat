@echo off
title GARGUEL v1.1 Simple

echo.
echo ════════════════════════════════════════════════════════════
echo           ⚽ GARGUEL v1.1 SIMPLE ⚽
echo         Version sin dependencias avanzadas
echo ════════════════════════════════════════════════════════════
echo.

echo [INFO] Iniciando version simplificada...
echo.

py garguel_simple.py

if errorlevel 1 (
    echo.
    echo [ERROR] No se pudo iniciar
    echo.
    echo Instala las dependencias minimas:
    echo    py -m pip install customtkinter pillow opencv-python numpy pyautogui pandas openpyxl
    echo.
    pause
)
