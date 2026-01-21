"""
Interfaz Gráfica Profesional para GARGUEL v1.1
Con visualización en tiempo real del aprendizaje de IA

Copyright (c) 2026 kazah-png
"""

import customtkinter as ctk
from tkinter import Canvas
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
from datetime import datetime
import threading
import time

# Configurar estilo moderno
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ModernCard(ctk.CTkFrame):
    """Tarjeta moderna con efecto hover"""
    
    def __init__(self, parent, title="", value="", icon="", color="#3498db", **kwargs):
        super().__init__(parent, corner_radius=15, **kwargs)
        
        self.color = color
        self.configure(fg_color=color)
        
        # Icono
        if icon:
            icon_label = ctk.CTkLabel(
                self, 
                text=icon, 
                font=ctk.CTkFont(size=40),
                text_color="white"
            )
            icon_label.pack(pady=(20, 5))
        
        # Valor principal
        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            font=ctk.CTkFont(size=36, weight="bold"),
            text_color="white"
        )
        self.value_label.pack(pady=5)
        
        # Título
        title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=14),
            text_color="white"
        )
        title_label.pack(pady=(0, 20))
        
    def update_value(self, new_value):
        """Actualizar valor"""
        self.value_label.configure(text=new_value)


class AIVisualizationPanel(ctk.CTkFrame):
    """Panel de visualización del aprendizaje de IA"""
    
    def __init__(self, parent, ai_system, **kwargs):
        super().__init__(parent, corner_radius=10, **kwargs)
        
        self.ai_system = ai_system
        
        # Título
        title = ctk.CTkLabel(
            self,
            text="🧠 APRENDIZAJE DE IA EN TIEMPO REAL",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=10)
        
        # Frame para gráficos
        graphs_frame = ctk.CTkFrame(self, fg_color="transparent")
        graphs_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        graphs_frame.grid_columnconfigure((0, 1), weight=1)
        graphs_frame.grid_rowconfigure((0, 1), weight=1)
        
        # Crear gráficos
        self.create_loss_graph(graphs_frame)
        self.create_accuracy_graph(graphs_frame)
        self.create_neural_network_viz(graphs_frame)
        self.create_metrics_panel(graphs_frame)
        
        # Iniciar actualización automática
        self.update_visualizations()
        
    def create_loss_graph(self, parent):
        """Gráfico de pérdida (loss)"""
        frame = ctk.CTkFrame(parent, corner_radius=10)
        frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        label = ctk.CTkLabel(frame, text="📉 Loss (Error)", font=ctk.CTkFont(size=12, weight="bold"))
        label.pack(pady=5)
        
        # Matplotlib figure
        self.loss_fig = Figure(figsize=(4, 3), facecolor='#2b2b2b')
        self.loss_ax = self.loss_fig.add_subplot(111)
        self.loss_ax.set_facecolor('#1e1e1e')
        self.loss_ax.tick_params(colors='white')
        self.loss_ax.spines['bottom'].set_color('white')
        self.loss_ax.spines('top').set_color('white')
        self.loss_ax.spines['left'].set_color('white')
        self.loss_ax.spines['right'].set_color('white')
        
        self.loss_canvas = FigureCanvasTkAgg(self.loss_fig, frame)
        self.loss_canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
    def create_accuracy_graph(self, parent):
        """Gráfico de precisión"""
        frame = ctk.CTkFrame(parent, corner_radius=10)
        frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        label = ctk.CTkLabel(frame, text="📈 Accuracy", font=ctk.CTkFont(size=12, weight="bold"))
        label.pack(pady=5)
        
        self.acc_fig = Figure(figsize=(4, 3), facecolor='#2b2b2b')
        self.acc_ax = self.acc_fig.add_subplot(111)
        self.acc_ax.set_facecolor('#1e1e1e')
        self.acc_ax.tick_params(colors='white')
        self.acc_ax.spines['bottom'].set_color('white')
        self.acc_ax.spines['top'].set_color('white')
        self.acc_ax.spines['left'].set_color('white')
        self.acc_ax.spines['right'].set_color('white')
        
        self.acc_canvas = FigureCanvasTkAgg(self.acc_fig, frame)
        self.acc_canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        
    def create_neural_network_viz(self, parent):
        """Visualización de la red neuronal"""
        frame = ctk.CTkFrame(parent, corner_radius=10)
        frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        
        label = ctk.CTkLabel(frame, text="🕸️ Red Neuronal", font=ctk.CTkFont(size=12, weight="bold"))
        label.pack(pady=5)
        
        self.nn_canvas = Canvas(frame, bg='#1e1e1e', highlightthickness=0)
        self.nn_canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Dibujar red neuronal
        self.draw_neural_network()
        
    def create_metrics_panel(self, parent):
        """Panel de métricas de IA"""
        frame = ctk.CTkFrame(parent, corner_radius=10)
        frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        
        label = ctk.CTkLabel(frame, text="📊 Métricas de IA", font=ctk.CTkFont(size=12, weight="bold"))
        label.pack(pady=10)
        
        self.metrics_text = ctk.CTkTextbox(frame, font=ctk.CTkFont(size=10))
        self.metrics_text.pack(fill="both", expand=True, padx=10, pady=10)
        
    def draw_neural_network(self):
        """Dibujar representación visual de la red neuronal"""
        try:
            data = self.ai_system.get_learning_visualization_data()
            layers = data['neural_network']['layers']
            
            self.nn_canvas.delete("all")
            
            width = self.nn_canvas.winfo_width() or 300
            height = self.nn_canvas.winfo_height() or 200
            
            layer_spacing = width / (len(layers) + 1)
            
            # Dibujar neuronas por capa
            neurons_pos = []
            
            for i, layer_size in enumerate(layers):
                x = layer_spacing * (i + 1)
                layer_neurons = []
                
                neuron_spacing = height / (layer_size + 1)
                
                for j in range(min(layer_size, 10)):  # Max 10 neuronas visibles
                    y = neuron_spacing * (j + 1)
                    
                    # Dibujar conexiones si no es la primera capa
                    if i > 0:
                        for prev_x, prev_y in neurons_pos[-1]:
                            self.nn_canvas.create_line(
                                prev_x, prev_y, x, y,
                                fill='#3498db', width=1
                            )
                    
                    layer_neurons.append((x, y))
                
                neurons_pos.append(layer_neurons)
                
            # Dibujar neuronas encima de las conexiones
            for layer in neurons_pos:
                for x, y in layer:
                    self.nn_canvas.create_oval(
                        x-8, y-8, x+8, y+8,
                        fill='#2ecc71', outline='#27ae60', width=2
                    )
                    
        except Exception as e:
            pass
    
    def update_visualizations(self):
        """Actualizar todas las visualizaciones"""
        try:
            data = self.ai_system.get_learning_visualization_data()
            
            # Actualizar gráfico de loss
            losses = data['history']['losses']
            if losses:
                self.loss_ax.clear()
                self.loss_ax.plot(losses, color='#e74c3c', linewidth=2)
                self.loss_ax.set_title('Loss over Time', color='white')
                self.loss_ax.set_xlabel('Epoch', color='white')
                self.loss_ax.set_ylabel('Loss', color='white')
                self.loss_ax.grid(True, alpha=0.3)
                self.loss_canvas.draw()
            
            # Actualizar gráfico de accuracy
            accuracies = data['history']['accuracies']
            if accuracies:
                self.acc_ax.clear()
                self.acc_ax.plot(accuracies, color='#2ecc71', linewidth=2)
                self.acc_ax.set_title('Accuracy over Time', color='white')
                self.acc_ax.set_xlabel('Epoch', color='white')
                self.acc_ax.set_ylabel('Accuracy (%)', color='white')
                self.acc_ax.set_ylim(0, 100)
                self.acc_ax.grid(True, alpha=0.3)
                self.acc_canvas.draw()
            
            # Actualizar métricas
            metrics = data['metrics']
            metrics_text = f"""
Muestras Entrenadas: {metrics['total_samples']}
Sesiones de Entrenamiento: {metrics['total_training_sessions']}

Accuracy Actual: {metrics['current_accuracy']:.2f}%
Mejor Accuracy: {metrics['best_accuracy']:.2f}%

Nivel de Confianza: {metrics['confidence_level']:.1f}%
Learning Rate: {metrics['learning_rate']}

Total Parámetros: {data['neural_network']['total_parameters']}
Arquitectura: {'-'.join(map(str, data['neural_network']['layers']))}
            """
            
            self.metrics_text.delete("1.0", "end")
            self.metrics_text.insert("1.0", metrics_text.strip())
            
            # Redibujar red neuronal
            self.draw_neural_network()
            
        except Exception as e:
            pass
        
        # Actualizar cada 2 segundos
        self.after(2000, self.update_visualizations)


class ProfessionalDashboard(ctk.CTkFrame):
    """Dashboard principal profesional"""
    
    def __init__(self, parent, bot, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        
        self.bot = bot
        
        # Crear grid
        self.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Fila de tarjetas
        self.create_stat_cards()
        
        # Panel principal con tabs
        self.create_main_panel()
        
    def create_stat_cards(self):
        """Crear tarjetas de estadísticas modernas"""
        stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        stats_frame.grid(row=0, column=0, columnspan=4, sticky="ew", padx=10, pady=10)
        stats_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        s = self.bot.stats
        
        self.card_matches = ModernCard(
            stats_frame,
            title="Total Partidos",
            value=str(s['total']),
            icon="⚽",
            color="#3498db"
        )
        self.card_matches.grid(row=0, column=0, padx=5, sticky="ew")
        
        self.card_winrate = ModernCard(
            stats_frame,
            title="Win Rate",
            value=f"{s['win_rate']:.1f}%",
            icon="🏆",
            color="#2ecc71"
        )
        self.card_winrate.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.card_streak = ModernCard(
            stats_frame,
            title="Racha Actual",
            value=f"{s['racha_actual']} 🔥",
            icon="⚡",
            color="#f39c12"
        )
        self.card_streak.grid(row=0, column=2, padx=5, sticky="ew")
        
        avg_time = self.bot.fmt_time(s['avg_total']) if s['avg_total'] > 0 else "0s"
        self.card_avgtime = ModernCard(
            stats_frame,
            title="Tiempo Promedio",
            value=avg_time,
            icon="⏱️",
            color="#9b59b6"
        )
        self.card_avgtime.grid(row=0, column=3, padx=5, sticky="ew")
        
    def create_main_panel(self):
        """Panel principal con tabs"""
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.grid(row=1, column=0, columnspan=4, sticky="nsew", padx=10, pady=10)
        
        # Tabs
        tab_ai = self.tabview.add("🧠 IA & Aprendizaje")
        tab_stats = self.tabview.add("📊 Estadísticas")
        tab_performance = self.tabview.add("💻 Rendimiento")
        tab_history = self.tabview.add("📜 Historial")
        
        # Contenido de tabs
        self.setup_ai_tab(tab_ai)
        self.setup_stats_tab(tab_stats)
        self.setup_performance_tab(tab_performance)
        self.setup_history_tab(tab_history)
        
    def setup_ai_tab(self, parent):
        """Tab de IA con visualización"""
        if hasattr(self.bot, 'ai_system'):
            self.ai_viz = AIVisualizationPanel(parent, self.bot.ai_system)
            self.ai_viz.pack(fill="both", expand=True)
        else:
            label = ctk.CTkLabel(parent, text="Sistema de IA no disponible")
            label.pack(pady=20)
    
    def setup_stats_tab(self, parent):
        """Tab de estadísticas detalladas"""
        # Frame con scroll
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        s = self.bot.stats
        
        # Sección: Resumen General
        section1 = ctk.CTkFrame(scroll_frame)
        section1.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            section1,
            text="📊 RESUMEN GENERAL",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        stats_text = f"""
Total de Partidos: {s['total']}
Victorias: {s['victorias']}
Derrotas: {s['derrotas']}
Win Rate: {s['win_rate']:.2f}%

Racha Actual: {s['racha_actual']} victorias
Mejor Racha: {s.get('mejor_racha', 0)} victorias
        """
        
        text_widget = ctk.CTkTextbox(section1, height=150, font=ctk.CTkFont(size=12))
        text_widget.pack(fill="x", padx=20, pady=10)
        text_widget.insert("1.0", stats_text.strip())
        text_widget.configure(state="disabled")
        
        # Sección: Tiempos
        section2 = ctk.CTkFrame(scroll_frame)
        section2.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            section2,
            text="⏱️ ANÁLISIS DE TIEMPOS",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        times_text = f"""
Tiempo Promedio: {self.bot.fmt_time(s['avg_total'])}
Récord Más Rápido: {self.bot.fmt_time(s['record'])}
Partido Más Lento: {self.bot.fmt_time(s['peor'])}

Promedio 1er Tiempo: {self.bot.fmt_time(s.get('avg_1t', 0))}
Promedio 2do Tiempo: {self.bot.fmt_time(s.get('avg_2t', 0))}
        """
        
        text_widget2 = ctk.CTkTextbox(section2, height=150, font=ctk.CTkFont(size=12))
        text_widget2.pack(fill="x", padx=20, pady=10)
        text_widget2.insert("1.0", times_text.strip())
        text_widget2.configure(state="disabled")
        
    def setup_performance_tab(self, parent):
        """Tab de rendimiento del sistema"""
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # CPU y RAM
        perf_frame = ctk.CTkFrame(scroll_frame)
        perf_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            perf_frame,
            text="💻 RENDIMIENTO DEL SISTEMA",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        cpu = self.bot.performance_monitor.get_avg_cpu()
        ram = self.bot.performance_monitor.get_avg_memory()
        
        # Barras de progreso
        ctk.CTkLabel(perf_frame, text=f"CPU: {cpu:.1f}%", font=ctk.CTkFont(size=12)).pack(pady=5)
        cpu_bar = ctk.CTkProgressBar(perf_frame, width=400)
        cpu_bar.pack(pady=5)
        cpu_bar.set(cpu / 100)
        
        ctk.CTkLabel(perf_frame, text=f"RAM: {ram:.1f}%", font=ctk.CTkFont(size=12)).pack(pady=5)
        ram_bar = ctk.CTkProgressBar(perf_frame, width=400)
        ram_bar.pack(pady=5)
        ram_bar.set(ram / 100)
        
        # Cache stats
        cache_frame = ctk.CTkFrame(scroll_frame)
        cache_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            cache_frame,
            text="📦 ESTADÍSTICAS DE CACHE",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        cache_stats = self.bot.detector.template_cache.get_stats()
        
        cache_text = f"""
Hit Rate: {cache_stats['hit_rate']:.2f}%
Total Hits: {cache_stats['total_hits']}
Total Misses: {cache_stats['total_misses']}
Templates en Cache: {cache_stats['cached_templates']}
        """
        
        text_widget = ctk.CTkTextbox(cache_frame, height=120, font=ctk.CTkFont(size=12))
        text_widget.pack(fill="x", padx=20, pady=10)
        text_widget.insert("1.0", cache_text.strip())
        text_widget.configure(state="disabled")
        
    def setup_history_tab(self, parent):
        """Tab de historial"""
        self.history_text = ctk.CTkTextbox(parent, font=ctk.CTkFont(size=10, family="Courier"))
        self.history_text.pack(fill="both", expand=True, padx=10, pady=10)
        self.load_history()
        
    def load_history(self):
        """Cargar historial de partidos"""
        try:
            import sqlite3
            import pandas as pd
            
            conn = sqlite3.connect(self.bot.db_path)
            matches = pd.read_sql_query("""
                SELECT timestamp, difficulty, result, total_time, 
                       first_half, second_half
                FROM matches
                ORDER BY timestamp DESC
                LIMIT 50
            """, conn)
            conn.close()
            
            self.history_text.delete("1.0", "end")
            
            if matches.empty:
                self.history_text.insert("end", "No hay partidos registrados.\n\n¡Inicia GARGUEL para comenzar!")
            else:
                self.history_text.insert("end", "═" * 90 + "\n")
                self.history_text.insert("end", "  HISTORIAL DE PARTIDOS (Últimos 50)\n")
                self.history_text.insert("end", "═" * 90 + "\n\n")
                
                for _, m in matches.iterrows():
                    ts = m['timestamp'][:19]
                    emoji = "🏆" if m['result'] == 'Victoria' else "💔"
                    total = self.bot.fmt_time(m['total_time'])
                    t1 = self.bot.fmt_time(m['first_half'])
                    t2 = self.bot.fmt_time(m['second_half'])
                    
                    line = f"{emoji} {ts} | {m['difficulty']:8s} | {total:7s} (1T:{t1:5s} 2T:{t2:5s})\n"
                    self.history_text.insert("end", line)
                    
        except Exception as e:
            self.history_text.insert("end", f"Error cargando historial: {e}")
    
    def update_cards(self):
        """Actualizar tarjetas de stats"""
        s = self.bot.stats
        
        self.card_matches.update_value(str(s['total']))
        self.card_winrate.update_value(f"{s['win_rate']:.1f}%")
        self.card_streak.update_value(f"{s['racha_actual']} 🔥")
        
        avg_time = self.bot.fmt_time(s['avg_total']) if s['avg_total'] > 0 else "0s"
        self.card_avgtime.update_value(avg_time)


# Continúa en el siguiente mensaje...


class ProfessionalGarguelGUI:
    """Interfaz gráfica profesional mejorada"""
    
    def __init__(self, bot):
        self.bot = bot
        self.thread = None
        self.setup_gui()
        
    def setup_gui(self):
        """Configurar interfaz"""
        self.root = ctk.CTk()
        self.root.title("⚽ GARGUEL v1.1 - Bot Profesional con IA - by kazah-png")
        self.root.geometry("1400x900")
        
        # Grid principal
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        
        # Crear componentes
        self.create_sidebar()
        self.create_main_content()
        self.create_status_bar()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def create_sidebar(self):
        """Barra lateral con controles"""
        sidebar = ctk.CTkFrame(self.root, width=280, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_propagate(False)
        
        # Logo y título
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(pady=20)
        
        # Intentar cargar logo épico
        try:
            from PIL import Image
            logo_path = Path("logo.png")
            if logo_path.exists():
                logo_img = Image.open(logo_path)
                # Redimensionar a 220x220
                logo_img = logo_img.resize((220, 220), Image.Resampling.LANCZOS)
                logo_photo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(220, 220))
                logo_label = ctk.CTkLabel(logo_frame, image=logo_photo, text="")
                logo_label.pack(pady=10)
            else:
                # Fallback a emoji
                logo = ctk.CTkLabel(logo_frame, text="⚽", font=ctk.CTkFont(size=60))
                logo.pack()
        except:
            # Fallback a emoji si hay error
            logo = ctk.CTkLabel(logo_frame, text="⚽", font=ctk.CTkFont(size=60))
            logo.pack()
        
        title = ctk.CTkLabel(
            logo_frame,
            text="GARGUEL",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(pady=(5, 0))
        
        subtitle = ctk.CTkLabel(
            logo_frame,
            text="v1.1 Pro with AI",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        subtitle.pack()
        
        author = ctk.CTkLabel(
            logo_frame,
            text="by kazah-png",
            font=ctk.CTkFont(size=10),
            text_color="gray60"
        )
        author.pack(pady=(3, 0))
        
        # Separador
        ctk.CTkFrame(sidebar, height=2, fg_color="gray30").pack(fill="x", pady=15, padx=20)
        
        # Controles
        controls_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        controls_frame.pack(fill="x", padx=20)
        
        ctk.CTkLabel(
            controls_frame,
            text="⚙️ Configuración",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(0, 10))
        
        # Dificultad
        ctk.CTkLabel(controls_frame, text="Dificultad:", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.diff_var = ctk.StringVar(value="Normal")
        diff_menu = ctk.CTkOptionMenu(
            controls_frame,
            values=["Fácil", "Normal", "Difícil"],
            variable=self.diff_var,
            width=240,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        diff_menu.pack(pady=(5, 15))
        
        # Botones principales
        self.start_btn = ctk.CTkButton(
            controls_frame,
            text="▶ INICIAR FARMEO",
            command=self.start,
            width=240,
            height=50,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        self.start_btn.pack(pady=5)
        
        self.pause_btn = ctk.CTkButton(
            controls_frame,
            text="⏸ Pausar",
            command=self.pause,
            width=240,
            height=40,
            font=ctk.CTkFont(size=13),
            state="disabled"
        )
        self.pause_btn.pack(pady=5)
        
        self.stop_btn = ctk.CTkButton(
            controls_frame,
            text="⏹ Detener",
            command=self.stop,
            width=240,
            height=40,
            font=ctk.CTkFont(size=13),
            state="disabled",
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        self.stop_btn.pack(pady=5)
        
        # Separador
        ctk.CTkFrame(sidebar, height=2, fg_color="gray30").pack(fill="x", pady=15, padx=20)
        
        # Funciones avanzadas
        advanced_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        advanced_frame.pack(fill="x", padx=20)
        
        ctk.CTkLabel(
            advanced_frame,
            text="🔧 Funciones Avanzadas",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=(0, 10))
        
        ctk.CTkButton(
            advanced_frame,
            text="🧠 Entrenar IA",
            command=self.train_ai,
            width=240,
            height=38,
            font=ctk.CTkFont(size=12)
        ).pack(pady=3)
        
        ctk.CTkButton(
            advanced_frame,
            text="📊 Exportar Excel",
            command=self.export_excel,
            width=240,
            height=38,
            font=ctk.CTkFont(size=12)
        ).pack(pady=3)
        
        ctk.CTkButton(
            advanced_frame,
            text="🔧 Auto-Calibrar",
            command=self.auto_calibrate,
            width=240,
            height=38,
            font=ctk.CTkFont(size=12)
        ).pack(pady=3)
        
        ctk.CTkButton(
            advanced_frame,
            text="💾 Crear Backup",
            command=self.create_backup,
            width=240,
            height=38,
            font=ctk.CTkFont(size=12)
        ).pack(pady=3)
        
    def create_main_content(self):
        """Contenido principal"""
        main_frame = ctk.CTkFrame(self.root)
        main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # Dashboard
        self.dashboard = ProfessionalDashboard(main_frame, self.bot)
        self.dashboard.pack(fill="both", expand=True)
        
    def create_status_bar(self):
        """Barra de estado"""
        status_frame = ctk.CTkFrame(self.root, height=40, corner_radius=0)
        status_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        # Estado
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="⚪ Detenido",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.status_label.pack(side="left", padx=20, pady=10)
        
        # Separador
        ctk.CTkFrame(status_frame, width=2, fg_color="gray30").pack(side="left", fill="y", padx=10)
        
        # Info de IA
        self.ai_status_label = ctk.CTkLabel(
            status_frame,
            text="🧠 IA: Listo",
            font=ctk.CTkFont(size=11)
        )
        self.ai_status_label.pack(side="left", padx=10)
        
        # Separador
        ctk.CTkFrame(status_frame, width=2, fg_color="gray30").pack(side="left", fill="y", padx=10)
        
        # Sistema
        self.system_label = ctk.CTkLabel(
            status_frame,
            text="💻 CPU: 0% | RAM: 0%",
            font=ctk.CTkFont(size=11)
        )
        self.system_label.pack(side="left", padx=10)
        
        # Copyright
        copyright_label = ctk.CTkLabel(
            status_frame,
            text="© 2026 kazah-png | GitHub: kazah-png/GARGUEL",
            font=ctk.CTkFont(size=9),
            text_color="gray"
        )
        copyright_label.pack(side="right", padx=20, pady=10)
        
    def start(self):
        """Iniciar farmeo"""
        self.start_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text="🟢 Ejecutando")
        
        diff = self.diff_var.get()
        
        self.thread = threading.Thread(
            target=self.bot.start_farming_enhanced,
            args=(diff,),
            daemon=True
        )
        self.thread.start()
        
        # Iniciar actualización de UI
        self.update_ui()
        
    def pause(self):
        """Pausar/reanudar"""
        self.bot.pause()
        if self.bot.paused:
            self.pause_btn.configure(text="▶ Reanudar")
            self.status_label.configure(text="🟡 Pausado")
        else:
            self.pause_btn.configure(text="⏸ Pausar")
            self.status_label.configure(text="🟢 Ejecutando")
            
    def stop(self):
        """Detener"""
        self.bot.stop()
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled", text="⏸ Pausar")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text="⚪ Detenido")
        self.dashboard.load_history()
        
    def train_ai(self):
        """Entrenar IA manualmente"""
        from tkinter import messagebox
        messagebox.showinfo("IA", "La IA se entrena automáticamente con cada partido.\n\n"
                           f"Muestras actuales: {self.bot.ai_system.learning_metrics['total_samples']}\n"
                           f"Accuracy: {self.bot.ai_system.learning_metrics['current_accuracy']:.2f}%")
        
    def export_excel(self):
        """Exportar a Excel"""
        from tkinter import messagebox
        
        if self.bot.export_complete_report():
            messagebox.showinfo("Éxito", "Reporte completo exportado a garguel_report.xlsx")
        else:
            messagebox.showerror("Error", "No se pudo exportar el reporte")
            
    def auto_calibrate(self):
        """Auto-calibrar región"""
        from tkinter import messagebox
        
        if self.bot.detector.auto_calibrate_region():
            messagebox.showinfo("Éxito", "Región calibrada y guardada en config.json")
        else:
            messagebox.showwarning("Advertencia", "No se pudo calibrar automáticamente")
            
    def create_backup(self):
        """Crear backup"""
        from tkinter import messagebox
        
        backup_path = self.bot.backup_manager.create_backup()
        if backup_path:
            messagebox.showinfo("Éxito", f"Backup creado:\n{backup_path}")
        else:
            messagebox.showerror("Error", "No se pudo crear backup")
            
    def update_ui(self):
        """Actualizar UI automáticamente"""
        if not self.bot.running:
            return
            
        # Actualizar tarjetas
        self.dashboard.update_cards()
        
        # Actualizar estado de IA
        if hasattr(self.bot, 'ai_system'):
            metrics = self.bot.ai_system.learning_metrics
            ai_text = f"🧠 IA: {metrics['total_samples']} muestras | {metrics['current_accuracy']:.1f}% accuracy"
            self.ai_status_label.configure(text=ai_text)
            
        # Actualizar sistema
        cpu = self.bot.performance_monitor.get_avg_cpu()
        ram = self.bot.performance_monitor.get_avg_memory()
        system_text = f"💻 CPU: {cpu:.1f}% | RAM: {ram:.1f}%"
        self.system_label.configure(text=system_text)
        
        # Repetir cada 2 segundos
        self.root.after(2000, self.update_ui)
        
    def on_close(self):
        """Al cerrar"""
        if self.bot.running:
            from tkinter import messagebox
            if messagebox.askokcancel("Salir", "¿Detener GARGUEL?"):
                self.bot.stop()
                # Guardar modelos de IA
                if hasattr(self.bot, 'ai_system'):
                    self.bot.ai_system.save_models()
                self.root.destroy()
        else:
            # Guardar modelos de IA
            if hasattr(self.bot, 'ai_system'):
                self.bot.ai_system.save_models()
            self.root.destroy()
            
    def run(self):
        """Ejecutar GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    print("Professional GUI Module for GARGUEL v1.1")
