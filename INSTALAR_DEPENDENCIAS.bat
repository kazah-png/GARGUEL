@echo off
title GARGUEL v1.1 - Instalador de Dependencias

echo.
echo ════════════════════════════════════════════════════════════
echo   GARGUEL v1.1 - Instalador de Dependencias
echo   Copyright (c) 2026 kazah-png
echo ════════════════════════════════════════════════════════════
echo.

echo [INFO] Verificando Python...
py --version
if errorlevel 1 (
    echo.
    echo [ERROR] Python no esta instalado o no esta en PATH
    echo.
    echo Por favor, instala Python desde: https://www.python.org/downloads/
    echo Asegurate de marcar "Add Python to PATH" durante la instalacion
    echo.
    pause
    exit /b 1
)

echo.
echo [INFO] Instalando dependencias minimas (version simple)...
echo        (Esto puede tardar 1-3 minutos)
echo.

py -m pip install --upgrade pip --quiet
py -m pip install -r requirements_minimal.txt

if errorlevel 1 (
    echo.
    echo [ADVERTENCIA] Algunos paquetes pueden haber fallado
    echo.
    echo Instalando paquetes criticos manualmente...
    py -m pip install customtkinter pillow opencv-python numpy pyautogui pandas openpyxl
)

echo.
echo [INFO] Instalacion minima completada
echo.
echo ¿Deseas instalar las funcionalidades avanzadas? (IA, graficos, etc)
echo Esto es OPCIONAL. El bot funciona sin ellas.
echo.
choice /C SN /M "Instalar funcionalidades avanzadas"

if errorlevel 2 (
    echo.
    echo [INFO] Saltando instalacion avanzada
    goto :done
)

echo.
echo [INFO] Instalando dependencias avanzadas...
echo        (Esto puede tardar 2-5 minutos adicionales)
echo.

py -m pip install psutil matplotlib requests schedule
if not errorlevel 1 (
    echo [OK] Funcionalidades avanzadas instaladas
)

:done

echo.
echo ════════════════════════════════════════════════════════════
echo   INSTALACION COMPLETADA
echo ════════════════════════════════════════════════════════════
echo.
echo   Ahora puedes ejecutar GARGUEL con:
echo   - Doble click en: INICIAR_GARGUEL.bat
echo   - O ejecuta: py launcher.py
echo.
echo ════════════════════════════════════════════════════════════
echo.
pause
