"""
GARGUEL v1.3 - Bot Profesional
Archivo único - Genera .exe funcional
"""

import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import pyautogui
import time
import sqlite3
import threading
from pathlib import Path
from datetime import datetime

# Configuración de pyautogui
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3

class GarguelDatabase:
    """Gestor de base de datos"""
    
    def __init__(self):
        self.db_path = Path('garguel_data.db')
        self.init_db()
    
    def init_db(self):
        """Inicializar BD"""
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                difficulty TEXT,
                result TEXT,
                duration INTEGER
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_match(self, difficulty, result, duration):
        """Guardar partido"""
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            'INSERT INTO matches (timestamp, difficulty, result, duration) VALUES (?, ?, ?, ?)',
            (datetime.now().isoformat(), difficulty, result, duration)
        )
        conn.commit()
        conn.close()
    
    def get_stats(self):
        """Obtener estadísticas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM matches')
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM matches WHERE result='Victoria'")
        wins = cursor.fetchone()[0]
        
        cursor.execute('SELECT AVG(duration) FROM matches')
        avg_time = cursor.fetchone()[0] or 0
        
        conn.close()
        
        win_rate = (wins / total * 100) if total > 0 else 0
        
        return {
            'total': total,
            'wins': wins,
            'losses': total - wins,
            'win_rate': win_rate,
            'avg_time': int(avg_time)
        }


class GarguelBot:
    """Bot de farmeo con macro optimizada"""
    
    # Posiciones optimizadas (1920x1080)
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
    
    TIMINGS = {
        'click_wait': 0.5,
        'screen_load': 1.5,
        'skip_wait': 0.3,
        'match_first_half': 20,
        'match_second_half': 20,
        'result_screen': 2.0,
    }
    
    def __init__(self):
        self.running = False
        self.paused = False
        self.db = GarguelDatabase()
    
    def click_pos(self, pos_name, wait=None):
        """Click en posición"""
        if pos_name in self.POSITIONS:
            x, y = self.POSITIONS[pos_name]
            pyautogui.click(x, y)
            time.sleep(wait or self.TIMINGS['click_wait'])
            return True
        return False
    
    def farmeo_sequence(self, difficulty='Normal'):
        """Secuencia de farmeo"""
        start_time = time.time()
        
        try:
            # Inicio
            self.click_pos('inicio_partido', self.TIMINGS['screen_load'])
            
            # Dificultad
            diff_pos = {
                'Facil': 'boton_facil',
                'Normal': 'boton_normal',
                'Dificil': 'boton_dificil'
            }.get(difficulty, 'boton_normal')
            
            self.click_pos(diff_pos, self.TIMINGS['click_wait'])
            self.click_pos('confirmar', self.TIMINGS['screen_load'])
            
            # Skip intro
            for _ in range(5):
                if not self.running or self.paused:
                    break
                self.click_pos('skip_intro', self.TIMINGS['skip_wait'])
            
            # Auto mode
            time.sleep(2)
            self.click_pos('auto_button', self.TIMINGS['click_wait'])
            
            # Partido
            self.wait_with_check(self.TIMINGS['match_first_half'])
            self.wait_with_check(self.TIMINGS['match_second_half'])
            
            # Post-partido
            time.sleep(self.TIMINGS['result_screen'])
            
            for _ in range(3):
                if not self.running or self.paused:
                    break
                self.click_pos('continuar_1', self.TIMINGS['click_wait'])
                self.click_pos('continuar_2', self.TIMINGS['click_wait'])
            
            self.click_pos('volver_menu', self.TIMINGS['screen_load'])
            
            duration = int(time.time() - start_time)
            self.db.save_match(difficulty, 'Victoria', duration)
            
            return duration
            
        except Exception as e:
            print(f"Error: {e}")
            return 0
    
    def wait_with_check(self, seconds):
        """Esperar con check de pausa"""
        start = time.time()
        while time.time() - start < seconds:
            if not self.running:
                break
            if self.paused:
                time.sleep(0.5)
                continue
            time.sleep(0.5)
    
    def start(self, difficulty, callback=None):
        """Iniciar farmeo"""
        self.running = True
        self.paused = False
        
        def run():
            while self.running:
                if not self.paused:
                    duration = self.farmeo_sequence(difficulty)
                    if callback and duration > 0:
                        callback(f"Partido completado en {duration}s")
                else:
                    time.sleep(0.5)
        
        thread = threading.Thread(target=run, daemon=True)
        thread.start()
    
    def pause(self):
        self.paused = not self.paused
    
    def stop(self):
        self.running = False
        self.paused = False


class GarguelGUI:
    """Interfaz gráfica"""
    
    def __init__(self):
        self.bot = GarguelBot()
        
        # Ventana
        self.root = ctk.CTk()
        self.root.title("GARGUEL v1.3")
        
        # Configurar icono si existe
        icon_path = Path('icon.png')
        if icon_path.exists():
            try:
                self.root.iconbitmap(default='icon.png')
            except:
                pass
        
        # Ventana completa maximizada
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"{screen_width}x{screen_height}+0+0")
        self.root.state('zoomed')
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.create_ui()
    
    def create_ui(self):
        """Crear interfaz"""
        main_frame = ctk.CTkScrollableFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_header(main_frame)
        self.create_stats(main_frame)
        self.create_controls(main_frame)
        self.create_log(main_frame)
        self.create_status()
    
    def create_header(self, parent):
        """Header con logo"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(pady=20, fill="x")
        
        # Logo si existe
        icon_path = Path('icon.png')
        if icon_path.exists():
            try:
                logo_img = Image.open(icon_path).resize((120, 120))
                logo_photo = ctk.CTkImage(logo_img, size=(120, 120))
                ctk.CTkLabel(header, image=logo_photo, text="").pack()
            except:
                ctk.CTkLabel(header, text="⚽", font=("Arial", 80)).pack()
        else:
            ctk.CTkLabel(header, text="⚽", font=("Arial", 80)).pack()
        
        ctk.CTkLabel(
            header,
            text="GARGUEL v1.3",
            font=("Arial", 50, "bold"),
            text_color="#00d4ff"
        ).pack()
    
    def create_stats(self, parent):
        """Stats"""
        stats_frame = ctk.CTkFrame(parent)
        stats_frame.pack(pady=20, padx=30, fill="x")
        
        ctk.CTkLabel(
            stats_frame,
            text="ESTADISTICAS",
            font=("Arial", 16, "bold")
        ).pack(pady=15)
        
        grid = ctk.CTkFrame(stats_frame, fg_color="transparent")
        grid.pack(pady=10)
        
        self.stat_labels = {}
        stats = [
            ("total", "Total", "0"),
            ("wins", "Victorias", "0"),
            ("win_rate", "Win Rate", "0%"),
            ("avg", "Tiempo Avg", "0s")
        ]
        
        for i, (key, label, value) in enumerate(stats):
            frame = ctk.CTkFrame(grid, width=250, height=100)
            frame.grid(row=0, column=i, padx=15, pady=10)
            
            ctk.CTkLabel(frame, text=label, font=("Arial", 12)).pack(pady=8)
            self.stat_labels[key] = ctk.CTkLabel(
                frame,
                text=value,
                font=("Arial", 28, "bold"),
                text_color="#00ff88"
            )
            self.stat_labels[key].pack()
        
        self.update_stats()
    
    def create_controls(self, parent):
        """Controles"""
        controls = ctk.CTkFrame(parent)
        controls.pack(pady=20, padx=30, fill="x")
        
        ctk.CTkLabel(
            controls,
            text="CONTROLES",
            font=("Arial", 16, "bold")
        ).pack(pady=15)
        
        diff_frame = ctk.CTkFrame(controls, fg_color="transparent")
        diff_frame.pack(pady=10)
        
        ctk.CTkLabel(diff_frame, text="Dificultad:", font=("Arial", 14)).pack(pady=8)
        
        self.diff_var = ctk.StringVar(value="Normal")
        ctk.CTkOptionMenu(
            diff_frame,
            values=["Facil", "Normal", "Dificil"],
            variable=self.diff_var,
            width=350,
            height=50,
            font=("Arial", 14)
        ).pack(pady=5)
        
        btn_frame = ctk.CTkFrame(controls, fg_color="transparent")
        btn_frame.pack(pady=25)
        
        self.start_btn = ctk.CTkButton(
            btn_frame,
            text="▶ INICIAR FARMEO",
            command=self.start,
            width=280,
            height=70,
            font=("Arial", 18, "bold"),
            fg_color="#00cc66",
            hover_color="#00ff88"
        )
        self.start_btn.pack(side="left", padx=10)
        
        self.pause_btn = ctk.CTkButton(
            btn_frame,
            text="⏸ Pausar",
            command=self.pause,
            width=160,
            height=70,
            font=("Arial", 16, "bold"),
            state="disabled",
            fg_color="#ff9900"
        )
        self.pause_btn.pack(side="left", padx=10)
        
        self.stop_btn = ctk.CTkButton(
            btn_frame,
            text="⏹ Detener",
            command=self.stop,
            width=160,
            height=70,
            font=("Arial", 16, "bold"),
            state="disabled",
            fg_color="#ff3366"
        )
        self.stop_btn.pack(side="left", padx=10)
    
    def create_log(self, parent):
        """Log"""
        log_frame = ctk.CTkFrame(parent)
        log_frame.pack(pady=20, padx=30, fill="both", expand=True)
        
        ctk.CTkLabel(
            log_frame,
            text="REGISTRO",
            font=("Arial", 14, "bold")
        ).pack(pady=10)
        
        self.log_text = ctk.CTkTextbox(
            log_frame,
            height=250,
            font=("Consolas", 11)
        )
        self.log_text.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.log("✅ GARGUEL v1.3 iniciado")
        self.log("📍 Posiciones optimizadas cargadas")
        self.log("🎮 Listo para farmear")
    
    def create_status(self):
        """Status bar"""
        status = ctk.CTkFrame(self.root, height=50)
        status.pack(side="bottom", fill="x", pady=0)
        
        self.status_label = ctk.CTkLabel(
            status,
            text="● DETENIDO",
            font=("Arial", 14, "bold"),
            text_color="#888888"
        )
        self.status_label.pack(side="left", padx=30, pady=10)
        
        exit_btn = ctk.CTkButton(
            status,
            text="Salir",
            command=self.on_close,
            width=100,
            height=35,
            fg_color="#666666"
        )
        exit_btn.pack(side="right", padx=30, pady=7)
        
        ctk.CTkLabel(
            status,
            text="© 2026 kazah-png",
            font=("Arial", 10)
        ).pack(side="right", padx=20)
    
    def update_stats(self):
        """Actualizar stats"""
        stats = self.bot.db.get_stats()
        self.stat_labels["total"].configure(text=str(stats['total']))
        self.stat_labels["wins"].configure(text=str(stats['wins']))
        self.stat_labels["win_rate"].configure(text=f"{stats['win_rate']:.1f}%")
        self.stat_labels["avg"].configure(text=f"{stats['avg_time']}s")
    
    def log(self, message):
        """Log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
    
    def start(self):
        """Iniciar"""
        self.start_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(
            text="● EJECUTANDO",
            text_color="#00ff88"
        )
        
        self.log(f"🚀 Farmeo iniciado - Dificultad: {self.diff_var.get()}")
        self.bot.start(self.diff_var.get(), self.on_match_complete)
    
    def pause(self):
        """Pausar"""
        self.bot.pause()
        if self.bot.paused:
            self.pause_btn.configure(text="▶ Reanudar")
            self.status_label.configure(
                text="● PAUSADO",
                text_color="#ffaa00"
            )
            self.log("⏸ Pausado")
        else:
            self.pause_btn.configure(text="⏸ Pausar")
            self.status_label.configure(
                text="● EJECUTANDO",
                text_color="#00ff88"
            )
            self.log("▶ Reanudado")
    
    def stop(self):
        """Detener"""
        self.bot.stop()
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="⏸ Pausar")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(
            text="● DETENIDO",
            text_color="#888888"
        )
        self.log("⏹ Detenido")
    
    def on_match_complete(self, message):
        """Callback"""
        self.log(f"✅ {message}")
        self.update_stats()
    
    def on_close(self):
        """Cerrar"""
        if self.bot.running:
            if messagebox.askokcancel("Salir", "¿Detener GARGUEL y salir?"):
                self.bot.stop()
                self.root.destroy()
        else:
            self.root.destroy()
    
    def run(self):
        """Run"""
        self.root.mainloop()


if __name__ == "__main__":
    app = GarguelGUI()
    app.run()
