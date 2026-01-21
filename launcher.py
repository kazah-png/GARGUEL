#!/usr/bin/env python3
"""
GARGUEL v1.1 - Launcher Simple
Copyright (c) 2026 kazah-png

Launcher que verifica dependencias antes de iniciar
"""

import sys
import subprocess
from pathlib import Path

print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           ⚽ GARGUEL v1.1 PROFESSIONAL ⚽                      ║
║    Bot Avanzado con IA y Aprendizaje Automático             ║
║                                                              ║
║              Copyright (c) 2026 kazah-png                    ║
║        GitHub: https://github.com/kazah-png/GARGUEL         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")

print("🔍 Verificando dependencias...")

# Lista de dependencias requeridas
required_packages = [
    'customtkinter',
    'pillow',
    'opencv-python',
    'numpy',
    'pyautogui',
    'pandas',
    'openpyxl',
    'psutil',
    'matplotlib'
]

missing_packages = []

for package in required_packages:
    try:
        if package == 'opencv-python':
            __import__('cv2')
        elif package == 'pillow':
            __import__('PIL')
        else:
            __import__(package.replace('-', '_'))
        print(f"   ✓ {package}")
    except ImportError:
        print(f"   ✗ {package} - FALTA")
        missing_packages.append(package)

if missing_packages:
    print(f"\n❌ Faltan {len(missing_packages)} dependencias\n")
    print("Instalando automáticamente...\n")
    
    for package in missing_packages:
        print(f"📦 Instalando {package}...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package, '--quiet'])
            print(f"   ✓ {package} instalado")
        except:
            print(f"   ✗ Error instalando {package}")
    
    print("\n✅ Instalación completada. Reiniciando...\n")

print("\n🚀 Iniciando GARGUEL v1.1 Simple...\n")

try:
    print("📦 Cargando GARGUEL Simple (sin dependencias avanzadas)...")
    print("    ✓ Requiere: customtkinter, pillow, opencv-python, numpy, pyautogui, pandas, openpyxl")
    print()
    
    # Importar y ejecutar versión simple directamente
    exec(open('garguel_simple.py', encoding='utf-8').read())
    
except FileNotFoundError:
    print("❌ Error: No se encuentra garguel_simple.py")
    print("\nAsegúrate de que el archivo existe en la carpeta actual")
    input("\nPresiona Enter para salir...")
    sys.exit(1)
    
except ImportError as e:
    print(f"❌ Error: Falta una dependencia: {e}")
    print("\n🔧 SOLUCIÓN:")
    print("   Ejecuta: INSTALAR_DEPENDENCIAS.bat")
    print("   O manualmente:")
    print("   py -m pip install customtkinter pillow opencv-python numpy pyautogui pandas openpyxl")
    print()
    input("Presiona Enter para salir...")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error inesperado: {e}")
    import traceback
    traceback.print_exc()
    input("\nPresiona Enter para salir...")
    sys.exit(1)
