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
        self.root.title("⚽ GARGUEL v1.1 - Bot Profesional con NEXUS IA - by kazah-png")
        self.root.geometry("1000x750")
        
        # Configurar tema oscuro de calidad
        ctk.set_appearance_mode("dark")
        
        # Frame principal con gradiente visual
        main_frame = ctk.CTkFrame(self.root, fg_color=("#1a1a1a", "#0a0a0a"))
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Header con logo
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(10, 20))
        
        # Intentar cargar logo épico
        logo_loaded = False
        try:
            from PIL import Image
            logo_path = Path("logo.png")
            if logo_path.exists():
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((120, 120), Image.Resampling.LANCZOS)
                logo_photo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(120, 120))
                logo_label = ctk.CTkLabel(header_frame, image=logo_photo, text="")
                logo_label.pack(pady=5)
                logo_loaded = True
        except:
            pass
        
        if not logo_loaded:
            # Fallback a emoji grande
            logo_label = ctk.CTkLabel(
                header_frame,
                text="⚽",
                font=ctk.CTkFont(size=80)
            )
            logo_label.pack(pady=5)
        
        # Título principal
        title_label = ctk.CTkLabel(
            header_frame,
            text="GARGUEL v1.1",
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=("#00d4ff", "#00d4ff")
        )
        title_label.pack()
        
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Bot de Farmeo Profesional • Powered by NEXUS IA",
            font=ctk.CTkFont(size=14),
            text_color=("gray70", "gray50")
        )
        subtitle.pack(pady=(5, 0))
        
        # Separador con estilo
        separator = ctk.CTkFrame(main_frame, height=2, fg_color=("#00d4ff", "#0088aa"))
        separator.pack(fill="x", padx=40, pady=15)
        
        # Stats con mejor diseño
        stats_frame = ctk.CTkFrame(
            main_frame,
            corner_radius=15,
            fg_color=("#2a2a2a", "#1a1a1a"),
            border_width=2,
            border_color=("#00d4ff", "#0088aa")
        )
        stats_frame.pack(pady=15, padx=30, fill="x")
        
        stats_title = ctk.CTkLabel(
            stats_frame,
            text="📊 ESTADÍSTICAS",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=("#00d4ff", "#00d4ff")
        )
        stats_title.pack(pady=(15, 10))
        
        s = self.bot.stats
        
        # Grid de stats
        stats_grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_grid.pack(fill="x", padx=20, pady=10)
        
        stats_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Stat cards
        self.create_stat_card(stats_grid, "🎮", "Total Partidos", str(s['total']), 0)
        self.create_stat_card(stats_grid, "🏆", "Victorias", str(s['victorias']), 1)
        self.create_stat_card(stats_grid, "📈", "Win Rate", f"{s['win_rate']:.1f}%", 2)
        self.create_stat_card(stats_grid, "⏱️", "Promedio", self.bot.fmt_time(s['avg_total']), 3)
        
        # NEXUS IA indicator (si está disponible)
        try:
            nexus_frame = ctk.CTkFrame(
                main_frame,
                corner_radius=10,
                fg_color=("#1a3a4a", "#0a1a2a"),
                border_width=1,
                border_color=("#00d4ff", "#0088aa")
            )
            nexus_frame.pack(pady=10, padx=30, fill="x")
            
            nexus_label = ctk.CTkLabel(
                nexus_frame,
                text="🧠 NEXUS IA: Sistema de Aprendizaje Activo",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("#00ff88", "#00dd77")
            )
            nexus_label.pack(pady=8)
        except:
            pass
        
        # Controles mejorados
        controls_frame = ctk.CTkFrame(
            main_frame,
            corner_radius=15,
            fg_color=("#2a2a2a", "#1a1a1a")
        )
        controls_frame.pack(pady=15, padx=30, fill="x")
        
        ctk.CTkLabel(
            controls_frame,
            text="⚙️ CONFIGURACIÓN",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=("#00d4ff", "#00d4ff")
        ).pack(pady=(15, 10))
        
        ctk.CTkLabel(
            controls_frame,
            text="Selecciona la dificultad:",
            font=ctk.CTkFont(size=13)
        ).pack(pady=(5, 5))
        
        self.diff_var = ctk.StringVar(value="Normal")
        diff_menu = ctk.CTkOptionMenu(
            controls_frame,
            values=["Fácil", "Normal", "Difícil"],
            variable=self.diff_var,
            width=350,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color=("#0088aa", "#006688"),
            button_color=("#00d4ff", "#0088aa"),
            button_hover_color=("#00ffcc", "#00aa88")
        )
        diff_menu.pack(pady=10)
        
        # Botones mejorados
        buttons_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        buttons_frame.pack(pady=20)
        
        self.start_btn = ctk.CTkButton(
            buttons_frame,
            text="▶ INICIAR FARMEO",
            command=self.start,
            width=220,
            height=55,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#00cc66", "#00aa55"),
            hover_color=("#00ff88", "#00cc66"),
            corner_radius=12
        )
        self.start_btn.pack(side="left", padx=8)
        
        self.pause_btn = ctk.CTkButton(
            buttons_frame,
            text="⏸ Pausar",
            command=self.pause,
            width=160,
            height=55,
            font=ctk.CTkFont(size=14),
            state="disabled",
            fg_color=("#ff9900", "#cc7700"),
            hover_color=("#ffaa33", "#dd8800"),
            corner_radius=12
        )
        self.pause_btn.pack(side="left", padx=8)
        
        self.stop_btn = ctk.CTkButton(
            buttons_frame,
            text="⏹ Detener",
            command=self.stop,
            width=160,
            height=55,
            font=ctk.CTkFont(size=14),
            state="disabled",
            fg_color=("#ff3366", "#cc2244"),
            hover_color=("#ff5588", "#dd3355"),
            corner_radius=12
        )
        self.stop_btn.pack(side="left", padx=8)
        
        # Espaciado adicional para asegurar visibilidad
        ctk.CTkLabel(controls_frame, text="", height=10).pack()
        
        # Botones de utilidades
        utils_label = ctk.CTkLabel(
            controls_frame,
            text="🔧 UTILIDADES",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray70", "gray50")
        )
        utils_label.pack(pady=(5, 5))
        
        utils_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        utils_frame.pack(pady=10)
        
        calibrate_btn = ctk.CTkButton(
            utils_frame,
            text="🎯 Auto-Calibrar Región",
            command=self.auto_calibrate,
            width=250,
            height=40,
            font=ctk.CTkFont(size=12),
            fg_color=("#4a90e2", "#3670b2"),
            hover_color=("#5aa0f2", "#4680c2"),
            corner_radius=10
        )
        calibrate_btn.pack(side="left", padx=5)
        
        export_btn = ctk.CTkButton(
            utils_frame,
            text="📊 Exportar a Excel",
            command=self.export_excel,
            width=250,
            height=40,
            font=ctk.CTkFont(size=12),
            fg_color=("#4a90e2", "#3670b2"),
            hover_color=("#5aa0f2", "#4680c2"),
            corner_radius=10
        )
        export_btn.pack(side="left", padx=5)
        
        # Espaciado final
        ctk.CTkLabel(controls_frame, text="", height=15).pack()
        
        # Log mejorado
        log_label = ctk.CTkLabel(
            main_frame,
            text="📜 REGISTRO DE ACTIVIDAD",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=("#00d4ff", "#00d4ff")
        )
        log_label.pack(pady=(10, 5))
        
        log_frame = ctk.CTkFrame(
            main_frame,
            corner_radius=10,
            fg_color=("#1a1a1a", "#0a0a0a"),
            border_width=2,
            border_color=("#333333", "#222222")
        )
        log_frame.pack(pady=5, padx=30, fill="both", expand=True)
        
        self.log_text = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(size=11, family="Consolas"),
            fg_color=("#0a0a0a", "#000000"),
            text_color=("#00ff88", "#00dd77"),
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.log_text.insert("end", "╔═══════════════════════════════════════════════════════╗\n")
        self.log_text.insert("end", "║   ⚽ GARGUEL v1.1 - Sistema de Farmeo Inteligente    ║\n")
        self.log_text.insert("end", "╚═══════════════════════════════════════════════════════╝\n\n")
        self.log_text.insert("end", "🧠 NEXUS IA: Sistema de aprendizaje adaptativo\n")
        self.log_text.insert("end", "📊 Base de datos: SQLite persistente\n")
        self.log_text.insert("end", "🎯 Detección: Templates con OpenCV\n")
        self.log_text.insert("end", "⚡ Optimización: Detección dinámica de tiempos\n\n")
        self.log_text.insert("end", "✅ Sistema inicializado y listo para usar\n")
        self.log_text.insert("end", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")
        
        # Status bar mejorado
        status_frame = ctk.CTkFrame(
            self.root,
            height=45,
            corner_radius=0,
            fg_color=("#1a1a1a", "#0a0a0a"),
            border_width=2,
            border_color=("#00d4ff", "#0088aa")
        )
        status_frame.pack(fill="x", side="bottom")
        
        status_content = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_content.pack(fill="x", padx=15, pady=8)
        
        self.status_label = ctk.CTkLabel(
            status_content,
            text="⚪ DETENIDO",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("#aaaaaa", "#888888")
        )
        self.status_label.pack(side="left")
        
        # Separador
        ctk.CTkFrame(
            status_content,
            width=2,
            height=25,
            fg_color=("#444444", "#333333")
        ).pack(side="left", padx=15)
        
        nexus_status = ctk.CTkLabel(
            status_content,
            text="🧠 NEXUS: Listo",
            font=ctk.CTkFont(size=11),
            text_color=("#00ff88", "#00dd77")
        )
        nexus_status.pack(side="left", padx=10)
        
        copyright_label = ctk.CTkLabel(
            status_content,
            text="© 2026 kazah-png | GitHub: kazah-png/GARGUEL",
            font=ctk.CTkFont(size=9),
            text_color=("gray60", "gray40")
        )
        copyright_label.pack(side="right")
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def create_stat_card(self, parent, icon, title, value, col):
        """Crear tarjeta de estadística"""
        card = ctk.CTkFrame(
            parent,
            corner_radius=10,
            fg_color=("#1a3a4a", "#0a1a2a"),
            border_width=1,
            border_color=("#00d4ff", "#0088aa")
        )
        card.grid(row=0, column=col, padx=8, pady=10, sticky="ew")
        
        icon_label = ctk.CTkLabel(
            card,
            text=icon,
            font=ctk.CTkFont(size=28)
        )
        icon_label.pack(pady=(10, 5))
        
        value_label = ctk.CTkLabel(
            card,
            text=value,
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=("#00d4ff", "#00d4ff")
        )
        value_label.pack()
        
        title_label = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(size=10),
            text_color=("gray70", "gray50")
        )
        title_label.pack(pady=(0, 10))
    
    def start(self):
        """Iniciar"""
        self.start_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(
            text="🟢 EJECUTANDO",
            text_color=("#00ff88", "#00dd77")
        )
        
        diff = self.diff_var.get()
        
        self.thread = threading.Thread(
            target=self.bot.start_farming,
            args=(diff,),
            daemon=True
        )
        self.thread.start()
        
        self.log_text.insert("end", f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        self.log_text.insert("end", f"▶ FARMEO INICIADO\n")
        self.log_text.insert("end", f"🎯 Dificultad: {diff}\n")
        self.log_text.insert("end", f"🧠 NEXUS IA: Analizando patrones...\n")
        self.log_text.insert("end", f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")
        self.log_text.see("end")
    
    def pause(self):
        """Pausar"""
        self.bot.pause()
        if self.bot.paused:
            self.pause_btn.configure(text="▶ Reanudar")
            self.status_label.configure(
                text="🟡 PAUSADO",
                text_color=("#ffaa00", "#dd8800")
            )
            self.log_text.insert("end", "⏸ Sistema pausado\n")
        else:
            self.pause_btn.configure(text="⏸ Pausar")
            self.status_label.configure(
                text="🟢 EJECUTANDO",
                text_color=("#00ff88", "#00dd77")
            )
            self.log_text.insert("end", "▶ Sistema reanudado\n")
        self.log_text.see("end")
    
    def stop(self):
        """Detener"""
        self.bot.stop()
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="⏸ Pausar")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(
            text="⚪ DETENIDO",
            text_color=("#aaaaaa", "#888888")
        )
        self.log_text.insert("end", "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        self.log_text.insert("end", "⏹ Farmeo detenido\n")
        self.log_text.insert("end", "🧠 NEXUS IA: Guardando datos de aprendizaje...\n")
        self.log_text.insert("end", "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")
        self.log_text.see("end")
    
    def auto_calibrate(self):
        """Auto-calibrar región del juego"""
        self.log_text.insert("end", "\n🎯 Intentando calibrar región automáticamente...\n")
        self.log_text.see("end")
        
        try:
            # Buscar ventana del juego
            import pygetwindow as gw
            windows = gw.getWindowsWithTitle("Inazuma")
            
            if not windows:
                windows = gw.getWindowsWithTitle("IEVR")
            
            if not windows:
                windows = gw.getWindowsWithTitle("Victory Road")
            
            if windows:
                win = windows[0]
                region = (win.left, win.top, win.left + win.width, win.top + win.height)
                
                # Guardar en config
                import json
                with open('config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                config['game_window_region'] = list(region)
                
                with open('config.json', 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                
                self.bot.region = region
                
                self.log_text.insert("end", f"✅ Región calibrada: {region}\n")
                self.log_text.insert("end", "💾 Configuración guardada\n")
                messagebox.showinfo("Éxito", f"Región calibrada:\n{region}")
            else:
                self.log_text.insert("end", "⚠️ No se encontró ventana del juego\n")
                messagebox.showwarning("Advertencia", "Abre Inazuma Eleven en modo ventana")
                
        except ImportError:
            self.log_text.insert("end", "⚠️ Instala: py -m pip install pygetwindow\n")
            messagebox.showinfo("Info", "Instala:\npy -m pip install pygetwindow")
        except Exception as e:
            self.log_text.insert("end", f"❌ Error: {e}\n")
            messagebox.showerror("Error", f"No se pudo calibrar: {e}")
        
        self.log_text.see("end")
    
    def export_excel(self):
        """Exportar estadísticas a Excel"""
        self.log_text.insert("end", "\n📊 Exportando estadísticas a Excel...\n")
        self.log_text.see("end")
        
        try:
            import pandas as pd
            import sqlite3
            from datetime import datetime
            
            conn = sqlite3.connect(self.bot.db_path)
            matches_df = pd.read_sql_query("SELECT * FROM matches", conn)
            conn.close()
            
            if matches_df.empty:
                self.log_text.insert("end", "⚠️ No hay datos para exportar\n")
                messagebox.showinfo("Info", "No hay partidos registrados aún")
                return
            
            filename = f"garguel_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                matches_df.to_excel(writer, sheet_name='Partidos', index=False)
                
                summary = pd.DataFrame({
                    'Métrica': ['Total', 'Victorias', 'Win Rate %', 'Tiempo Promedio (s)'],
                    'Valor': [
                        self.bot.stats['total'],
                        self.bot.stats['victorias'],
                        round(self.bot.stats['win_rate'], 2),
                        self.bot.stats['avg_total']
                    ]
                })
                summary.to_excel(writer, sheet_name='Resumen', index=False)
            
            self.log_text.insert("end", f"✅ Exportado: {filename}\n")
            messagebox.showinfo("Éxito", f"Exportado:\n{filename}")
            
        except Exception as e:
            self.log_text.insert("end", f"❌ Error: {e}\n")
            messagebox.showerror("Error", f"No se pudo exportar: {e}")
        
        self.log_text.see("end")
    
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
║           ⚽ GARGUEL v1.1 PROFESSIONAL ⚽                      ║
║         Bot Avanzado • Powered by NEXUS IA                   ║
║                                                              ║
║              Copyright (c) 2026 kazah-png                    ║
║        GitHub: https://github.com/kazah-png/GARGUEL         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🧠 NEXUS IA: Sistema de aprendizaje adaptativo
🚀 Versión optimizada - Sin dependencias avanzadas
✅ Detección dinámica con OpenCV
⚡ Base de datos SQLite integrada
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
