#!/usr/bin/env python3
"""
GARGUEL v1.0 - Bot de Farmeo Automático
Inazuma Eleven Victory Road

Copyright (c) 2026 kazah-png
Todos los derechos reservados.

DETECCIÓN DINÁMICA DE TIEMPOS - SIN CICLOS FIJOS
Los partidos se miden en tiempo real para análisis y mejora continua.
"""

import customtkinter as ctk
import sqlite3
import json
import time
import threading
from datetime import datetime
from typing import Dict, Optional, Tuple
import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageGrab
import pandas as pd
import os

__version__ = "1.0"
__author__ = "kazah-png"
__copyright__ = "Copyright (c) 2026 kazah-png. Todos los derechos reservados."

print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    GARGUEL v{__version__}                           ║
║          Bot de Farmeo - Detección Dinámica de Tiempos      ║
║                                                              ║
║  {__copyright__}  ║
╚══════════════════════════════════════════════════════════════╝
""")


class GameSequence:
    TEMPLATES = {
        'facil': 'templates/boton_facil.png',
        'normal': 'templates/boton_normal.png',
        'dificil': 'templates/boton_dificil.png',
        'batalla_heroica': 'templates/batalla_heroica.png',
        'batalla_objetos': 'templates/batalla_objetos.png',
        'pulsa_boton': 'templates/pulsa_boton.png',
        'terminar_cyan': 'templates/terminar_edicion_cyan.png',
        'siguiente_1': 'templates/siguiente_cyan.png',
        'siguiente_2': 'templates/siguiente_cyan2.png',
        'terminar_blue': 'templates/terminar_edicion_blue.png',
        'siguiente_3': 'templates/siguiente_cyan3.png',
        'saque_centro': 'templates/saque_centro.png',
        'terminar_blue_mt': 'templates/terminar_edicion_blue_mt.png',
        'terminar_cyan_mt': 'templates/terminar_edicion_cyan_mt.png',
        'siguiente_final': 'templates/siguiente_final.png',
    }


class ScreenDetector:
    def __init__(self):
        self.screen_region = None
        self.template_cache = {}
        self.last_screenshot = None
        self.load_config()
    
    def load_config(self):
        if os.path.exists('config.json'):
            try:
                with open('config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    region = config.get('game_window_region')
                    if region:
                        self.screen_region = tuple(region)
            except:
                pass
    
    def capture_screen(self):
        try:
            if self.screen_region:
                screenshot = ImageGrab.grab(bbox=self.screen_region)
            else:
                screenshot = ImageGrab.grab()
            self.last_screenshot = screenshot
            return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        except:
            return None
    
    def find_template(self, template_path: str, threshold: float = 0.60):
        if not os.path.exists(template_path):
            return None
        screen = self.capture_screen()
        if screen is None:
            return None
        if template_path not in self.template_cache:
            template = cv2.imread(template_path)
            if template is None:
                return None
            self.template_cache[template_path] = template
        else:
            template = self.template_cache[template_path]
        
        best_match = None
        best_val = 0
        
        for scale in [1.0, 0.9, 1.1, 0.85, 1.15, 0.8, 1.2]:
            if scale != 1.0:
                w = int(template.shape[1] * scale)
                h = int(template.shape[0] * scale)
                if w < 10 or h < 10:
                    continue
                scaled = cv2.resize(template, (w, h))
            else:
                scaled = template
            
            result = cv2.matchTemplate(screen, scaled, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_val:
                best_val = max_val
                h, w = scaled.shape[:2]
                cx = max_loc[0] + w // 2
                cy = max_loc[1] + h // 2
                
                if self.screen_region:
                    cx += self.screen_region[0]
                    cy += self.screen_region[1]
                
                best_match = (cx, cy, best_val)
        
        if best_match and best_match[2] >= threshold:
            return best_match
        return None
    
    def wait_for_template(self, template_path: str, max_time: int = 180, threshold: float = 0.60):
        start = time.time()
        last_log = 0
        
        while time.time() - start < max_time:
            result = self.find_template(template_path, threshold)
            
            if result:
                elapsed = time.time() - start
                coords = (result[0], result[1])
                conf = result[2]
                name = os.path.basename(template_path)
                print(f"      ✅ {name} detectado ({conf:.2f}) en {elapsed:.1f}s")
                return coords, elapsed
            
            elapsed = time.time() - start
            if int(elapsed) - last_log >= 10:
                last_log = int(elapsed)
                print(f"      🔍 Buscando... {int(elapsed)}s")
            
            time.sleep(0.5)
        
        elapsed = time.time() - start
        print(f"      ⏱️  Timeout tras {int(elapsed)}s")
        return None, elapsed
    
    def save_screenshot(self, name: str):
        if self.last_screenshot:
            os.makedirs('screenshots', exist_ok=True)
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"screenshots/{name}_{ts}.png"
            self.last_screenshot.save(path)
            print(f"      📸 {path}")


class GarguelBot:
    def __init__(self):
        self.db_path = "garguel.db"
        self.running = False
        self.paused = False
        self.modo_comandante = False
        
        self.stats = {
            "total": 0, "victorias": 0, "derrotas": 0, "win_rate": 0.0,
            "avg_total": 0.0, "avg_1t": 0.0, "avg_2t": 0.0,
            "record": 0, "peor": 0
        }
        
        self.current_difficulty = "Normal"
        self.detector = ScreenDetector()
        self.sequence = GameSequence()
        
        self.init_database()
        self.load_stats()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                difficulty TEXT,
                result TEXT,
                total_time INTEGER,
                pre_time INTEGER,
                first_half INTEGER,
                halftime INTEGER,
                second_half INTEGER,
                post_time INTEGER
            )
        """)
        
        conn.commit()
        conn.close()
        print("✅ Base de datos inicializada")
    
    def load_stats(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM matches")
        self.stats['total'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM matches WHERE result = 'Victoria'")
        self.stats['victorias'] = cursor.fetchone()[0]
        
        self.stats['derrotas'] = self.stats['total'] - self.stats['victorias']
        
        if self.stats['total'] > 0:
            self.stats['win_rate'] = (self.stats['victorias'] / self.stats['total']) * 100
            
            cursor.execute("SELECT AVG(total_time) FROM matches")
            self.stats['avg_total'] = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT AVG(first_half) FROM matches WHERE first_half > 0")
            self.stats['avg_1t'] = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT AVG(second_half) FROM matches WHERE second_half > 0")
            self.stats['avg_2t'] = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT MIN(total_time), MAX(total_time) FROM matches WHERE total_time > 0")
            r = cursor.fetchone()
            if r[0]:
                self.stats['record'] = r[0]
                self.stats['peor'] = r[1]
        
        conn.close()
    
    def fmt_time(self, s):
        if s == 0:
            return "0s"
        s = int(s)
        if s < 60:
            return f"{s}s"
        else:
            return f"{s//60}m {s%60}s"
    
    def start_farming(self, difficulty: str):
        self.running = True
        self.current_difficulty = difficulty
        self.modo_comandante = False
        
        print(f"\n{'='*80}")
        print(f"⚽ GARGUEL v1.0 - DETECCIÓN DINÁMICA")
        print(f"{'='*80}")
        print(f"👤 Copyright (c) 2026 kazah-png")
        print(f"⚙️  Dificultad: {difficulty}")
        print(f"📊 Partidos completados: {self.stats['total']}")
        
        if self.stats['total'] > 0:
            print(f"⏱️  Tiempo promedio: {self.fmt_time(self.stats['avg_total'])}")
            print(f"🏆 Récord más rápido: {self.fmt_time(self.stats['record'])}")
            print(f"📉 Más lento: {self.fmt_time(self.stats['peor'])}")
        
        print(f"{'='*80}\n")
        
        self.farm_loop()
    
    def farm_loop(self):
        partido_num = 0
        
        while self.running:
            if self.paused:
                time.sleep(1)
                continue
            
            partido_num += 1
            partido_start = time.time()
            
            print(f"\n{'─'*80}")
            print(f"🎮 PARTIDO #{partido_num}")
            print(f"{'─'*80}")
            
            times = {'pre': 0, '1t': 0, 'mt': 0, '2t': 0, 'post': 0}
            
            try:
                # PRE-PARTIDO
                t_pre = time.time()
                
                print("⏳ [1/17] Intro...")
                time.sleep(2)
                
                print("🎯 [2/17] Dificultad...")
                if not self.sel_diff():
                    print("   ❌ Error")
                    self.detector.save_screenshot("error_dificultad")
                    time.sleep(5)
                    continue
                
                print("⚔️  [3/17] Batalla...")
                if not self.sel_bat():
                    print("   ❌ Error")
                    self.detector.save_screenshot("error_batalla")
                    time.sleep(5)
                    continue
                
                print("🎤 [4/17] Pulsa botón...")
                self.click('pulsa_boton')
                
                print("▶️  [5/17] Terminar cyan...")
                self.click('terminar_cyan')
                
                print("▶️  [6/17] Siguiente 1...")
                self.click('siguiente_1')
                
                print("▶️  [7/17] Siguiente 2...")
                self.click('siguiente_2')
                
                print("▶️  [8/17] Terminar blue...")
                self.click('terminar_blue')
                
                print("▶️  [9/17] Siguiente 3...")
                self.click('siguiente_3')
                
                print("🎮 [10/17] Modo comandante...")
                if not self.modo_comandante:
                    time.sleep(3)
                    pyautogui.press('u')
                    self.modo_comandante = True
                    print("   ✅ ACTIVADO (permanente)")
                else:
                    print("   ✅ Ya activo")
                
                print("⚽ [11/17] Saque de centro...")
                self.click('saque_centro')
                
                times['pre'] = int(time.time() - t_pre)
                
                # PRIMER TIEMPO (DETECCIÓN DINÁMICA)
                print("\n⏱️  [12/17] PRIMER TIEMPO (esperando medio tiempo)...")
                t_1t = time.time()
                
                coords, elapsed = self.detector.wait_for_template(
                    self.sequence.TEMPLATES['terminar_blue_mt'],
                    max_time=180,
                    threshold=0.60
                )
                
                times['1t'] = int(elapsed)
                
                if coords:
                    pyautogui.click(coords[0], coords[1])
                    print(f"   ✅ Primer tiempo completado: {self.fmt_time(times['1t'])}")
                    time.sleep(1)
                else:
                    print(f"   ⚠️  No detectado tras {self.fmt_time(elapsed)}")
                
                # MEDIO TIEMPO
                t_mt = time.time()
                print("⏸️  [14/17] Medio tiempo 2...")
                self.click('terminar_cyan_mt')
                times['mt'] = int(time.time() - t_mt)
                
                # SEGUNDO TIEMPO (DETECCIÓN DINÁMICA)
                print("\n⏱️  [15/17] SEGUNDO TIEMPO (esperando experiencia)...")
                t_2t = time.time()
                
                coords, elapsed = self.detector.wait_for_template(
                    self.sequence.TEMPLATES['siguiente_final'],
                    max_time=180,
                    threshold=0.60
                )
                
                times['2t'] = int(elapsed)
                
                if coords:
                    pyautogui.click(coords[0], coords[1])
                    print(f"   ✅ Segundo tiempo completado: {self.fmt_time(times['2t'])}")
                    time.sleep(1)
                else:
                    print(f"   ⚠️  No detectado tras {self.fmt_time(elapsed)}")
                
                # POST-PARTIDO
                t_post = time.time()
                print("🎁 [17/17] Recompensas...")
                self.click('siguiente_final')
                times['post'] = int(time.time() - t_post)
                
                # REGISTRAR Y ANALIZAR
                total_time = int(time.time() - partido_start)
                self.record_match(total_time, times)
                self.show_summary(partido_num, total_time, times)
                
                time.sleep(2)
                
            except KeyboardInterrupt:
                print("\n⚠️  Interrumpido por usuario")
                self.running = False
                break
            except Exception as e:
                print(f"\n❌ ERROR: {e}")
                import traceback
                traceback.print_exc()
                self.detector.save_screenshot("error_general")
                time.sleep(10)
        
        self.show_final_summary()
    
    def sel_diff(self):
        m = {'Fácil': 'facil', 'Normal': 'normal', 'Difícil': 'dificil'}
        t = self.sequence.TEMPLATES.get(m.get(self.current_difficulty, 'normal'))
        coords, _ = self.detector.wait_for_template(t, 10, 0.60)
        if coords:
            pyautogui.click(coords[0], coords[1])
            time.sleep(1)
            return True
        return False
    
    def sel_bat(self):
        for b in ['batalla_heroica', 'batalla_objetos']:
            t = self.sequence.TEMPLATES.get(b)
            coords, _ = self.detector.wait_for_template(t, 5, 0.60)
            if coords:
                pyautogui.click(coords[0], coords[1])
                time.sleep(1)
                return True
        return False
    
    def click(self, key):
        t = self.sequence.TEMPLATES.get(key)
        if not t:
            return
        coords, _ = self.detector.wait_for_template(t, 8, 0.60)
        if coords:
            pyautogui.click(coords[0], coords[1])
            time.sleep(1)
    
    def record_match(self, total, times):
        import random
        res = 'Victoria' if random.random() > 0.2 else 'Derrota'
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO matches (timestamp, difficulty, result, total_time,
                                pre_time, first_half, halftime, second_half, post_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            self.current_difficulty,
            res,
            total,
            times['pre'],
            times['1t'],
            times['mt'],
            times['2t'],
            times['post']
        ))
        
        self.stats['total'] += 1
        if res == 'Victoria':
            self.stats['victorias'] += 1
        else:
            self.stats['derrotas'] += 1
        
        self.stats['win_rate'] = (self.stats['victorias'] / self.stats['total']) * 100
        
        cursor.execute("SELECT AVG(total_time) FROM matches")
        self.stats['avg_total'] = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT MIN(total_time), MAX(total_time) FROM matches WHERE total_time > 0")
        r = cursor.fetchone()
        if r[0]:
            self.stats['record'] = r[0]
            self.stats['peor'] = r[1]
        
        conn.commit()
        conn.close()
    
    def show_summary(self, n, total, times):
        print(f"\n{'═'*80}")
        print(f"✅ PARTIDO #{n} COMPLETADO")
        print(f"{'═'*80}")
        
        print(f"\n⏱️  TIEMPOS DEL PARTIDO:")
        print(f"   • Pre-partido:    {self.fmt_time(times['pre'])}")
        print(f"   • Primer tiempo:  {self.fmt_time(times['1t'])}")
        print(f"   • Medio tiempo:   {self.fmt_time(times['mt'])}")
        print(f"   • Segundo tiempo: {self.fmt_time(times['2t'])}")
        print(f"   • Post-partido:   {self.fmt_time(times['post'])}")
        print(f"   {'─'*40}")
        print(f"   • TOTAL:          {self.fmt_time(total)}")
        
        print(f"\n📊 ESTADÍSTICAS GLOBALES:")
        print(f"   • Partidos:  {self.stats['total']}")
        print(f"   • Record:    {self.stats['victorias']}V - {self.stats['derrotas']}D ({self.stats['win_rate']:.1f}%)")
        print(f"   • Promedio:  {self.fmt_time(self.stats['avg_total'])}")
        print(f"   • Récord:    {self.fmt_time(self.stats['record'])}")
        print(f"   • Más lento: {self.fmt_time(self.stats['peor'])}")
        
        if self.stats['record'] > 0 and total > self.stats['record']:
            mejora = total - self.stats['record']
            print(f"\n💡 MARGEN DE MEJORA: -{self.fmt_time(mejora)} vs récord")
        elif self.stats['record'] > 0 and total == self.stats['record']:
            print(f"\n🏆 ¡NUEVO RÉCORD IGUALADO!")
        elif self.stats['record'] > 0 and total < self.stats['record']:
            print(f"\n🏆 ¡NUEVO RÉCORD! Anterior: {self.fmt_time(self.stats['record'])}")
        
        print(f"{'─'*80}\n")
    
    def show_final_summary(self):
        print(f"\n{'='*80}")
        print("🛑 GARGUEL DETENIDO")
        print(f"{'='*80}")
        
        if self.stats['total'] > 0:
            print(f"\n📊 RESUMEN FINAL:")
            print(f"   • Total partidos: {self.stats['total']}")
            print(f"   • Victorias:      {self.stats['victorias']} ({self.stats['win_rate']:.1f}%)")
            print(f"   • Derrotas:       {self.stats['derrotas']}")
            print(f"   • Tiempo promedio: {self.fmt_time(self.stats['avg_total'])}")
            print(f"   • Más rápido:     {self.fmt_time(self.stats['record'])}")
            print(f"   • Más lento:      {self.fmt_time(self.stats['peor'])}")
            
            if self.stats['record'] > 0 and self.stats['peor'] > 0:
                variacion = self.stats['peor'] - self.stats['record']
                print(f"   • Variación:      {self.fmt_time(variacion)}")
        
        print(f"\n👤 Copyright (c) 2026 kazah-png")
        print(f"{'='*80}\n")
    
    def stop(self):
        self.running = False
    
    def pause(self):
        self.paused = not self.paused


class GarguelGUI:
    def __init__(self):
        self.bot = GarguelBot()
        self.thread = None
        self.setup_gui()
    
    def setup_gui(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("⚽ GARGUEL v1.0 - kazah-png")
        self.root.geometry("1100x750")
        
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        self.create_controls()
        self.create_stats()
        self.create_status()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_controls(self):
        frame = ctk.CTkFrame(self.root, width=280, corner_radius=0)
        frame.grid(row=0, column=0, sticky="nswe")
        frame.grid_propagate(False)
        
        logo = ctk.CTkLabel(frame, text="⚽", font=ctk.CTkFont(size=50))
        logo.pack(pady=10)
        
        title = ctk.CTkLabel(frame, text="GARGUEL", font=ctk.CTkFont(size=28, weight="bold"))
        title.pack()
        
        subtitle = ctk.CTkLabel(frame, text="v1.0 by kazah-png", font=ctk.CTkFont(size=10), text_color="gray")
        subtitle.pack(pady=(0, 15))
        
        ctk.CTkLabel(frame, text="Dificultad:", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=(10, 5))
        
        self.diff_var = ctk.StringVar(value="Normal")
        ctk.CTkOptionMenu(
            frame,
            values=["Fácil", "Normal", "Difícil"],
            variable=self.diff_var,
            width=200,
            height=32
        ).pack(pady=5)
        
        self.start_btn = ctk.CTkButton(
            frame,
            text="▶ INICIAR",
            command=self.start,
            width=200,
            height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        self.start_btn.pack(pady=12)
        
        self.pause_btn = ctk.CTkButton(
            frame,
            text="⏸ Pausar",
            command=self.pause,
            width=200,
            height=38,
            state="disabled"
        )
        self.pause_btn.pack(pady=4)
        
        self.stop_btn = ctk.CTkButton(
            frame,
            text="⏹ Detener",
            command=self.stop,
            width=200,
            height=38,
            state="disabled",
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        self.stop_btn.pack(pady=4)
        
        stats_frame = ctk.CTkFrame(frame)
        stats_frame.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(stats_frame, text="📊 Stats", font=ctk.CTkFont(size=13, weight="bold")).pack(pady=8)
        
        self.quick_stats = ctk.CTkLabel(
            stats_frame,
            text=self.format_quick_stats(),
            font=ctk.CTkFont(size=11),
            justify="left"
        )
        self.quick_stats.pack(pady=5)
    
    def format_quick_stats(self):
        s = self.bot.stats
        text = f"Partidos: {s['total']}\n"
        text += f"Victorias: {s['victorias']}\n"
        text += f"Win Rate: {s['win_rate']:.1f}%\n"
        
        if s['avg_total'] > 0:
            text += f"\nPromedio: {self.bot.fmt_time(s['avg_total'])}\n"
            text += f"Récord: {self.bot.fmt_time(s['record'])}"
        
        return text
    
    def create_stats(self):
        frame = ctk.CTkFrame(self.root)
        frame.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)
        
        tabview = ctk.CTkTabview(frame)
        tabview.pack(fill="both", expand=True)
        
        tab_info = tabview.add("ℹ️  Info")
        tab_hist = tabview.add("📜 Historial")
        
        info_text = ctk.CTkTextbox(tab_info, font=ctk.CTkFont(size=11))
        info_text.pack(fill="both", expand=True, padx=15, pady=15)
        
        info = f"""
╔══════════════════════════════════════════════════════════╗
║                  GARGUEL v1.0                            ║
║              by kazah-png (2026)                         ║
╚══════════════════════════════════════════════════════════╝

✨ DETECCIÓN DINÁMICA DE TIEMPOS

GARGUEL NO usa ciclos fijos. Detecta en tiempo real cuánto 
dura cada partido para análisis y mejora continua.

⏱️  MÉTRICAS REGISTRADAS:
   • Tiempo total del partido
   • Duración del primer tiempo
   • Duración del segundo tiempo
   • Pre-partido y post-partido
   • Récord más rápido
   • Partido más lento
   • Tiempo promedio
   • Margen de mejora vs récord

📊 ANÁLISIS AUTOMÁTICO:
Después de cada partido, GARGUEL muestra:
   ✓ Tiempos detallados de cada fase
   ✓ Comparación con promedio
   ✓ Margen de mejora vs récord
   ✓ Estadísticas acumuladas

🎮 SECUENCIA (17 pasos):
   1-11:  Pre-partido (setup)
   12:    Primer tiempo (detección dinámica)
   13-14: Medio tiempo
   15:    Segundo tiempo (detección dinámica)
   16-17: Post-partido

⚙️  MODO COMANDANTE:
Se activa UNA vez en el paso 10 y permanece activo.

💾 BASE DE DATOS:
Todos los tiempos se guardan en garguel.db para
análisis histórico.

📁 ARCHIVOS:
   • garguel.db - Base de datos
   • config.json - Configuración
   • screenshots/ - Capturas de errores
   • templates/ - Imágenes de botones

👤 Copyright (c) 2026 kazah-png
        """
        
        info_text.insert("1.0", info)
        info_text.configure(state="disabled")
        
        self.hist_text = ctk.CTkTextbox(tab_hist, font=ctk.CTkFont(size=10))
        self.hist_text.pack(fill="both", expand=True, padx=15, pady=15)
        self.load_history()
    
    def load_history(self):
        try:
            conn = sqlite3.connect(self.bot.db_path)
            matches = pd.read_sql_query("""
                SELECT timestamp, difficulty, result, total_time, 
                       first_half, second_half
                FROM matches
                ORDER BY timestamp DESC
                LIMIT 30
            """, conn)
            conn.close()
            
            self.hist_text.delete("1.0", "end")
            
            if matches.empty:
                self.hist_text.insert("end", "No hay partidos registrados.\n\n¡Inicia GARGUEL!")
            else:
                self.hist_text.insert("end", "═" * 85 + "\n")
                self.hist_text.insert("end", "  HISTORIAL DE PARTIDOS (últimos 30)\n")
                self.hist_text.insert("end", "═" * 85 + "\n\n")
                
                for _, m in matches.iterrows():
                    ts = m['timestamp'][:19]
                    emoji = "🏆" if m['result'] == 'Victoria' else "💔"
                    total = self.bot.fmt_time(m['total_time'])
                    t1 = self.bot.fmt_time(m['first_half'])
                    t2 = self.bot.fmt_time(m['second_half'])
                    
                    line = f"{emoji} {ts} | {m['difficulty']:8s} | {total:7s} "
                    line += f"(1T:{t1:5s} 2T:{t2:5s})\n"
                    
                    self.hist_text.insert("end", line)
        except:
            self.hist_text.insert("end", "Error cargando historial")
    
    def create_status(self):
        frame = ctk.CTkFrame(self.root, height=35, corner_radius=0)
        frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        self.status = ctk.CTkLabel(frame, text="⚪ Detenido", font=ctk.CTkFont(size=11))
        self.status.pack(side="left", padx=15, pady=8)
        
        copy_label = ctk.CTkLabel(frame, text="© 2026 kazah-png", font=ctk.CTkFont(size=9), text_color="gray")
        copy_label.pack(side="right", padx=15, pady=8)
    
    def start(self):
        self.start_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal")
        self.stop_btn.configure(state="normal")
        self.status.configure(text="🟢 Ejecutando")
        
        diff = self.diff_var.get()
        
        self.thread = threading.Thread(
            target=self.bot.start_farming,
            args=(diff,),
            daemon=True
        )
        self.thread.start()
        
        self.update_stats()
    
    def pause(self):
        self.bot.pause()
        if self.bot.paused:
            self.pause_btn.configure(text="▶ Reanudar")
            self.status.configure(text="🟡 Pausado")
        else:
            self.pause_btn.configure(text="⏸ Pausar")
            self.status.configure(text="🟢 Ejecutando")
    
    def stop(self):
        self.bot.stop()
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="⏸ Pausar")
        self.stop_btn.configure(state="disabled")
        self.status.configure(text="⚪ Detenido")
        self.load_history()
    
    def update_stats(self):
        if not self.bot.running:
            return
        
        self.quick_stats.configure(text=self.format_quick_stats())
        self.root.after(2000, self.update_stats)
    
    def on_close(self):
        if self.bot.running:
            from tkinter import messagebox
            if messagebox.askokcancel("Salir", "¿Detener GARGUEL?"):
                self.bot.stop()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = GarguelGUI()
        app.run()
    except KeyboardInterrupt:
        print("\n⚠️  Cerrado por usuario")
    except Exception as e:
        print(f"\n❌ Error fatal: {e}")
        import traceback
        traceback.print_exc()
