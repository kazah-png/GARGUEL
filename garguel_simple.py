#!/usr/bin/env python3
"""
GARGUEL v1.1 - Versión Simplificada (Sin dependencias avanzadas)
Copyright (c) 2026 kazah-png

Versión que funciona sin psutil ni matplotlib para compatibilidad máxima
"""

import customtkinter as ctk
from tkinter import messagebox
import cv2
import numpy as np
import pyautogui
from PIL import Image, ImageGrab
import sqlite3
import pandas as pd
import time
import json
import logging
from pathlib import Path
from datetime import datetime
import threading

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

# Configurar pyautogui
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3

__version__ = "1.1"


class GarguelBot:
    """Bot principal simplificado"""
    
    def __init__(self):
        self.db_path = 'garguel.db'
        self.config_path = 'config.json'
        self.templates_dir = Path('templates')
        
        self.running = False
        self.paused = False
        
        self.stats = {
            'total': 0,
            'victorias': 0,
            'derrotas': 0,
            'win_rate': 0.0,
            'avg_total': 0,
            'record': 999999,
            'peor': 0,
            'racha_actual': 0,
            'mejor_racha': 0,
            'avg_1t': 0,
            'avg_2t': 0
        }
        
        self.load_config()
        self.init_database()
        self.load_stats()
        
        logger.info("⚽ GARGUEL v1.1 Simplificado inicializado")
        
    def load_config(self):
        """Cargar configuración"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.region = config.get('game_window_region')
            self.threshold = config.get('template_threshold', 0.6)
            
            logger.info(f"Configuración cargada: threshold={self.threshold}")
            
        except Exception as e:
            logger.warning(f"No se pudo cargar config: {e}, usando defaults")
            self.region = None
            self.threshold = 0.6
    
    def init_database(self):
        """Inicializar base de datos"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    difficulty TEXT,
                    result TEXT,
                    total_time INTEGER,
                    first_half INTEGER,
                    second_half INTEGER
                )
            """)
            
            conn.commit()
            conn.close()
            
            logger.info("Base de datos inicializada")
            
        except Exception as e:
            logger.error(f"Error inicializando BD: {e}")
    
    def load_stats(self):
        """Cargar estadísticas desde BD"""
        try:
            conn = sqlite3.connect(self.db_path)
            matches_df = pd.read_sql_query("SELECT * FROM matches", conn)
            conn.close()
            
            if not matches_df.empty:
                self.stats['total'] = len(matches_df)
                self.stats['victorias'] = len(matches_df[matches_df['result'] == 'Victoria'])
                self.stats['derrotas'] = self.stats['total'] - self.stats['victorias']
                
                if self.stats['total'] > 0:
                    self.stats['win_rate'] = (self.stats['victorias'] / self.stats['total']) * 100
                
                times = matches_df['total_time'][matches_df['total_time'] > 0]
                if not times.empty:
                    self.stats['avg_total'] = int(times.mean())
                    self.stats['record'] = int(times.min())
                    self.stats['peor'] = int(times.max())
                
                logger.info(f"Stats cargadas: {self.stats['total']} partidos")
                
        except Exception as e:
            logger.error(f"Error cargando stats: {e}")
    
    def find_template(self, template_name, confidence=None):
        """Buscar template en pantalla"""
        try:
            template_path = self.templates_dir / template_name
            if not template_path.exists():
                logger.error(f"Template no encontrado: {template_name}")
                return None
            
            template = cv2.imread(str(template_path))
            if template is None:
                return None
            
            # Capturar pantalla
            if self.region:
                screenshot = ImageGrab.grab(bbox=self.region)
            else:
                screenshot = ImageGrab.grab()
            
            screenshot = np.array(screenshot)
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
            
            # Buscar
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            threshold = confidence if confidence else self.threshold
            
            if max_val >= threshold:
                h, w = template.shape[:2]
                x = max_loc[0] + w // 2
                y = max_loc[1] + h // 2
                
                if self.region:
                    x += self.region[0]
                    y += self.region[1]
                
                return (x, y, max_val)
            
            return None
            
        except Exception as e:
            logger.error(f"Error buscando template {template_name}: {e}")
            return None
    
    def click_template(self, template_name, wait=1.0, confidence=None):
        """Buscar y hacer click en template"""
        result = self.find_template(template_name, confidence)
        
        if result:
            x, y, conf = result
            logger.info(f"Click en {template_name} ({conf:.2f}) -> ({x}, {y})")
            pyautogui.click(x, y)
            time.sleep(wait)
            return True
        else:
            logger.warning(f"No se encontró {template_name}")
            return False
    
    def wait_for_template(self, template_name, timeout=120, check_interval=2):
        """Esperar hasta que aparezca un template"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not self.running:
                return False
            
            if self.paused:
                time.sleep(1)
                continue
            
            result = self.find_template(template_name)
            if result:
                logger.info(f"Template {template_name} encontrado")
                return True
            
            time.sleep(check_interval)
        
        logger.warning(f"Timeout esperando {template_name}")
        return False
    
    def save_match(self, difficulty, result, total_time, first_half, second_half):
        """Guardar partido en BD"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO matches (timestamp, difficulty, result, total_time, first_half, second_half)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                difficulty,
                result,
                total_time,
                first_half,
                second_half
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Partido guardado: {result} - {total_time}s")
            
        except Exception as e:
            logger.error(f"Error guardando partido: {e}")
    
    def fmt_time(self, seconds):
        """Formatear tiempo"""
        if seconds <= 0:
            return "0s"
        m = seconds // 60
        s = seconds % 60
        if m > 0:
            return f"{m}m {s}s"
        return f"{s}s"
    
    def start_farming(self, difficulty):
        """Iniciar farmeo"""
        self.running = True
        self.current_difficulty = difficulty
        
        logger.info(f"\n{'='*60}")
        logger.info(f"INICIANDO FARMEO - Dificultad: {difficulty}")
        logger.info(f"{'='*60}\n")
        
        partido_num = 0
        
        while self.running:
            if self.paused:
                time.sleep(1)
                continue
            
            try:
                partido_num += 1
                logger.info(f"\n🎮 PARTIDO #{partido_num}")
                
                # Secuencia simplificada de 17 pasos
                start_time = time.time()
                
                # 1-11: Pre-partido
                self.click_template('siguiente_cyan.png', wait=0.5)
                self.click_template(f'boton_{difficulty.lower()}.png', wait=0.5)
                self.click_template('batalla_heroica.png', wait=0.5)
                
                for _ in range(7):
                    self.click_template('siguiente_cyan.png', wait=0.3)
                
                # 12: Primer tiempo
                first_half_start = time.time()
                if not self.wait_for_template('terminar_edicion_cyan_mt.png', timeout=180):
                    logger.error("Timeout en primer tiempo")
                    continue
                first_half_time = int(time.time() - first_half_start)
                
                # 13-14: Medio tiempo
                self.click_template('terminar_edicion_cyan_mt.png', wait=0.5)
                self.click_template('siguiente_cyan.png', wait=0.5)
                
                # 15: Segundo tiempo
                second_half_start = time.time()
                if not self.wait_for_template('siguiente_final.png', timeout=180):
                    logger.error("Timeout en segundo tiempo")
                    continue
                second_half_time = int(time.time() - second_half_start)
                
                # 16-17: Post-partido
                self.click_template('siguiente_final.png', wait=0.5)
                self.click_template('siguiente_cyan.png', wait=0.5)
                
                total_time = int(time.time() - start_time)
                
                # Guardar
                self.save_match(difficulty, 'Victoria', total_time, first_half_time, second_half_time)
                self.load_stats()
                
                logger.info(f"✅ Partido completado en {self.fmt_time(total_time)}")
                
            except Exception as e:
                logger.error(f"Error en partido: {e}")
                continue
    
    def pause(self):
        """Pausar/reanudar"""
        self.paused = not self.paused
        logger.info(f"{'⏸ Pausado' if self.paused else '▶ Reanudado'}")
    
    def stop(self):
        """Detener"""
        self.running = False
        logger.info("⏹ Detenido")


class SimpleGUI:
    """Interfaz gráfica simplificada"""
    
    def __init__(self, bot):
        self.bot = bot
        self.setup_gui()
    
    def setup_gui(self):
        """Configurar interfaz"""
        self.root = ctk.CTk()
        self.root.title("⚽ GARGUEL v1.1 Simple - by kazah-png")
        self.root.geometry("900x700")
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Logo y título
        logo_label = ctk.CTkLabel(
            main_frame,
            text="⚽ GARGUEL v1.1",
            font=ctk.CTkFont(size=40, weight="bold")
        )
        logo_label.pack(pady=20)
        
        subtitle = ctk.CTkLabel(
            main_frame,
            text="Bot de Farmeo Simplificado",
            font=ctk.CTkFont(size=16)
        )
        subtitle.pack()
        
        # Stats
        stats_frame = ctk.CTkFrame(main_frame)
        stats_frame.pack(pady=20, padx=20, fill="x")
        
        s = self.bot.stats
        
        stats_text = f"""
        📊 ESTADÍSTICAS
        
        Total Partidos: {s['total']}
        Victorias: {s['victorias']}
        Win Rate: {s['win_rate']:.1f}%
        
        Tiempo Promedio: {self.bot.fmt_time(s['avg_total'])}
        Récord: {self.bot.fmt_time(s['record'])}
        """
        
        stats_label = ctk.CTkLabel(
            stats_frame,
            text=stats_text,
            font=ctk.CTkFont(size=14),
            justify="left"
        )
        stats_label.pack(pady=10)
        
        # Controles
        controls_frame = ctk.CTkFrame(main_frame)
        controls_frame.pack(pady=20, padx=20, fill="x")
        
        ctk.CTkLabel(
            controls_frame,
            text="Dificultad:",
            font=ctk.CTkFont(size=14)
        ).pack(pady=5)
        
        self.diff_var = ctk.StringVar(value="Normal")
        diff_menu = ctk.CTkOptionMenu(
            controls_frame,
            values=["Fácil", "Normal", "Difícil"],
            variable=self.diff_var,
            width=300,
            height=40,
            font=ctk.CTkFont(size=14)
        )
        diff_menu.pack(pady=10)
        
        # Botones
        buttons_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        buttons_frame.pack(pady=20)
        
        self.start_btn = ctk.CTkButton(
            buttons_frame,
            text="▶ INICIAR",
            command=self.start,
            width=200,
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        self.start_btn.pack(side="left", padx=5)
        
        self.pause_btn = ctk.CTkButton(
            buttons_frame,
            text="⏸ Pausar",
            command=self.pause,
            width=150,
            height=50,
            font=ctk.CTkFont(size=14),
            state="disabled"
        )
        self.pause_btn.pack(side="left", padx=5)
        
        self.stop_btn = ctk.CTkButton(
            buttons_frame,
            text="⏹ Detener",
            command=self.stop,
            width=150,
            height=50,
            font=ctk.CTkFont(size=14),
            state="disabled",
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        self.stop_btn.pack(side="left", padx=5)
        
        # Info
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.log_text = ctk.CTkTextbox(
            info_frame,
            font=ctk.CTkFont(size=11, family="Courier")
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.log_text.insert("end", "⚽ GARGUEL v1.1 Simple\n")
        self.log_text.insert("end", "Copyright (c) 2026 kazah-png\n\n")
        self.log_text.insert("end", "Versión simplificada sin dependencias avanzadas\n")
        self.log_text.insert("end", "Listo para usar.\n\n")
        
        # Status
        self.status_label = ctk.CTkLabel(
            self.root,
            text="⚪ Detenido",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.status_label.pack(pady=10)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def start(self):
        """Iniciar"""
        self.start_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text="🟢 Ejecutando")
        
        diff = self.diff_var.get()
        
        self.thread = threading.Thread(
            target=self.bot.start_farming,
            args=(diff,),
            daemon=True
        )
        self.thread.start()
        
        self.log_text.insert("end", f"\n▶ Iniciado en dificultad: {diff}\n")
    
    def pause(self):
        """Pausar"""
        self.bot.pause()
        if self.bot.paused:
            self.pause_btn.configure(text="▶ Reanudar")
            self.status_label.configure(text="🟡 Pausado")
            self.log_text.insert("end", "⏸ Pausado\n")
        else:
            self.pause_btn.configure(text="⏸ Pausar")
            self.status_label.configure(text="🟢 Ejecutando")
            self.log_text.insert("end", "▶ Reanudado\n")
    
    def stop(self):
        """Detener"""
        self.bot.stop()
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="⏸ Pausar")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="⚪ Detenido")
        self.log_text.insert("end", "⏹ Detenido\n")
    
    def on_close(self):
        """Al cerrar"""
        if self.bot.running:
            if messagebox.askokcancel("Salir", "¿Detener GARGUEL?"):
                self.bot.stop()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Ejecutar"""
        self.root.mainloop()


if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           ⚽ GARGUEL v1.1 SIMPLE ⚽                            ║
║         Bot de Farmeo Simplificado                           ║
║                                                              ║
║              Copyright (c) 2026 kazah-png                    ║
║        GitHub: https://github.com/kazah-png/GARGUEL         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🚀 Versión simplificada - Sin dependencias avanzadas
✅ Funciona sin: psutil, matplotlib, sklearn
    """)
    
    try:
        bot = GarguelBot()
        app = SimpleGUI(bot)
        app.run()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
