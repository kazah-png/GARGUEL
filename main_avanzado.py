#!/usr/bin/env python3
"""
GARGUEL v1.1 - Bot Profesional con IA
Punto de entrada principal

Copyright (c) 2026 kazah-png
GitHub: https://github.com/kazah-png/GARGUEL
"""

import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('garguel.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Banner
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

🚀 Funcionalidades v1.1:
   ✓ Sistema de IA con aprendizaje profundo
   ✓ Visualización gráfica del aprendizaje
   ✓ Interfaz profesional mejorada
   ✓ Optimización automática del sistema
   ✓ Gestión avanzada de ventanas
   ✓ Análisis predictivo con ML
   ✓ 25+ funcionalidades avanzadas

📊 Iniciando...
""")

try:
    # Importar módulos principales
    logger.info("Importando módulos...")
    
    from garguel import GarguelUltimateEnhanced
    from ai_learning_system import AdaptiveLearningSystem
    from professional_gui import ProfessionalGarguelGUI
    
    logger.info("✓ Módulos importados correctamente")
    
    # Crear bot con IA
    logger.info("Inicializando bot con sistema de IA...")
    bot = GarguelUltimateEnhanced()
    
    # Integrar sistema de IA
    bot.ai_system = AdaptiveLearningSystem(bot.db_path)
    logger.info(f"✓ IA inicializada: {bot.ai_system.learning_metrics['total_samples']} muestras entrenadas")
    
    # Crear GUI profesional
    logger.info("Creando interfaz gráfica profesional...")
    app = ProfessionalGarguelGUI(bot)
    
    # Intentar configurar icono de ventana
    try:
        from PIL import Image
        logo_path = Path("logo.png")
        if logo_path.exists():
            app.root.iconbitmap(default='logo.png')
            logger.info("✓ Logo configurado como icono de ventana")
    except:
        pass
    
    logger.info("✓ GARGUEL listo para usar\n")
    
    # Ejecutar
    app.run()
    
except KeyboardInterrupt:
    logger.info("\n⚠️  Cerrado por usuario")
    sys.exit(0)
    
except Exception as e:
    logger.error(f"\n❌ Error fatal: {e}")
    import traceback
    traceback.print_exc()
    input("\nPresiona Enter para salir...")
    sys.exit(1)
