# 🚀 INSTRUCCIONES RÁPIDAS - GARGUEL v1.0

**Copyright (c) 2026 kazah-png**

---

## ⚡ Inicio en 3 Pasos

### 1️⃣ Instalar
```bash
pip install -r requirements.txt
```

### 2️⃣ Ejecutar
```bash
python garguel.py
```

### 3️⃣ Usar
- Juego en **MODO VENTANA**
- Seleccionar dificultad
- Click "▶ INICIAR"

---

## 🎮 Cómo Funciona

GARGUEL usa **DETECCIÓN DINÁMICA** de tiempos:

- ❌ **NO** hay ciclos fijos
- ✅ Detecta cuánto dura cada partido en tiempo real
- ✅ Mide primer tiempo y segundo tiempo dinámicamente
- ✅ Registra todo para análisis

---

## 📊 Análisis de Tiempos

Después de cada partido verás:

```
⏱️  TIEMPOS DEL PARTIDO:
   • Primer tiempo:  1m 32s
   • Segundo tiempo: 1m 28s
   • TOTAL:          3m 48s

📊 ESTADÍSTICAS:
   • Promedio:  3m 52s
   • Récord:    3m 45s
   • Margen:    -3s vs récord
```

---

## 🔧 Generar EXE

### Windows:
```
Doble click en: build_exe.bat
```

### Linux/Mac:
```bash
chmod +x build_exe.sh
./build_exe.sh
```

El ejecutable estará en `dist/`

---

## ⚙️ Configuración Básica

**Archivo:** `config.json`

```json
{
    "game_window_region": [0, 0, 1280, 720],
    "template_threshold": 0.60
}
```

### Si no detecta botones:
```json
"template_threshold": 0.50
```

---

## 🎯 Modo Comandante

- Se activa **automáticamente** en el paso 10
- Solo se activa **UNA vez**
- Permanece activo el resto del farmeo
- **No requiere intervención**

---

## 🐛 Problemas Comunes

| Problema | Solución |
|----------|----------|
| No encuentra botones | Reduce threshold a 0.50 |
| Clicks incorrectos | Juego en modo ventana |
| Muy lento | Normal, es detección dinámica |

---

## 📁 Archivos Importantes

```
garguel.py       → Aplicación principal
config.json      → Configuración
garguel.db       → Base de datos
templates/       → Imágenes de botones
screenshots/     → Capturas de errores
```

---

## 💡 Consejos

✅ **Juego en ventana** (obligatorio)  
✅ **No mover el juego** tras iniciar  
✅ **Revisar consola** para ver progreso  
✅ **Screenshots** para debug  

---

## 📊 Base de Datos

Todos los tiempos se guardan en `garguel.db`

**Ver datos:**
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('garguel.db')
df = pd.read_sql_query("SELECT * FROM matches", conn)
print(df)
```

---

## ⚠️ IMPORTANTE

### ✅ Detección Dinámica

GARGUEL **NO** usa tiempos fijos. Cada partido puede durar diferente porque:

- Los partidos varían en duración
- El juego puede tener lag
- Los eventos son impredecibles

GARGUEL **espera dinámicamente** a que aparezcan los botones para medir el tiempo exacto.

---

## 🆘 Ayuda

**Consulta el README.md completo para:**
- Instrucciones detalladas
- Solución de problemas
- Configuración avanzada
- FAQ

---

**GARGUEL v1.0**  
**Copyright (c) 2026 kazah-png**

⚽ ¡Farmeo automático con análisis de tiempos!
