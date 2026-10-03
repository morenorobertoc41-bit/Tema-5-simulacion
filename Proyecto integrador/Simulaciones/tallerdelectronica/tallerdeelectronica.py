import math
import random
import time
import tkinter as tk
from tkinter import ttk

# Colores y estilo de la interfaz (Tema oscuro adaptado)
BG_DARK = "#030712"
PANEL_BG = "#0f172a"
TEXT_LIGHT = "#f8fafc"
TEXT_MUTED = "#94a3b8"
ACCENT_CYAN = "#38bdf8"
ACCENT_EMERALD = "#10b981"
ACCENT_AMBER = "#f59e0b"

class TallerElectronicaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Taller de Electrónica 2D - Simulación")
        self.root.geometry("1366x768")
        self.root.configure(bg=BG_DARK)

        # Variables de control de simulación
        self.is_running = False
        self.sim_speed = 5
        self.simulation_time = 480 # Inicia a las 08:00 del Día 1
        self.total_equipments_target = 50
        self.equipments_spawned = 0
        self.next_spawn_in = 0
        self.completed_count = 0
        self.total_time_accumulated = 0

        # Definición de estaciones
        self.stations = [
            {"id": "recepcion", "name": "1. Recepción", "x": 0.12, "y": 0.35, "duration": 5, "tech": "Técnico 1", "queue": [], "currentItem": None, "progress": 0},
            {"id": "diagnostico", "name": "2. Diagnóstico", "x": 0.32, "y": 0.35, "duration": 15, "tech": "Técnico 2", "queue": [], "currentItem": None, "progress": 0},
            {"id": "reparacion", "name": "3. Reparación", "x": 0.55, "y": 0.35, "duration": 45, "tech": "Técnico 3", "queue": [], "currentItem": None, "progress": 0},
            {"id": "calidad", "name": "4. Pruebas de Calidad", "x": 0.75, "y": 0.35, "duration": 10, "tech": "Técnico 2", "queue": [], "currentItem": None, "progress": 0},
            {"id": "entrega", "name": "5. Entrega y Fact.", "x": 0.90, "y": 0.65, "duration": 5, "tech": "Técnico 1", "queue": [], "currentItem": None, "progress": 0}
        ]

        self.equipments = []

        self.create_widgets()
        self.last_time = time.time()
        self.update_loop()

    def create_widgets(self):
        # Header principal
        header_frame = tk.Frame(self.root, bg=PANEL_BG, height=60)
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        title_lbl = tk.Label(header_frame, text="Taller de Electrónica 2D (Simulación)", fg=ACCENT_CYAN, bg=PANEL_BG, font=("Inter", 14, "bold"))
        title_lbl.pack(side=tk.LEFT, padx=15)

        controls_frame = tk.Frame(header_frame, bg=PANEL_BG)
        controls_frame.pack(side=tk.RIGHT, padx=15)

        self.btn_play = tk.Button(controls_frame, text="▶ Iniciar Simulación", bg="#059669", fg="white", font=("Inter", 10, "bold"), command=self.start_sim)
        self.btn_play.pack(side=tk.LEFT, padx=5)

        self.btn_pause = tk.Button(controls_frame, text="⏸ Pausar", bg="#d97706", fg="white", font=("Inter", 10, "bold"), state=tk.DISABLED, command=self.pause_sim)
        self.btn_pause.pack(side=tk.LEFT, padx=5)

        self.btn_reset = tk.Button(controls_frame, text="🔄 Reiniciar", bg="#475569", fg="white", font=("Inter", 10, "bold"), command=self.reset_sim)
        self.btn_reset.pack(side=tk.LEFT, padx=5)

        tk.Label(controls_frame, text="Velocidad:", fg=TEXT_MUTED, bg=PANEL_BG, font=("Inter", 10)).pack(side=tk.LEFT, padx=(10, 2))
        self.speed_var = tk.StringVar(value="5x Rápido")
        self.speed_combo = ttk.Combobox(controls_frame, textvariable=self.speed_var, values=["1x (Real)", "5x Rápido", "15x Turbo", "30x Ultra"], width=12, state="readonly")
        self.speed_combo.pack(side=tk.LEFT, padx=5)
        self.speed_combo.bind("<<ComboboxSelected>>", self.change_speed)

        # Contenedor Principal
        main_pane = tk.Frame(self.root, bg=BG_DARK)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Columna Izquierda: Canvas + Métricas
        left_col = tk.Frame(main_pane, bg=BG_DARK)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        canvas_container = tk.Frame(left_col, bg=PANEL_BG, bd=1, relief=tk.SOLID)
        canvas_container.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        canvas_top_bar = tk.Frame(canvas_container, bg=PANEL_BG)
        canvas_top_bar.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(canvas_top_bar, text="Plano General del Taller (Estaciones y Técnicos)", fg=TEXT_LIGHT, bg=PANEL_BG, font=("Inter", 11, "bold")).pack(side=tk.LEFT)
        self.clock_lbl = tk.Label(canvas_top_bar, text="Día 1 - 08:00", fg=ACCENT_CYAN, bg="#082f49", font=("Inter", 10, "bold"), padx=10, relief=tk.SOLID, bd=1)
        self.clock_lbl.pack(side=tk.RIGHT)

        # Contenedor wrapper para el canvas y mensaje flotante sin solaparse
        canvas_wrapper = tk.Frame(canvas_container, bg="#090d16")
        canvas_wrapper.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(canvas_wrapper, bg="#090d16", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Mensaje flotante independiente (superpuesto abajo a la izquierda)
        self.overlay_frame = tk.Frame(canvas_wrapper, bg="#0f172a", bd=1, relief=tk.SOLID, padx=12, pady=8)
        self.overlay_frame.place(relx=0.03, rely=0.85, anchor=tk.W)
        tk.Label(
            self.overlay_frame, 
            text="Presiona Iniciar Simulación para comenzar el flujo de los 50 equipos.", 
            fg=TEXT_MUTED, bg="#0f172a", font=("Inter", 9)
        ).pack()

        # Panel inferior de métricas
        metrics_frame = tk.Frame(left_col, bg=BG_DARK)
        metrics_frame.pack(fill=tk.X, pady=(0, 5))

        self.stat_total_lbl = self.create_metric_card(metrics_frame, "Equipos Totales", "50", 0)
        self.stat_process_lbl = self.create_metric_card(metrics_frame, "En Proceso", "0", 1)
        self.stat_completed_lbl = self.create_metric_card(metrics_frame, "Completados", "0", 2)
        self.stat_avg_lbl = self.create_metric_card(metrics_frame, "Tiempo Promedio", "0 min", 3)

        # Columna Derecha: Técnicos y Parámetros
        right_col = tk.Frame(main_pane, bg=BG_DARK, width=320)
        right_col.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))

        tech_card = tk.Frame(right_col, bg=PANEL_BG, bd=1, relief=tk.SOLID, padx=10, pady=10)
        tech_card.pack(fill=tk.X, pady=(0, 10))

        tk.Label(tech_card, text="Personal Técnico Asignado", fg=ACCENT_CYAN, bg=PANEL_BG, font=("Inter", 11, "bold")).pack(anchor=tk.W, pady=(0, 8))

        self.tech_status_labels = {}
        self.tech_task_labels = {}
        techs_info = [
            ("Técnico 1", "Recepción & Entrega/Facturación"),
            ("Técnico 2", "Diagnóstico & Pruebas de calidad"),
            ("Técnico 3", "Reparación y mantenimiento + Retrabajo")
        ]
        for t_name, t_desc in techs_info:
            f = tk.Frame(tech_card, bg="#1e293b", padx=8, pady=6)
            f.pack(fill=tk.X, pady=4)
            top_f = tk.Frame(f, bg="#1e293b")
            top_f.pack(fill=tk.X)
            tk.Label(top_f, text=t_name, fg=ACCENT_CYAN, bg="#1e293b", font=("Inter", 10, "bold")).pack(side=tk.LEFT)
            st_lbl = tk.Label(top_f, text="Libre", fg=TEXT_MUTED, bg="#0f172a", font=("Inter", 9), padx=4)
            st_lbl.pack(side=tk.RIGHT)
            self.tech_status_labels[t_name] = st_lbl

            tk.Label(f, text=t_desc, fg=TEXT_MUTED, bg="#1e293b", font=("Inter", 9)).pack(anchor=tk.W)
            tsk_lbl = tk.Label(f, text="Carga actual: Ninguna", fg=TEXT_LIGHT, bg="#1e293b", font=("Inter", 9, "italic"))
            tsk_lbl.pack(anchor=tk.W)
            self.tech_task_labels[t_name] = tsk_lbl

        doc_card = tk.Frame(right_col, bg=PANEL_BG, bd=1, relief=tk.SOLID, padx=10, pady=10)
        doc_card.pack(fill=tk.BOTH, expand=True)

        tk.Label(doc_card, text="Parámetros de la Simulación", fg="#a855f7", bg=PANEL_BG, font=("Inter", 11, "bold")).pack(anchor=tk.W, pady=(0, 8))
        doc_text = (
            "• 50 equipos totales.\n"
            "• Llegada: ~15 min promedio.\n"
            "• Recepción: 5 min\n"
            "• Diagnóstico: 15 min\n"
            "• Reparación: 45 min\n"
            "• Calidad: 10 min (20% retrabajo)\n"
            "• Entrega: 5 min"
        )
        tk.Label(doc_card, text=doc_text, fg=TEXT_MUTED, bg=PANEL_BG, font=("Inter", 9), justify=tk.LEFT).pack(anchor=tk.W)

    def create_metric_card(self, parent, title, initial_val, col):
        card = tk.Frame(parent, bg=PANEL_BG, bd=1, relief=tk.SOLID, padx=10, pady=8)
        card.grid(row=0, column=col, sticky="nsew", padx=2)
        parent.columnconfigure(col, weight=1)
        tk.Label(card, text=title, fg=TEXT_MUTED, bg=PANEL_BG, font=("Inter", 9)).pack(anchor=tk.W)
        val_lbl = tk.Label(card, text=initial_val, fg=TEXT_LIGHT, bg=PANEL_BG, font=("Inter", 12, "bold"))
        val_lbl.pack(anchor=tk.W)
        return val_lbl

    def start_sim(self):
        self.is_running = True
        self.btn_play.config(state=tk.DISABLED)
        self.btn_pause.config(state=tk.NORMAL)
        self.overlay_frame.place_forget() # Oculta el mensaje flotante al iniciar

    def pause_sim(self):
        self.is_running = False
        self.btn_play.config(state=tk.NORMAL)
        self.btn_pause.config(state=tk.DISABLED)

    def reset_sim(self):
        self.is_running = False
        self.simulation_time = 480
        self.equipments_spawned = 0
        self.next_spawn_in = 0
        self.equipments = []
        self.completed_count = 0
        self.total_time_accumulated = 0
        for s in self.stations:
            s["queue"] = []
            s["currentItem"] = None
            s["progress"] = 0
        self.btn_play.config(state=tk.NORMAL)
        self.btn_pause.config(state=tk.DISABLED)
        self.overlay_frame.place(relx=0.03, rely=0.85, anchor=tk.W) # Vuelve a mostrar el mensaje flotante
        self.update_metrics_ui()
        self.draw_canvas()

    def change_speed(self, event):
        val = self.speed_var.get()
        if "1x" in val: self.sim_speed = 1
        elif "5x" in val: self.sim_speed = 5
        elif "15x" in val: self.sim_speed = 15
        elif "30x" in val: self.sim_speed = 30

    def update_loop(self):
        now = time.time()
        delta_time = (now - self.last_time) * 1000.0
        self.last_time = now

        if self.is_running:
            self.update_simulation(delta_time)

        self.draw_canvas()
        self.update_metrics_ui()
        self.root.after(30, self.update_loop)

    def update_simulation(self, delta_time):
        minutes_elapsed = (delta_time / 1000.0) * (self.sim_speed * 2)
        self.simulation_time += minutes_elapsed

        if self.equipments_spawned < self.total_equipments_target:
            self.next_spawn_in -= minutes_elapsed
            if self.next_spawn_in <= 0:
                self.equipments_spawned += 1
                eq = {
                    "id": self.equipments_spawned,
                    "name": f"EQ-{str(self.equipments_spawned).zfill(2)}",
                    "currentStationIndex": 0,
                    "state": "waiting_queue",
                    "x": 50, "y": 200,
                    "entryTime": self.simulation_time,
                    "totalTimeInSystem": 0,
                    "hasRetried": False
                }
                self.stations[0]["queue"].append(eq)
                self.equipments.append(eq)
                self.next_spawn_in = 8 + random.random() * 14

        for index, station in enumerate(self.stations):
            if not station["currentItem"] and len(station["queue"]) > 0:
                station["currentItem"] = station["queue"].pop(0)
                station["currentItem"]["state"] = "processing"
                station["progress"] = 0

            if station["currentItem"]:
                duration_minutes = station["duration"]
                progress_increment = (minutes_elapsed / duration_minutes) * 100.0
                station["progress"] += progress_increment

                if station["progress"] >= 100:
                    finished_item = station["currentItem"]
                    station["currentItem"] = None
                    station["progress"] = 0

                    if index == 2:
                        finished_item["currentStationIndex"] = 3
                        self.stations[3]["queue"].append(finished_item)
                    elif index == 3:
                        if not finished_item["hasRetried"] and random.random() < 0.20:
                            finished_item["hasRetried"] = True
                            finished_item["currentStationIndex"] = 2
                            self.stations[2]["queue"].append(finished_item)
                        else:
                            finished_item["currentStationIndex"] = 4
                            self.stations[4]["queue"].append(finished_item)
                    else:
                        finished_item["currentStationIndex"] += 1
                        if finished_item["currentStationIndex"] < len(self.stations):
                            self.stations[finished_item["currentStationIndex"]]["queue"].append(finished_item)
                        else:
                            finished_item["state"] = "completed"
                            finished_item["totalTimeInSystem"] = round(self.simulation_time - finished_item["entryTime"])
                            self.completed_count += 1
                            self.total_time_accumulated += finished_item["totalTimeInSystem"]

        c_width = self.canvas.winfo_width() or 800
        c_height = self.canvas.winfo_height() or 450

        for eq in self.equipments:
            if eq["state"] == "completed":
                target_x, target_y = c_width * 0.92, c_height * 0.85
            else:
                st_idx = eq["currentStationIndex"]
                st = self.stations[st_idx]
                st_x, st_y = c_width * st["x"], c_height * st["y"]
                if st["currentItem"] == eq:
                    target_x, target_y = st_x, st_y
                else:
                    try:
                        q_pos = st["queue"].index(eq)
                        target_x = st_x - 45 - (q_pos * 22)
                        target_y = st_y + 40
                    except ValueError:
                        target_x, target_y = st_x, st_y

            eq["x"] += (target_x - eq["x"]) * 0.1
            eq["y"] += (target_y - eq["y"]) * 0.1

    def draw_canvas(self):
        self.canvas.delete("draw_item")
        c_width = self.canvas.winfo_width() or 800
        c_height = self.canvas.winfo_height() or 450

        grid_size = 40
        for x in range(0, c_width, grid_size):
            self.canvas.create_line(x, 0, x, c_height, fill="#0f172a", tags="draw_item")
        for y in range(0, c_height, grid_size):
            self.canvas.create_line(0, y, c_width, y, fill="#0f172a", tags="draw_item")

        # Líneas de flujo principales
        self.canvas.create_line(
            c_width * 0.12, c_height * 0.35,
            c_width * 0.32, c_height * 0.35,
            c_width * 0.55, c_height * 0.35,
            c_width * 0.75, c_height * 0.35,
            c_width * 0.85, c_height * 0.35,
            c_width * 0.85, c_height * 0.65,
            c_width * 0.90, c_height * 0.65,
            fill="#0ea5e9", width=3, dash=(6, 6), tags="draw_item"
        )

        for idx, st in enumerate(self.stations):
            x, y = c_width * st["x"], c_height * st["y"]
            radius = 38
            bg_col = "#1e293b" if st["currentItem"] else "#0f172a"
            border_col = "#38bdf8" if st["currentItem"] else "#334155"

            self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=bg_col, outline=border_col, width=3, tags="draw_item")
            self.canvas.create_text(x, y - 12, text=st["name"], fill=TEXT_LIGHT, font=("Inter", 9, "bold"), tags="draw_item")
            self.canvas.create_text(x, y + 4, text=st["tech"], fill=TEXT_MUTED, font=("Inter", 8), tags="draw_item")
            self.canvas.create_text(x, y + 18, text=f"{st['duration']} min", fill=ACCENT_CYAN, font=("Inter", 8), tags="draw_item")

        out_x, out_y = c_width * 0.90, c_height * 0.85
        self.canvas.create_rectangle(out_x - 55, out_y - 25, out_x + 55, out_y + 25, fill="#064e3b", outline=ACCENT_EMERALD, width=2, tags="draw_item")
        self.canvas.create_text(out_x, out_y - 5, text="Área de Salida", fill=ACCENT_EMERALD, font=("Inter", 9, "bold"), tags="draw_item")
        self.canvas.create_text(out_x, out_y + 10, text=f"Completados: {self.completed_count}", fill=TEXT_LIGHT, font=("Inter", 8), tags="draw_item")

        for eq in self.equipments:
            fill_c = ACCENT_EMERALD if eq["state"] == "completed" else (ACCENT_CYAN if eq["state"] == "processing" else ACCENT_AMBER)
            self.canvas.create_oval(eq["x"] - 12, eq["y"] - 12, eq["x"] + 12, eq["y"] + 12, fill=fill_c, outline="white", width=2, tags="draw_item")
            self.canvas.create_text(eq["x"], eq["y"], text=str(eq["id"]), fill="#0f172a", font=("Inter", 8, "bold"), tags="draw_item")

    def update_metrics_ui(self):
        in_process = len([e for e in self.equipments if e["state"] != "completed"])
        avg_time = round(self.total_time_accumulated / self.completed_count) if self.completed_count > 0 else 0

        self.stat_total_lbl.config(text=str(self.equipments_spawned))
        self.stat_process_lbl.config(text=str(in_process))
        self.stat_completed_lbl.config(text=str(self.completed_count))
        self.stat_avg_lbl.config(text=f"{avg_time} min")

        total_mins = int(self.simulation_time)
        hours = (total_mins // 60) % 24 + 8
        mins = total_mins % 60
        day = total_mins // (24 * 60) + 1
        self.clock_lbl.config(text=f"Día {day} - {str(hours % 24).zfill(2)}:{str(mins).zfill(2)}")

        t1_busy = (self.stations[0]["currentItem"] is not None) or (self.stations[4]["currentItem"] is not None)
        self.tech_status_labels["Técnico 1"].config(text="Ocupado" if t1_busy else "Libre", fg=ACCENT_AMBER if t1_busy else ACCENT_EMERALD)
        t1_task = "Atendiendo Recepción" if self.stations[0]["currentItem"] else ("Atendiendo Entrega" if self.stations[4]["currentItem"] else "Ninguna")
        self.tech_task_labels["Técnico 1"].config(text=f"Carga actual: {t1_task}")

        t2_busy = (self.stations[1]["currentItem"] is not None) or (self.stations[3]["currentItem"] is not None)
        self.tech_status_labels["Técnico 2"].config(text="Ocupado" if t2_busy else "Libre", fg=ACCENT_AMBER if t2_busy else ACCENT_EMERALD)
        t2_task = "Diagnóstico técnico" if self.stations[1]["currentItem"] else ("Pruebas de calidad" if self.stations[3]["currentItem"] else "Ninguna")
        self.tech_task_labels["Técnico 2"].config(text=f"Carga actual: {t2_task}")

        t3_busy = self.stations[2]["currentItem"] is not None
        self.tech_status_labels["Técnico 3"].config(text="Ocupado" if t3_busy else "Libre", fg=ACCENT_AMBER if t3_busy else ACCENT_EMERALD)
        t3_task = "Reparación / Mantenimiento" if t3_busy else "Ninguna"
        self.tech_task_labels["Técnico 3"].config(text=f"Carga actual: {t3_task}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TallerElectronicaApp(root)
    root.mainloop()