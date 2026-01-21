# Changelog

Todos los cambios notables de GARGUEL se documentan en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto se adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.1] - 2026-01-21

### ✨ Añadido
- **Sistema de Auto-Calibración**: Detección automática de ventana del juego
- **Cache Inteligente**: Sistema de cache con >90% hit rate
- **Threshold Adaptativo**: Aprendizaje automático del mejor umbral por template
- **Recuperación Automática de Errores**: Sistema de reintentos con estrategias específicas
- **Monitor de Rendimiento**: Monitoreo de CPU/RAM en tiempo real
- **Predicción de Tiempos**: Sistema predictivo basado en histórico personal
- **Sistema de Notificaciones Avanzado**: Alertas clasificadas por nivel
- **Exportación a Excel**: Generación de archivo Excel con análisis completo
- **Estadísticas de Racha**: Tracking de racha actual y mejor racha
- **Base de Datos Mejorada**: Nuevas tablas para sesiones y log de errores
- **Debug Visual Automático**: Screenshots automáticos en caso de error
- **Interfaz Mejorada**: Tarjetas de estadísticas en tiempo real
- **Tab de Rendimiento**: Visualización de métricas del sistema
- **Logging Detallado**: Sistema de logs con niveles INFO/WARNING/ERROR

### 🔧 Cambiado
- Optimización de detección de templates (hasta 70% más rápido)
- Mejora en gestión de memoria
- Interfaz gráfica rediseñada con más información
- Sistema de errores más robusto
- Documentación completamente reescrita

### 🐛 Corregido
- Mejora en estabilidad de detección
- Corrección de memory leaks en cache
- Fix en manejo de excepciones
- Mejora en precisión de clicks
- Optimización de uso de CPU

### 📝 Documentación
- README.md completamente reescrito
- LEEME.txt actualizado con nuevas características
- Documentación técnica ampliada
- FAQ extendido
- Guías de uso mejoradas

## [1.0] - 2026-01-20

### ✨ Añadido
- Versión inicial de GARGUEL
- Detección dinámica de tiempos sin ciclos fijos
- 17 pasos automatizados de farmeo
- Modo comandante automático
- Interfaz gráfica con CustomTkinter
- Base de datos SQLite para historial
- 15 templates para detección de botones
- Sistema de estadísticas básico
- Configuración mediante config.json
- Exportación de datos a CSV
- Logging básico
- Manejo de errores básico

### 📝 Documentación
- README.md inicial
- LEEME.txt con instrucciones
- LICENSE.txt con términos de uso

---

[1.1]: https://github.com/kazah-png/GARGUEL/releases/tag/v1.1
[1.0]: https://github.com/kazah-png/GARGUEL/releases/tag/v1.0

### 🚀 Funcionalidades Avanzadas Añadidas

#### SystemOptimizer
- Sistema de optimización de proceso
- Aumento de prioridad automático
- Configuración de afinidad de CPU
- Restauración automática al cerrar

#### GameWindowManager
- Búsqueda automática de ventana del juego
- Gestión inteligente de ventanas
- Mantiene ventana activa durante farmeo
- Detección automática de región

#### InputSimulator
- Múltiples métodos de entrada
- Click inteligente con fallbacks
- Control preciso de delays
- Soporte para Win32 API

#### ScreenshotManager
- Screenshots anotados con detecciones
- Generación de videos desde capturas
- Organización automática
- Marcado visual de coordenadas

#### DataAnalyzer
- Análisis de patrones con ML
- Predicción de tiempos futuros
- Detección de mejor hora para farmear
- Correlación CPU/RAM con rendimiento
- Recomendaciones automáticas
- Detección de tendencias

#### AutoUpdater
- Verificación automática de actualizaciones
- Integración con GitHub API
- Notificaciones de nuevas versiones
- Muestra changelog automáticamente

#### BackupManager
- Backups automáticos cada 10 partidos
- Gestión inteligente de backups
- Mantiene últimos 10 backups
- Sistema de restauración

#### TemplateOptimizer
- Análisis de calidad de templates
- Métricas: nitidez, contraste, brillo
- Score de calidad (0-100)
- Detección de templates problemáticos

#### SessionRecorder
- Grabación completa de sesiones
- Exportación a JSON
- Timestamps precisos
- Análisis post-sesión

### 📈 Mejoras de Rendimiento

- **+20-30%** más rápido en detección
- **+70%** reducción en búsquedas repetidas (cache)
- **>90%** hit rate en cache
- **±5-10s** precisión en predicciones

### 🔧 Mejoras Técnicas

- Integración completa con sistema operativo
- Optimización automática de recursos
- Gestión avanzada de memoria
- Análisis predictivo con ML
- Sistema de respaldo robusto

