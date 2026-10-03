import math
import random
import time
import tkinter as tk
from tkinter import ttk


class ElectronicsShopSimulator:

  def __init__(self, root):
    self.root = root
    self.root.title(
        "Taller de Electrónica 2D - Simulación"
    )
    self.root.geometry("1320x760")
    self.root.configure(bg="#030712")

    # Variables de simulación
    self.is_running = False
    self.sim_speed = 5
    self.simulation_time = 480.0  # 08:00 AM
    self.total_equipments_target = 50
    self.equipments_spawned = 0
    self.next_spawn_in = 0.0

    self.equipments = []
    self.completed_count = 0
    self.total_time_accumulated = 0

    # Cantidad de técnicos en la estación de reparación (cuello de botella) -> Máximo 3
    self.repair_techs_count = 1

    # Estaciones del taller
    self.stations = [
        {
            "id": "recepcion",
            "name": "1. Recepción",
            "x": 0.12,
            "y": 0.35,
            "duration": 5,
            "tech": "Técnico 1",
            "queue": [],
            "current_item": None,
            "progress": 0.0,
        },
        {
            "id": "diagnostico",
            "name": "2. Diagnóstico",
            "x": 0.32,
            "y": 0.35,
            "duration": 15,
            "tech": "Técnico 2",
            "queue": [],
            "current_item": None,
            "progress": 0.0,
        },
        {
            "id": "reparacion",
            "name": "3. Reparación",
            "x": 0.55,
            "y": 0.35,
            "duration": 45,
            "tech": "Reparación (1-3)",
            "queue": [],
            "current_items": (
                []
            ),  # Soporta múltiples reparaciones en paralelo
        },
        {
            "id": "calidad",
            "name": "4. Pruebas Calidad",
            "x": 0.75,
            "y": 0.35,
            "duration": 10,
            "tech": "Técnico 2",
            "queue": [],
            "current_item": None,
            "progress": 0.0,
        },
        {
            "id": "entrega",
            "name": "5. Entrega y Fact.",
            "x": 0.90,
            "y": 0.65,
            "duration": 5,
            "tech": "Técnico 1",
            "queue": [],
            "current_item": None,
            "progress": 0.0,
        },
    ]

    self.setup_styles()
    self.create_widgets()

    self.last_update = time.time() * 1000
    self.run_loop()

  def setup_styles(self):
    self.style = ttk.Style()
    self.style.theme_use("clam")
    self.style.configure(
        "TCombobox", fieldbackground="#1e293b", background="#0f172a", foreground="#38bdf8"
    )

  def create_widgets(self):
    # Header Principal
    header_frame = tk.Frame(self.root, bg="#0f172a", height=60)
    header_frame.pack(side=tk.TOP, fill=tk.X)

    title_lbl = tk.Label(
        header_frame,
        text="Taller de Electrónica 2D",
        font=("Inter", 13, "bold"),
        bg="#0f172a",
        fg="#38bdf8",
    )
    title_lbl.pack(side=tk.LEFT, padx=15, pady=10)

    # Controles de simulación y botón extra
    controls_frame = tk.Frame(header_frame, bg="#0f172a")
    controls_frame.pack(side=tk.RIGHT, padx=15)

    # BOTÓN EXTRA PARA AGREGAR TÉCNICOS EN REPARACIÓN
    self.btn_repair_techs = tk.Button(
        controls_frame,
        text="🔧 Técnicos Reparación: 1",
        bg="#0284c7",
        fg="white",
        font=("Inter", 9, "bold"),
        relief=tk.FLAT,
        command=self.toggle_repair_techs,
        padx=8,
    )
    self.btn_repair_techs.pack(side=tk.LEFT, padx=5)

    self.btn_play = tk.Button(
        controls_frame,
        text="▶ Iniciar",
        bg="#059669",
        fg="white",
        font=("Inter", 9, "bold"),
        relief=tk.FLAT,
        command=self.start_sim,
        padx=8,
    )
    self.btn_play.pack(side=tk.LEFT, padx=5)

    self.btn_pause = tk.Button(
        controls_frame,
        text="⏸ Pausar",
        bg="#d97706",
        fg="white",
        font=("Inter", 9, "bold"),
        relief=tk.FLAT,
        command=self.pause_sim,
        state=tk.DISABLED,
        padx=8,
    )
    self.btn_pause.pack(side=tk.LEFT, padx=5)

    self.btn_reset = tk.Button(
        controls_frame,
        text="🔄 Reiniciar",
        bg="#334155",
        fg="white",
        font=("Inter", 9, "bold"),
        relief=tk.FLAT,
        command=self.reset_sim,
        padx=8,
    )
    self.btn_reset.pack(side=tk.LEFT, padx=5)

    tk.Label(
        controls_frame,
        text="Vel:",
        bg="#0f172a",
        fg="#94a3b8",
        font=("Inter", 9),
    ).pack(side=tk.LEFT, padx=(10, 2))
    self.speed_var = tk.StringVar(value="5x Rápido")
    speed_cb = ttk.Combobox(
        controls_frame,
        textvariable=self.speed_var,
        values=["1x (Real)", "5x Rápido", "15x Turbo", "30x Ultra"],
        width=10,
        state="readonly",
    )
    speed_cb.pack(side=tk.LEFT)
    speed_cb.bind("<<ComboboxSelected>>", self.change_speed)

    # Main Area
    main_frame = tk.Frame(self.root, bg="#030712")
    main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Panel Izquierdo: Canvas y Métricas
    left_panel = tk.Frame(main_frame, bg="#030712")
    left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    canvas_container = tk.Frame(
        left_panel, bg="#0f172a", highlightbackground="#1e293b", highlightthickness=1
    )
    canvas_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    self.canvas = tk.Canvas(
        canvas_container, bg="#0b0f19", highlightthickness=0
    )
    self.canvas.pack(fill=tk.BOTH, expand=True)
    self.canvas.bind("<Configure>", lambda e: self.draw())

    # Panel inferior de Métricas
    metrics_frame = tk.Frame(left_panel, bg="#030712", height=80)
    metrics_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))

    self.stat_total_lbl = self.create_metric_card(
        metrics_frame, "Equipos Totales", "50", "#3b82f6"
    )
    self.stat_process_lbl = self.create_metric_card(
        metrics_frame, "En Proceso", "0", "#f59e0b"
    )
    self.stat_completed_lbl = self.create_metric_card(
        metrics_frame, "Completados", "0", "#10b981"
    )
    self.stat_time_lbl = self.create_metric_card(
        metrics_frame, "Tiempo Promedio", "0 min", "#a855f7"
    )

    # Panel Derecho: Información y Técnicos
    right_panel = tk.Frame(
        main_frame, bg="#0f172a", width=300, highlightbackground="#1e293b"
    )
    right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
    right_panel.pack_propagate(False)

    tk.Label(
        right_panel,
        text="Personal Técnico Asignado",
        font=("Inter", 11, "bold"),
        bg="#0f172a",
        fg="#f8fafc",
    ).pack(anchor="w", padx=15, pady=(15, 10))

    self.tech_status_labels = []
    for t_name, t_desc in [
        (
            "Técnico 1 (Recepción / Entrega)",
            "Estaciones: Recepción & Facturación",
        ),
        (
            "Técnico 2 (Diagnóstico / Calidad)",
            "Estaciones: Diagnóstico & Pruebas",
        ),
        ("Técnico 3 (Especialistas)", "Estación: Reparación (Hasta 3)"),
    ]:
        f = tk.Frame(
            right_panel,
            bg="#1e293b",
            highlightbackground="#334155",
            highlightthickness=1,
        )
        f.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(
            f, text=t_name, font=("Inter", 9, "bold"), bg="#1e293b", fg="#38bdf8"
        ).pack(anchor="w", padx=10, pady=(5, 0))
        tk.Label(
            f, text=t_desc, font=("Inter", 8), bg="#1e293b", fg="#94a3b8"
        ).pack(anchor="w", padx=10)
        status_lbl = tk.Label(
            f,
            text="Estado: Libre",
            font=("Inter", 8, "bold"),
            bg="#1e293b",
            fg="#10b981",
        )
        status_lbl.pack(anchor="w", padx=10, pady=(0, 5))
        self.tech_status_labels.append(status_lbl)

    tk.Label(
        right_panel,
        text="Parámetros de Documentación",
        font=("Inter", 11, "bold"),
        bg="#0f172a",
        fg="#f8fafc",
    ).pack(anchor="w", padx=15, pady=(20, 10))

    params_text = (
        "• Llegada de equipos: 50 total (cada ~15 min).\n"
        "• Recepción: 5 min | Diagnóstico: 15 min.\n"
        "• Reparación: 45 min (Escalable a 3).\n"
        "• Pruebas de Calidad: 10 min.\n"
        "• Bucle de Retrabajo: 20% de fallos regresan\n"
        "  a la estación de Reparación."
    )
    tk.Label(
        right_panel,
        text=params_text,
        font=("Inter", 8),  # Corregido de 8.5 a 8
        bg="#0f172a",
        fg="#cbd5e1",
        justify=tk.LEFT,
    ).pack(anchor="w", padx=15)

    self.clock_lbl = tk.Label(
        right_panel,
        text="Tiempo: Día 1 - 08:00",
        font=("Inter", 10, "bold"),
        bg="#0f172a",
        fg="#38bdf8",
    )
    self.clock_lbl.pack(side=tk.BOTTOM, pady=20)

  def create_metric_card(self, parent, title, initial_value, color):
    card = tk.Frame(
        parent,
        bg="#0f172a",
        highlightbackground="#1e293b",
        highlightthickness=1,
    )
    card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)
    tk.Label(
        card, text=title, font=("Inter", 8), bg="#0f172a", fg="#94a3b8"
    ).pack(anchor="w", padx=8, pady=(8, 0))
    val_lbl = tk.Label(
        card,
        text=initial_value,
        font=("Inter", 13, "bold"),
        bg="#0f172a",
        fg=color,
    )
    val_lbl.pack(anchor="w", padx=8, pady=(0, 8))
    return val_lbl

  def toggle_repair_techs(self):
    self.repair_techs_count += 1
    if self.repair_techs_count > 3:
      self.repair_techs_count = 1
    self.btn_repair_techs.config(
        text=f"🔧 Técnicos Reparación: {self.repair_techs_count}"
    )

  def start_sim(self):
    self.is_running = True
    self.btn_play.config(state=tk.DISABLED)
    self.btn_pause.config(state=tk.NORMAL)

  def pause_sim(self):
    self.is_running = False
    self.btn_play.config(state=tk.NORMAL)
    self.btn_pause.config(state=tk.DISABLED)

  def reset_sim(self):
    self.is_running = False
    self.simulation_time = 480.0
    self.equipments_spawned = 0
    self.next_spawn_in = 0.0
    self.equipments.clear()
    self.completed_count = 0
    self.total_time_accumulated = 0
    for st in self.stations:
      st["queue"].clear()
      if "current_items" in st:
        st["current_items"].clear()
      else:
        st["current_item"] = None
        st["progress"] = 0.0
    self.btn_play.config(state=tk.NORMAL)
    self.btn_pause.config(state=tk.DISABLED)
    self.update_metrics()
    self.draw()

  def change_speed(self, event):
    val = self.speed_var.get()
    if "1x" in val:
      self.sim_speed = 1
    elif "5x" in val:
      self.sim_speed = 5
    elif "15x" in val:
      self.sim_speed = 15
    elif "30x" in val:
      self.sim_speed = 30

  class EquipmentObj:

    def __init__(self, eq_id):
      self.id = eq_id
      self.name = f"EQ-{eq_id:02d}"
      self.current_station_index = 0
      self.state = "waiting_queue"
      self.x = 50.0
      self.y = 200.0
      self.entry_time = 480.0
      self.total_time = 0
      self.has_retried = False

  def run_loop(self):
    current_ticks = time.time() * 1000
    delta_ms = current_ticks - self.last_update
    self.last_update = current_ticks

    if self.is_running and delta_ms > 0:
      delta_seconds = delta_ms / 1000.0
      minutes_elapsed = delta_seconds * (self.sim_speed * 2)
      self.simulation_time += minutes_elapsed

      if self.equipments_spawned < self.total_equipments_target:
        self.next_spawn_in -= minutes_elapsed
        if self.next_spawn_in <= 0:
          self.equipments_spawned += 1
          eq = self.EquipmentObj(self.equipments_spawned)
          eq.entry_time = self.simulation_time
          self.stations[0]["queue"].append(eq)
          self.equipments.append(eq)
          self.next_spawn_in = random.uniform(8, 22)

      for idx in [0, 1, 3, 4]:
        station = self.stations[idx]
        if not station["current_item"] and station["queue"]:
          station["current_item"] = station["queue"].pop(0)
          station["current_item"].state = "processing"
          station["progress"] = 0.0

        if station["current_item"]:
          item = station["current_item"]
          progress_increment = (minutes_elapsed / station["duration"]) * 100.0
          station["progress"] += progress_increment

          if station["progress"] >= 100.0:
            station["current_item"] = None
            station["progress"] = 0.0

            if idx == 3:
              if not item.has_retried and random.random() < 0.20:
                item.has_retried = True
                item.current_station_index = 2
                self.stations[2]["queue"].append(item)
              else:
                item.current_station_index = 4
                self.stations[4]["queue"].append(item)
            else:
              item.current_station_index += 1
              if item.current_station_index < len(self.stations):
                self.stations[item.current_station_index]["queue"].append(item)
              else:
                item.state = "completed"
                item.total_time = int(
                    self.simulation_time - item.entry_time
                )
                self.completed_count += 1
                self.total_time_accumulated += item.total_time

      rep_station = self.stations[2]
      while (
          len(rep_station["current_items"]) < self.repair_techs_count
          and rep_station["queue"]
      ):
        next_item = rep_station["queue"].pop(0)
        next_item.state = "processing"
        rep_station["current_items"].append({"item": next_item, "progress": 0.0})

      items_to_finish = []
      for proc in rep_station["current_items"]:
        progress_inc = (minutes_elapsed / rep_station["duration"]) * 100.0
        proc["progress"] += progress_inc
        if proc["progress"] >= 100.0:
          items_to_finish.append(proc)

      for finished in items_to_finish:
        rep_station["current_items"].remove(finished)
        item = finished["item"]
        item.current_station_index = 3
        self.stations[3]["queue"].append(item)

      w = self.canvas.winfo_width()
      h = self.canvas.winfo_height()
      if w > 10 and h > 10:
        for eq in self.equipments:
          target_x, target_y = w * 0.92, h * 0.85
          if eq.state != "completed":
            st_idx = eq.current_station_index
            st = self.stations[st_idx]
            st_x, st_y = w * st["x"], h * st["y"]

            if st_idx == 2:
              in_proc_idx = next(
                  (
                      i
                      for i, p in enumerate(st["current_items"])
                      if p["item"] == eq
                  ),
                  -1,
              )
              if in_proc_idx != -1:
                target_x = st_x + ((in_proc_idx - 1) * 25)
                target_y = st_y - 15
              else:
                try:
                  q_pos = st["queue"].index(eq)
                  target_x = st_x - 45 - (q_pos * 20)
                  target_y = st_y + 40
                except ValueError:
                  target_x, target_y = st_x, st_y
            else:
              if st["current_item"] == eq:
                target_x, target_y = st_x, st_y
              else:
                try:
                  q_pos = st["queue"].index(eq)
                  target_x = st_x - 45 - (q_pos * 20)
                  target_y = st_y + 40
                except ValueError:
                  target_x, target_y = st_x, st_y

          eq.x += (target_x - eq.x) * 0.1
          eq.y += (target_y - eq.y) * 0.1

      self.update_metrics()
      self.draw()

    self.root.after(30, self.run_loop)

  def update_metrics(self):
    in_process = len([e for e in self.equipments if e.state != "completed"])
    avg_time = (
        int(self.total_time_accumulated / self.completed_count)
        if self.completed_count > 0
        else 0
    )

    self.stat_total_lbl.config(text=str(self.equipments_spawned))
    self.stat_process_lbl.config(text=str(in_process))
    self.stat_completed_lbl.config(text=str(self.completed_count))
    self.stat_time_lbl.config(text=f"{avg_time} min")

    total_mins = int(self.simulation_time)
    hours = (total_mins // 60) % 24 + 8
    mins = total_mins % 60
    day = (total_mins // (24 * 60)) + 1
    self.clock_lbl.config(
        text=f"Tiempo: Día {day} - {hours%24:02d}:{mins:02d}"
    )

    t1_busy = (
        self.stations[0]["current_item"] is not None
        or self.stations[4]["current_item"] is not None
    )
    t2_busy = (
        self.stations[1]["current_item"] is not None
        or self.stations[3]["current_item"] is not None
    )
    rep_active = len(self.stations[2]["current_items"])

    self.tech_status_labels[0].config(
        text="Estado: Ocupado" if t1_busy else "Estado: Libre",
        fg="#f59e0b" if t1_busy else "#10b981",
    )
    self.tech_status_labels[1].config(
        text="Estado: Ocupado" if t2_busy else "Estado: Libre",
        fg="#f59e0b" if t2_busy else "#10b981",
    )
    self.tech_status_labels[2].config(
        text=f"Activos: {rep_active}/{self.repair_techs_count} técnicos",
        fg="#38bdf8" if rep_active > 0 else "#10b981",
    )

  def draw(self):
    self.canvas.delete("all")
    w = self.canvas.winfo_width()
    h = self.canvas.winfo_height()
    if w < 10 or h < 10:
      return

    coords = [(w * st["x"], h * st["y"]) for st in self.stations]
    for i in range(len(coords) - 1):
      self.canvas.create_line(
          coords[i][0],
          coords[i][1],
          coords[i + 1][0],
          coords[i + 1][1],
          fill="#0ea5e9",
          width=3,
          dash=(6, 6),
      )

    self.canvas.create_arc(
        w * 0.55,
        15,
        w * 0.75,
        h * 0.35,
        start=0,
        extent=180,
        style=tk.ARC,
        outline="#ef4444",
        width=2,
    )
    self.canvas.create_text(
        w * 0.65,
        25,
        text="Bucle de Retrabajo (20% Fallos)",
        fill="#ef4444",
        font=("Inter", 8, "bold"),  # Corregido de 8.5 a 8
    )

    for idx, st in enumerate(self.stations):
      sx, sy = w * st["x"], h * st["y"]
      r = 38

      if idx == 2:
        is_active = len(st["current_items"]) > 0
      else:
        is_active = st["current_item"] is not None

      fill_color = "#1e293b" if is_active else "#0f172a"
      self.canvas.create_oval(
          sx - r,
          sy - r,
          sx + r,
          sy + r,
          fill=fill_color,
          outline="#38bdf8" if is_active else "#334155",
          width=3,
      )

      if idx == 2:
        self.canvas.create_text(
            sx,
            sy - 12,
            text=st["name"],
            fill="#f8fafc",
            font=("Inter", 9, "bold"),
        )
        self.canvas.create_text(
            sx,
            sy + 4,
            text=f"Técnicos: {len(st['current_items'])}/{self.repair_techs_count}",
            fill="#38bdf8",
            font=("Inter", 8, "bold"),
        )
        self.canvas.create_text(
            sx, sy + 20, text=f"{st['duration']} min", fill="#94a3b8", font=("Inter", 8)
        )
      else:
        self.canvas.create_text(
            sx,
            sy - 10,
            text=st["name"],
            fill="#f8fafc",
            font=("Inter", 9, "bold"),
        )
        self.canvas.create_text(
            sx, sy + 8, text=st["tech"], fill="#94a3b8", font=("Inter", 8)
        )
        self.canvas.create_text(
            sx,
            sy + 22,
            text=f"{st['duration']} min",
            fill="#38bdf8",
            font=("Inter", 8),
        )

    out_x, out_y = w * 0.90, h * 0.85
    self.canvas.create_rectangle(
        out_x - 50,
        out_y - 25,
        out_x + 50,
        out_y + 25,
        fill="#064e3b",
        outline="#10b981",
        width=2,
    )
    self.canvas.create_text(
        out_x,
        out_y - 8,
        text="Salida",
        fill="#10b981",
        font=("Inter", 10, "bold"),
    )
    self.canvas.create_text(
        out_x,
        out_y + 8,
        text=f"Total: {self.completed_count}",
        fill="#cbd5e1",
        font=("Inter", 8),
    )

    for eq in self.equipments:
      color = (
          "#10b981"
          if eq.state == "completed"
          else "#38bdf8"
          if eq.state == "processing"
          else "#f59e0b"
      )
      self.canvas.create_oval(
          eq.x - 12,
          eq.y - 12,
          eq.x + 12,
          eq.y + 12,
          fill=color,
          outline="white",
          width=2,
      )
      self.canvas.create_text(
          eq.x, eq.y, text=str(eq.id), fill="#030712", font=("Inter", 8, "bold")
      )


if __name__ == "__main__":
  root = tk.Tk()
  app = ElectronicsShopSimulator(root)
  root.mainloop()