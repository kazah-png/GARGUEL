# ⚽ GARGUEL v1.0

**Bot de Farmeo Automático con Detección Dinámica de Tiempos**  
**Inazuma Eleven Victory Road**

```
Copyright (c) 2026 kazah-png
Todos los derechos reservados.
```

---

## 📖 Índice

1. [¿Qué es GARGUEL?](#qué-es-garguel)
2. [Características Principales](#características-principales)
3. [Instalación](#instalación)
4. [Generar Ejecutable .EXE](#generar-ejecutable-exe)
5. [Uso](#uso)
6. [Configuración](#configuración)
7. [Análisis de Tiempos](#análisis-de-tiempos)
8. [Solución de Problemas](#solución-de-problemas)
9. [Base de Datos](#base-de-datos)
10. [Copyright y Licencia](#copyright-y-licencia)

---

## ¿Qué es GARGUEL?

GARGUEL es un bot automatizado que juega partidos en Inazuma Eleven Victory Road de forma autónoma. A diferencia de otros bots, **GARGUEL NO usa tiempos fijos**. Detecta dinámicamente cuánto dura cada partido para proporcionar análisis detallados y margen de mejora.

### ✨ Detección Dinámica

- **NO hay ciclos fijos**: Cada partido puede durar diferente
- **Medición en tiempo real**: Registra duración exacta de cada fase
- **Análisis automático**: Compara con promedios y récords
- **Margen de mejora**: Te muestra cuánto puedes optimizar

---

## Características Principales

### ⚡ Funcionalidades

- ✅ **Farmeo 100% Automático** - 17 pasos por partido
- ✅ **Detección Dinámica** - Mide tiempos reales sin ciclos fijos
- ✅ **Modo Comandante** - Se activa una vez y permanece
- ✅ **Análisis Detallado** - Tiempos de cada fase del partido
- ✅ **Estadísticas Completas** - Récord, promedio, margen de mejora
- ✅ **Base de Datos SQLite** - Historial completo
- ✅ **Interfaz Gráfica** - GUI moderna con CustomTkinter
- ✅ **Ejecutable .EXE** - Genera tu propio ejecutable

### 📊 Métricas Registradas

Para cada partido, GARGUEL registra:

- **Tiempo total** del partido completo
- **Pre-partido** (setup y configuración)
- **Primer tiempo** (detección dinámica)
- **Medio tiempo** (transición)
- **Segundo tiempo** (detección dinámica)
- **Post-partido** (recompensas)

Luego compara con:
- Promedio histórico
- Récord más rápido
- Partido más lento
- Margen de mejora

---

## Instalación

### Requisitos

- **Python 3.8+** (recomendado 3.10 o superior)
- **Windows**, **Linux** o **macOS**
- **Inazuma Eleven Victory Road** instalado

### Paso 1: Extraer el ZIP

Descomprime `GARGUEL_v1.0.zip` en una carpeta.

### Paso 2: Instalar Dependencias

Abre una terminal/CMD en la carpeta de GARGUEL:

```bash
pip install -r requirements.txt
```

Esto instalará:
- customtkinter (interfaz)
- opencv-python (detección de imágenes)
- pyautogui (automatización)
- pandas (análisis de datos)
- pillow, numpy (procesamiento)
- pyinstaller (para generar .exe)

### Paso 3: ¡Listo!

Ya puedes ejecutar GARGUEL:

```bash
python garguel.py
```

---

## Generar Ejecutable .EXE

### Windows

1. Doble click en `build_exe.bat`
2. Espera a que termine (puede tardar 2-3 minutos)
3. El ejecutable estará en la carpeta `dist/`
4. Ejecuta `dist/GARGUEL_v1.0.exe`

### Linux / macOS

```bash
chmod +x build_exe.sh
./build_exe.sh
```

El ejecutable estará en `dist/GARGUEL_v1.0`

### Distribución

Para distribuir GARGUEL, copia la carpeta `dist/` completa que incluye:
- GARGUEL_v1.0.exe (o GARGUEL_v1.0)
- templates/ (carpeta con imágenes)
- config.json

---

## Uso

### Inicio Rápido

1. **Abre el juego en MODO VENTANA** (no pantalla completa)
2. **Ejecuta GARGUEL**:
   - Doble click en `GARGUEL_v1.0.exe`, O
   - Ejecuta `python garguel.py`
3. **Selecciona dificultad** (Fácil, Normal o Difícil)
4. **Click "▶ INICIAR"**
5. **¡GARGUEL hace todo automáticamente!**

### Secuencia Automática (17 pasos)

```
PRE-PARTIDO (pasos 1-11):
  1. Intro
  2. Selección de dificultad
  3. Selección de batalla
  4. Pulsa el botón
  5-9. Configuración del partido (5 pasos)
  10. MODO COMANDANTE (U) ← Se activa UNA vez
  11. Saque de centro

PRIMER TIEMPO (paso 12):
  12. Detección dinámica → Espera hasta detectar medio tiempo
      ⏱️  Mide cuánto dura en tiempo real

MEDIO TIEMPO (pasos 13-14):
  13-14. Pantallas de medio tiempo

SEGUNDO TIEMPO (paso 15):
  15. Detección dinámica → Espera hasta detectar experiencia
      ⏱️  Mide cuánto dura en tiempo real

POST-PARTIDO (pasos 16-17):
  16. Experiencia jugadores
  17. Recompensas

→ LOOP (vuelve al paso 1)
```

### Controles en la Interfaz

- **▶ INICIAR** - Comienza el farmeo
- **⏸ Pausar** - Pausa temporalmente (se puede reanudar)
- **⏹ Detener** - Para el bot completamente

### Pestañas

- **ℹ️ Info** - Información y ayuda
- **📜 Historial** - Últimos 30 partidos con tiempos

---

## Configuración

### Archivo config.json

```json
{
    "game_window_region": null,
    "template_threshold": 0.60
}
```

#### game_window_region

Define la región de la ventana del juego para mejor precisión.

```json
"game_window_region": [x, y, ancho, alto]
```

**Ejemplo** para ventana en 1280x720:
```json
"game_window_region": [0, 0, 1280, 720]
```

**⚠️ IMPORTANTE**: El juego DEBE estar en modo ventana.

#### template_threshold

Umbral de detección (0.0 - 1.0):
- **0.50** = Más permisivo (detecta más fácil)
- **0.60** = Balanceado (por defecto)
- **0.75** = Muy estricto (más preciso)

---

## Análisis de Tiempos

### Qué Mide GARGUEL

Después de cada partido, GARGUEL muestra:

```
═══════════════════════════════════════════════════════
✅ PARTIDO #5 COMPLETADO
═══════════════════════════════════════════════════════

⏱️  TIEMPOS DEL PARTIDO:
   • Pre-partido:    45s
   • Primer tiempo:  1m 32s
   • Medio tiempo:   8s
   • Segundo tiempo: 1m 28s
   • Post-partido:   15s
   ────────────────────────────────────
   • TOTAL:          3m 48s

📊 ESTADÍSTICAS GLOBALES:
   • Partidos:  5
   • Record:    5V - 0D (100.0%)
   • Promedio:  3m 52s
   • Récord:    3m 45s
   • Más lento: 4m 2s

💡 MARGEN DE MEJORA: -3s vs récord
```

### Interpretación

- **Tiempo total**: Duración completa del partido
- **Promedio**: Media de todos tus partidos
- **Récord**: Tu partido más rápido
- **Más lento**: Tu partido más largo
- **Margen de mejora**: Cuánto puedes mejorar vs tu récord

**Ejemplo**: Si tu récord es 3m 45s y este partido duró 3m 48s, el margen de mejora es -3s.

### Variación de Tiempos

**GARGUEL NO usa tiempos fijos porque:**

1. Los partidos pueden variar en duración
2. El juego puede tener lag o cargas
3. Los eventos del partido son impredecibles

**GARGUEL detecta dinámicamente** cuándo termina cada tiempo esperando ver los botones correspondientes en pantalla.

---

## Solución de Problemas

### No encuentra los templates

**Causa**: Threshold muy alto o ventana incorrecta

**Solución**:
```json
// En config.json
"template_threshold": 0.50
```

### Clicks incorrectos

**Causa**: Juego no está en modo ventana

**Solución**:
1. Pon el juego en **MODO VENTANA**
2. No lo muevas tras iniciar GARGUEL
3. Configura `game_window_region` en config.json

### El modo comandante no se activa

**Causa**: GARGUEL lo activa automáticamente en el paso 10

**Solución**:
- Es automático, no requiere intervención
- Se activa UNA vez y permanece activo
- Revisa la consola para ver confirmación

### Los tiempos son muy largos

**Causa**: El bot espera hasta detectar los botones

**Solución**:
- Es normal, GARGUEL detecta dinámicamente
- Si tarda mucho (>3 min por tiempo), puede ser:
  - Template no detectado (revisa threshold)
  - Juego lento o con lag
  - Pantalla del juego oculta

### Screenshots de debug

Cuando hay errores, GARGUEL guarda capturas en `screenshots/`:
- `error_dificultad_*.png`
- `error_batalla_*.png`
- `error_general_*.png`

Revisa estas imágenes para ver qué está detectando.

---

## Base de Datos

### Archivo garguel.db

GARGUEL guarda todo en una base de datos SQLite.

### Tabla: matches

Cada partido registrado con:
- timestamp
- difficulty
- result (Victoria/Derrota)
- total_time
- pre_time
- first_half
- halftime
- second_half
- post_time

### Consultar la Base de Datos

**Con Python:**
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('garguel.db')
df = pd.read_sql_query("SELECT * FROM matches", conn)
print(df)
```

**Con herramientas:**
- DB Browser for SQLite
- DBeaver
- Cualquier visor de SQLite

---

## Copyright y Licencia

```
GARGUEL v1.0
Copyright (c) 2026 kazah-png
Todos los derechos reservados.

Este software es propiedad de kazah-png.
```

### Uso Permitido

- ✅ Uso personal
- ✅ Modificación para uso propio
- ✅ Estudio y aprendizaje

### Uso NO Permitido

- ❌ Distribución comercial
- ❌ Venta del software
- ❌ Remoción del copyright

---

## 📁 Estructura de Archivos

```
GARGUEL_v1.0/
├── garguel.py              # Aplicación principal
├── requirements.txt        # Dependencias
├── config.json            # Configuración
├── build_exe.bat          # Generador EXE (Windows)
├── build_exe.sh           # Generador EXE (Linux/Mac)
├── README.md             # Este archivo
├── INSTRUCCIONES.md      # Guía de uso
│
├── templates/            # 15 templates incluidos
│   ├── boton_facil.png
│   ├── boton_normal.png
│   ├── boton_dificil.png
│   ├── batalla_heroica.png
│   ├── batalla_objetos.png
│   ├── pulsa_boton.png
│   ├── terminar_edicion_cyan.png
│   ├── siguiente_cyan.png
│   ├── siguiente_cyan2.png
│   ├── terminar_edicion_blue.png
│   ├── siguiente_cyan3.png
│   ├── saque_centro.png
│   ├── terminar_edicion_blue_mt.png
│   ├── terminar_edicion_cyan_mt.png
│   └── siguiente_final.png
│
├── garguel.db            # Base de datos (se crea al ejecutar)
└── screenshots/          # Capturas de debug (se crea al ejecutar)
```

---

## ❓ FAQ

**P: ¿Por qué los partidos duran diferente?**  
R: GARGUEL detecta dinámicamente. Los partidos pueden variar según el juego, lag, eventos, etc.

**P: ¿Puedo dejarlo funcionando toda la noche?**  
R: Sí, GARGUEL puede funcionar indefinidamente. Asegúrate de que el juego no tenga timeouts de inactividad.

**P: ¿Cómo genero el .exe?**  
R: Ejecuta `build_exe.bat` (Windows) o `build_exe.sh` (Linux/Mac). El .exe estará en `dist/`.

**P: ¿Necesito tener Python instalado para el .exe?**  
R: No, el .exe es standalone y no requiere Python.

**P: ¿Funciona en pantalla completa?**  
R: No, el juego DEBE estar en modo ventana.

**P: ¿Puedo cambiar los templates?**  
R: Sí, reemplaza las imágenes en `templates/` con tus propias capturas.

**P: ¿Dónde están mis estadísticas?**  
R: En `garguel.db`. Puedes abrirlo con cualquier visor de SQLite.

---

## 🆘 Soporte

Si encuentras problemas:

1. Revisa la sección [Solución de Problemas](#solución-de-problemas)
2. Verifica los screenshots en `screenshots/`
3. Revisa la consola para mensajes de error
4. Comprueba que el juego esté en modo ventana

---

## 🎯 TL;DR - Guía Ultra Rápida

```bash
# 1. Extraer ZIP

# 2. Instalar
pip install -r requirements.txt

# 3. Ejecutar
python garguel.py

# 4. Generar EXE (opcional)
build_exe.bat    # Windows
./build_exe.sh   # Linux/Mac

# 5. Usar
- Juego en modo ventana
- Seleccionar dificultad
- Click "▶ INICIAR"
- ¡Farmear!
```

---

**GARGUEL v1.0** - Bot de Farmeo con Detección Dinámica  
**Copyright (c) 2026 kazah-png**

⚽ ¡Disfruta del farmeo automático con análisis de tiempos en tiempo real!

---

## 📦 Base de Datos de Jugadores

### Google Sheets Oficial

GARGUEL puede importar jugadores desde la base de datos oficial:

**URL**: https://docs.google.com/spreadsheets/d/1HW-weeq79GRnoZNcfbj7bINVaDv55WVl/edit

**Créditos**: Creador de la base de datos de jugadores de Inazuma Eleven Victory Road

### Importar Jugadores

Ejecuta el script incluido:

```bash
python import_players.py
```

Esto descargará automáticamente la base de datos y la importará a `garguel.db`.

---

## 📜 Créditos Completos

### GARGUEL v1.0
- **Desarrollador**: kazah-png
- **Copyright**: (c) 2026 kazah-png
- **Versión**: 1.0
- **Tipo**: Bot de Farmeo con Detección Dinámica

### Base de Datos de Jugadores
- **Fuente**: Google Sheets - Base de datos comunitaria de IEVR
- **URL**: https://docs.google.com/spreadsheets/d/1HW-weeq79GRnoZNcfbj7bINVaDv55WVl
- **Créditos**: Creador original de la base de datos

### Tecnologías Utilizadas
- Python 3.8+
- CustomTkinter (GUI)
- OpenCV (Detección de imágenes)
- PyAutoGUI (Automatización)
- Pandas (Análisis de datos)
- SQLite (Base de datos)

---

**GARGUEL v1.0** - © 2026 kazah-png - Todos los derechos reservados
