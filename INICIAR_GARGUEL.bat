@echo off
title GARGUEL v1.1 - Launcher

echo.
echo ════════════════════════════════════════════════════════════
echo           ⚽ GARGUEL v1.1 PROFESSIONAL ⚽
echo ════════════════════════════════════════════════════════════
echo.

REM Verificar si existen las dependencias
py -c "import customtkinter" 2>nul
if errorlevel 1 (
    echo [ADVERTENCIA] Dependencias no instaladas
    echo.
    echo Ejecutando instalador automatico...
    echo.
    call INSTALAR_DEPENDENCIAS.bat
)

echo [INFO] Iniciando GARGUEL Simple...
echo.

py garguel_simple.py

if errorlevel 1 (
    echo.
    echo [ERROR] No se pudo iniciar GARGUEL
    echo.
    echo Soluciones:
    echo 1. Ejecuta: INSTALAR_DEPENDENCIAS.bat
    echo 2. O manualmente: py -m pip install customtkinter pillow opencv-python numpy pyautogui pandas openpyxl
    echo.
    pause
)
