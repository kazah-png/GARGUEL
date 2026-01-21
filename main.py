#!/usr/bin/env python3
"""
GARGUEL v1.1 - Punto de entrada principal
Redirecciona a la versión simplificada para evitar errores

Copyright (c) 2026 kazah-png
"""

print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           ⚽ GARGUEL v1.1 ⚽                                   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

Iniciando versión simplificada (recomendada)...
""")

try:
    # Ejecutar versión simple directamente
    with open('garguel_simple.py', 'r', encoding='utf-8') as f:
        exec(f.read())
        
except FileNotFoundError:
    print("❌ Error: No se encuentra garguel_simple.py")
    print("\nAsegúrate de que el archivo existe en la carpeta actual")
    input("\nPresiona Enter para salir...")
    
except ImportError as e:
    print(f"\n❌ Error: Falta una dependencia: {e}")
    print("\n🔧 SOLUCIÓN:")
    print("   Ejecuta en CMD/PowerShell:")
    print("   py -m pip install customtkinter pillow opencv-python numpy pyautogui pandas openpyxl")
    print()
    input("Presiona Enter para salir...")
    
except Exception as e:
    print(f"\n❌ Error inesperado: {e}")
    import traceback
    traceback.print_exc()
    input("\nPresiona Enter para salir...")
