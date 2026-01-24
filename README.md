# GARGUEL v1.3

Bot Profesional de Farmeo - Todo en Uno

## 🎯 Características

### ✨ Un Solo Archivo
- `GARGUEL_v1.3.py` - Todo incluido
- Bot + GUI + BD en un archivo
- Fácil de mantener y modificar

### 🖥️ Ventana Completa
- Inicia en modo fullscreen windowed
- Maximizado automáticamente
- Interfaz escalable

### 📍 Posiciones Optimizadas
Basadas en macro real con 90% éxito:
- Inicio partido: Centro-abajo
- Selección dificultad: Centro
- Botones: Esquinas estratégicas
- Auto mode: Superior derecha

### ⏱️ Tiempos Calibrados
- Click wait: 0.5s
- Screen load: 1.5s
- Match tiempo: 40s (20s + 20s)
- Result screen: 2s

### 📦 Genera .EXE
- Ejecutable standalone
- ~25MB
- Sin Python requerido
- Distribuible

## 🚀 Uso

### Opción 1: Python

```bash
# Instalar
INSTALAR.bat

# Ejecutar
INICIAR.bat
```

### Opción 2: Ejecutable

```bash
# Generar .exe
CREAR_EXE.bat

# El .exe estará en dist/GARGUEL.exe
```

## 📋 Requisitos

Solo 2 paquetes:
```
customtkinter>=5.2.0
pyautogui>=0.9.54
```

## 🎮 Posiciones

```python
POSITIONS = {
    'inicio_partido': (960, 600),
    'seleccionar_dificultad': (960, 540),
    'boton_facil': (700, 540),
    'boton_normal': (960, 540),
    'boton_dificil': (1220, 540),
    'confirmar': (960, 650),
    'skip_intro': (1800, 1000),
    'auto_button': (1850, 50),
    'continuar_1': (960, 750),
    'continuar_2': (960, 800),
    'volver_menu': (960, 900),
}
```

Basadas en resolución 1920x1080.

## ⏱️ Secuencia

1. **Inicio** (1.5s)
   - Click inicio partido
   
2. **Selección** (2s)
   - Elegir dificultad
   - Confirmar

3. **Skip Intro** (1.5s)
   - 5 clicks rápidos
   
4. **Auto Mode** (0.5s)
   - Activar automático

5. **Partido** (40s)
   - Primer tiempo: 20s
   - Segundo tiempo: 20s

6. **Resultado** (5s)
   - Pantallas post-partido
   - Volver al menú

**Total:** ~50 segundos por partido

## 🖼️ Interfaz

- **Header:** Logo + Título
- **Stats:** Total, Victorias, Win Rate, Tiempo Avg
- **Controles:** Dificultad + Botones
- **Log:** Registro de actividad
- **Status:** Estado actual

## 📊 Base de Datos

SQLite integrada:
- Timestamp
- Dificultad
- Resultado
- Duración

Archivo: `garguel_data.db`

## 🎊 Ventajas v1.3

| Característica | Valor |
|----------------|-------|
| Archivos | 1 solo |
| Dependencias | 2 |
| Tamaño código | ~400 líneas |
| .exe tamaño | ~25MB |
| Ventana | Fullscreen |
| Posiciones | Optimizadas |
| Tiempos | Calibrados |
| Éxito | 90% |

## 📖 Autor

kazah-png © 2026
