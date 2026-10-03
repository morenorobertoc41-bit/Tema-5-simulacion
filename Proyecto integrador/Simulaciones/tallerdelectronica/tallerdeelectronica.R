# =====================================================================
# SIMULADOR VISUAL 2D EN TIEMPO REAL - TALLER DE ELECTRÓNICA
# =====================================================================

library(shiny)

ui <- fluidPage(
  tags$head(
    tags$meta(charset = "UTF-8"),
    tags$meta(name = "viewport", content = "width=device-width, initial-scale=1.0"),
    tags$title("Taller de Electrónica 2D - Simulación Oficial"),
    tags$script(src = "https://cdn.tailwindcss.com"),
    tags$link(href = "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap", rel = "stylesheet"),
    tags$link(rel = "stylesheet", href = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"),
    tags$style(HTML("
      body { font-family: 'Inter', sans-serif; background-color: #030712; color: #f8fafc; }
      .glass-panel {
          background: rgba(15, 23, 42, 0.85);
          backdrop-filter: blur(12px);
          border: 1px solid rgba(255, 255, 255, 0.1);
      }
      .canvas-shadow {
          box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
      }
    "))
  ),
  
  HTML('
  <div class="h-full bg-slate-950 text-slate-100 flex flex-col overflow-x-hidden min-h-screen">
    <!-- Header Principal -->
    <header class="glass-panel border-b border-slate-800 px-6 py-4 flex flex-wrap items-center justify-between shadow-lg z-20">
        <div class="flex items-center space-x-3">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
                <i class="fa-solid fa-microchip text-white text-lg"></i>
            </div>
            <div>
                <h1 class="text-xl font-bold tracking-wide bg-gradient-to-r from-cyan-400 to-indigo-300 bg-clip-text text-transparent">Taller de Electrónica 2D</h1>
                <p class="text-xs text-slate-400">Simulación Oficial de Procesos y Asignación de Técnicos</p>
            </div>
        </div>
        <div class="flex items-center space-x-3 mt-2 sm:mt-0">
            <button id="btnPlay" class="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-medium text-sm flex items-center space-x-2 transition shadow-lg shadow-emerald-600/30 active:scale-95">
                <i class="fa-solid fa-play"></i><span>Iniciar Simulación</span>
            </button>
            <button id="btnPause" class="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white rounded-lg font-medium text-sm flex items-center space-x-2 transition shadow-lg shadow-amber-600/30 active:scale-95" disabled>
                <i class="fa-solid fa-pause"></i><span>Pausar</span>
            </button>
            <button id="btnReset" class="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium text-sm flex items-center space-x-2 transition active:scale-95">
                <i class="fa-solid fa-rotate-right"></i><span>Reiniciar</span>
            </button>
            <div class="bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-700 flex items-center space-x-2">
                <span class="text-xs text-slate-400">Velocidad:</span>
                <select id="simSpeed" class="bg-slate-800 text-cyan-400 font-semibold text-xs rounded px-1.5 py-1 focus:outline-none">
                    <option value="1">1x (Real)</option>
                    <option value="5" selected>5x Rápido</option>
                    <option value="15">15x Turbo</option>
                    <option value="30">30x Ultra</option>
                </select>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="flex-1 flex flex-col lg:flex-row p-4 gap-4 max-w-[1920px] mx-auto w-full overflow-y-auto">
        
        <!-- Left Column: Canvas + Metrics -->
        <div class="flex-1 flex flex-col gap-4">
            <div class="glass-panel canvas-shadow rounded-2xl p-4 flex flex-col relative overflow-hidden border border-slate-800 flex-1 min-h-[550px]">
                <div class="flex justify-between items-center mb-3">
                    <div class="flex items-center space-x-2">
                        <span class="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></span>
                        <h2 class="font-semibold text-sm text-slate-200">Plano General del Taller (Estaciones y Técnicos)</h2>
                    </div>
                    <div class="text-xs text-cyan-400 bg-cyan-950/60 px-3 py-1 rounded-full border border-cyan-800/60 font-mono">
                        Tiempo Simulado: <span id="clockDisplay" class="font-bold text-white">Día 1 - 08:00</span>
                    </div>
                </div>
                
                <div class="flex-1 relative w-full h-full bg-slate-900/90 rounded-xl overflow-hidden border border-slate-800 flex items-center justify-center min-h-[420px]">
                    <canvas id="simCanvas" class="w-full h-full block cursor-crosshair"></canvas>
                    <div id="canvasOverlayMsg" class="absolute bottom-4 left-4 bg-slate-900/80 backdrop-blur border border-slate-700 px-4 py-2 rounded-xl text-xs text-slate-300 pointer-events-none shadow-lg">
                        Presiona <strong class="text-cyan-400">Iniciar Simulación</strong> para comenzar el flujo de los 50 equipos.
                    </div>
                </div>
            </div>

            <!-- Bottom Metrics Panel -->
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div class="glass-panel p-3.5 rounded-xl border border-slate-800 flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-lg bg-blue-500/10 border border-blue-500/30 flex items-center justify-center text-blue-400">
                        <i class="fa-solid fa-boxes-stacked text-lg"></i>
                    </div>
                    <div>
                        <p class="text-xs text-slate-400">Equipos Totales</p>
                        <h3 class="text-lg font-bold text-white" id="statTotal">50</h3>
                    </div>
                </div>
                <div class="glass-panel p-3.5 rounded-xl border border-slate-800 flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400">
                        <i class="fa-solid fa-arrows-spin text-lg"></i>
                    </div>
                    <div>
                        <p class="text-xs text-slate-400">En Proceso</p>
                        <h3 class="text-lg font-bold text-white" id="statInProcess">0</h3>
                    </div>
                </div>
                <div class="glass-panel p-3.5 rounded-xl border border-slate-800 flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
                        <i class="fa-solid fa-circle-check text-lg"></i>
                    </div>
                    <div>
                        <p class="text-xs text-slate-400">Completados</p>
                        <h3 class="text-lg font-bold text-white" id="statCompleted">0</h3>
                    </div>
                </div>
                <div class="glass-panel p-3.5 rounded-xl border border-slate-800 flex items-center space-x-3">
                    <div class="w-10 h-10 rounded-lg bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
                        <i class="fa-solid fa-clock-rotate-left text-lg"></i>
                    </div>
                    <div>
                        <p class="text-xs text-slate-400">Tiempo Promedio</p>
                        <h3 class="text-lg font-bold text-white" id="statAvgTime">0 min</h3>
                    </div>
                </div>
            </div>
        </div>

        <!-- Right Column: Technicians & Documentation Parameters -->
        <div class="w-full lg:w-96 flex flex-col gap-4">
            
            <!-- Technicians Status Card -->
            <div class="glass-panel rounded-2xl p-4 border border-slate-800 shadow-xl">
                <h3 class="font-bold text-sm text-slate-200 mb-3 flex items-center space-x-2">
                    <i class="fa-solid fa-users-gear text-cyan-400"></i>
                    <span>Personal Técnico Asignado</span>
                </h3>
                <div class="space-y-3">
                    <div class="bg-slate-900/80 p-3 rounded-xl border border-slate-800 flex flex-col space-y-1">
                        <div class="flex justify-between items-center">
                            <span class="font-semibold text-xs text-cyan-300">Técnico 1 (Recepción y Entrega)</span>
                            <span id="tech1Status" class="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400 font-medium">Libre</span>
                        </div>
                        <p class="text-[11px] text-slate-400">Estaciones: Recepción & Entrega/Facturación</p>
                        <div class="text-[11px] text-slate-300 font-mono mt-1">Carga actual: <span id="tech1Task" class="text-white">Ninguna</span></div>
                    </div>
                    <div class="bg-slate-900/80 p-3 rounded-xl border border-slate-800 flex flex-col space-y-1">
                        <div class="flex justify-between items-center">
                            <span class="font-semibold text-xs text-cyan-300">Técnico 2 (Diagnóstico y Calidad)</span>
                            <span id="tech2Status" class="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400 font-medium">Libre</span>
                        </div>
                        <p class="text-[11px] text-slate-400">Estaciones: Diagnóstico técnico & Pruebas de calidad</p>
                        <div class="text-[11px] text-slate-300 font-mono mt-1">Carga actual: <span id="tech2Task" class="text-white">Ninguna</span></div>
                    </div>
                    <div class="bg-slate-900/80 p-3 rounded-xl border border-slate-800 flex flex-col space-y-1">
                        <div class="flex justify-between items-center">
                            <span class="font-semibold text-xs text-cyan-300">Técnico 3 (Especialista en Reparación)</span>
                            <span id="tech3Status" class="px-2 py-0.5 rounded text-[10px] bg-slate-800 text-slate-400 font-medium">Libre</span>
                        </div>
                        <p class="text-[11px] text-slate-400">Estación: Reparación y mantenimiento + Retrabajo</p>
                        <div class="text-[11px] text-slate-300 font-mono mt-1">Carga actual: <span id="tech3Task" class="text-white">Ninguna</span></div>
                    </div>
                </div>
            </div>

            <!-- Documentation Parameters Card -->
            <div class="glass-panel rounded-2xl p-4 border border-slate-800 shadow-xl flex-1 flex flex-col">
                <h3 class="font-bold text-sm text-slate-200 mb-3 flex items-center space-x-2">
                    <i class="fa-solid fa-file-lines text-indigo-400"></i>
                    <span>Parámetros de Documentación</span>
                </h3>
                <div class="space-y-2.5 text-xs text-slate-300 overflow-y-auto pr-1 max-h-[340px]">
                    <div class="p-2.5 bg-slate-900/60 rounded-xl border border-slate-800/80">
                        <strong class="text-cyan-400 block mb-0.5"><i class="fa-solid fa-truck-ramp-box mr-1.5"></i>1. Llegada de equipos</strong>
                        <span>50 equipos totales. Tiempo promedio de llegada de <strong>15 minutos</strong> entre cada uno.</span>
                    </div>
                    <div class="p-2.5 bg-slate-900/60 rounded-xl border border-slate-800/80">
                        <strong class="text-cyan-400 block mb-0.5"><i class="fa-solid fa-stopwatch mr-1.5"></i>2. Duración de etapas</strong>
                        <ul class="space-y-1 mt-1 text-[11px] text-slate-400">
                            <li>• Recepción: <strong>5 min</strong> promedio</li>
                            <li>• Diagnóstico técnico: <strong>15 min</strong> promedio</li>
                            <li>• Reparación y mantenimiento: <strong>45 min</strong> promedio</li>
                            <li>• Pruebas de calidad: <strong>10 min</strong> promedio</li>
                            <li>• Entrega y facturación: <strong>5 min</strong> promedio</li>
                        </ul>
                    </div>
                    <div class="p-2.5 bg-slate-900/60 rounded-xl border border-slate-800/80">
                        <strong class="text-cyan-400 block mb-0.5"><i class="fa-solid fa-rotate-left mr-1.5"></i>3. Bucle de Retrabajo</strong>
                        <span>Si falla la prueba de calidad (20% prob.), el equipo regresa a la estación de Reparación con el Técnico 3.</span>
                    </div>
                </div>
            </div>
        </div>
    </main>
  </div>
  
  <!-- JavaScript Simulation Engine -->
  <script>
    const canvas = document.getElementById(\'simCanvas\');
    const ctx = canvas.getContext(\'2d\');

    let isRunning = false;
    let animationFrameId = null;
    let simSpeed = 5;
    let simulationTime = 480; 
    let totalEquipmentsTarget = 50;
    let equipmentsSpawned = 0;
    let nextSpawnIn = 0;

    const stations = [
        { id: \'recepcion\', name: \'1. Recepción\', x: 0.12, y: 0.35, duration: 5, tech: \'Técnico 1\', queue: [], currentItem: null, progress: 0 },
        { id: \'diagnostico\', name: \'2. Diagnóstico\', x: 0.32, y: 0.35, duration: 15, tech: \'Técnico 2\', queue: [], currentItem: null, progress: 0 },
        { id: \'reparacion\', name: \'3. Reparación\', x: 0.55, y: 0.35, duration: 45, tech: \'Técnico 3\', queue: [], currentItem: null, progress: 0 },
        { id: \'calidad\', name: \'4. Pruebas de Calidad\', x: 0.75, y: 0.35, duration: 10, tech: \'Técnico 2\', queue: [], currentItem: null, progress: 0 },
        { id: \'entrega\', name: \'5. Entrega y Fact.\', x: 0.90, y: 0.65, duration: 5, tech: \'Técnico 1\', queue: [], currentItem: null, progress: 0 }
    ];

    let equipments = [];
    let completedCount = 0;
    let totalTimeAccumulated = 0;

    class Equipment {
        constructor(id) {
            this.id = id;
            this.name = `EQ-${String(id).padStart(2, \'0\')}`;
            this.currentStationIndex = 0;
            this.state = \'waiting_queue\';
            this.x = 50;
            this.y = 200;
            this.targetX = 50;
            this.targetY = 200;
            this.entryTime = simulationTime;
            this.totalTimeInSystem = 0;
            this.hasRetried = false;
        }
    }

    function resizeCanvas() {
        if (!canvas || !canvas.parentElement) return;
        const rect = canvas.parentElement.getBoundingClientRect();
        canvas.width = rect.width || 800;
        canvas.height = rect.height || 450;
    }

    window.addEventListener(\'resize\', resizeCanvas);
    setTimeout(resizeCanvas, 100);

    document.getElementById(\'simSpeed\').addEventListener(\'change\', (e) => {
        simSpeed = parseInt(e.target.value);
    });

    document.getElementById(\'btnPlay\').addEventListener(\'click\', () => {
        if (!isRunning) {
            isRunning = true;
            document.getElementById(\'btnPlay\').disabled = true;
            document.getElementById(\'btnPause\').disabled = false;
            document.getElementById(\'canvasOverlayMsg\').style.display = \'none\';
        }
    });

    document.getElementById(\'btnPause\').addEventListener(\'click\', () => {
        isRunning = false;
        document.getElementById(\'btnPlay\').disabled = false;
        document.getElementById(\'btnPause\').disabled = true;
    });

    document.getElementById(\'btnReset\').addEventListener(\'click\', () => {
        isRunning = false;
        simulationTime = 480;
        equipmentsSpawned = 0;
        nextSpawnIn = 0;
        equipments = [];
        completedCount = 0;
        totalTimeAccumulated = 0;
        stations.forEach(s => { s.queue = []; s.currentItem = null; s.progress = 0; });
        document.getElementById(\'btnPlay\').disabled = false;
        document.getElementById(\'btnPause\').disabled = true;
        document.getElementById(\'canvasOverlayMsg\').style.display = \'block\';
        updateMetrics();
        draw();
    });

    function getStationCoords(stationIndex) {
        if (stationIndex >= stations.length) {
            return { x: canvas.width * 0.90, y: canvas.height * 0.85 };
        }
        const st = stations[stationIndex];
        return { x: canvas.width * st.x, y: canvas.height * st.y };
    }

    function getNextArrivalInterval() {
        return 8 + Math.random() * 14;
    }

    function updateSimulation(deltaTime) {
        const minutesElapsed = (deltaTime / 1000) * (simSpeed * 2); 
        simulationTime += minutesElapsed;

        if (equipmentsSpawned < totalEquipmentsTarget) {
            nextSpawnIn -= minutesElapsed;
            if (nextSpawnIn <= 0) {
                equipmentsSpawned++;
                const eq = new Equipment(equipmentsSpawned);
                eq.x = canvas.width * 0.08;
                eq.y = canvas.height * 0.75;
                stations[0].queue.push(eq);
                equipments.push(eq);
                nextSpawnIn = getNextArrivalInterval();
            }
        }

        stations.forEach((station, index) => {
            if (!station.currentItem && station.queue.length > 0) {
                station.currentItem = station.queue.shift();
                station.currentItem.state = \'processing\';
                station.progress = 0;
            }

            if (station.currentItem) {
                const durationMinutes = station.duration;
                const progressIncrement = (minutesElapsed / durationMinutes) * 100;
                station.progress += progressIncrement;

                if (station.progress >= 100) {
                    const finishedItem = station.currentItem;
                    station.currentItem = null;
                    station.progress = 0;

                    if (index === 2) {
                        finishedItem.currentStationIndex = 3;
                        stations[3].queue.push(finishedItem);
                    } else if (index === 3) {
                        if (!finishedItem.hasRetried && Math.random() < 0.20) {
                            finishedItem.hasRetried = true;
                            finishedItem.currentStationIndex = 2;
                            stations[2].queue.push(finishedItem);
                        } else {
                            finishedItem.currentStationIndex = 4;
                            stations[4].queue.push(finishedItem);
                        }
                    } else {
                        finishedItem.currentStationIndex++;
                        if (finishedItem.currentStationIndex < stations.length) {
                            stations[finishedItem.currentStationIndex].queue.push(finishedItem);
                        } else {
                            finishedItem.state = \'completed\';
                            finishedItem.totalTimeInSystem = Math.round(simulationTime - finishedItem.entryTime);
                            completedCount++;
                            totalTimeAccumulated += finishedItem.totalTimeInSystem;
                        }
                    }
                }
            }
        });

        equipments.forEach(eq => {
            let targetPos = { x: 0, y: 0 };
            if (eq.state === \'completed\') {
                targetPos = { x: canvas.width * 0.92, y: canvas.height * 0.85 };
            } else {
                const stIdx = eq.currentStationIndex;
                const stCoords = getStationCoords(stIdx);
                if (stations[stIdx].currentItem === eq) {
                    targetPos = stCoords;
                } else {
                    const queuePos = stations[stIdx].queue.indexOf(eq);
                    if (queuePos !== -1) {
                        targetPos = {
                            x: stCoords.x - 45 - (queuePos * 22),
                            y: stCoords.y + 40
                        };
                    } else {
                        targetPos = stCoords;
                    }
                }
            }
            eq.x += (targetPos.x - eq.x) * 0.1;
            eq.y += (targetPos.y - eq.y) * 0.1;
        });

        updateMetrics();
    }

    function updateMetrics() {
        const inProcess = equipments.filter(e => e.state !== \'completed\').length;
        const avgTime = completedCount > 0 ? Math.round(totalTimeAccumulated / completedCount) : 0;

        document.getElementById(\'statTotal\').innerText = equipmentsSpawned;
        document.getElementById(\'statInProcess\').innerText = inProcess;
        document.getElementById(\'statCompleted\').innerText = completedCount;
        document.getElementById(\'statAvgTime\').innerText = avgTime + \' min\';

        const totalMins = Math.floor(simulationTime);
        const hours = Math.floor(totalMins / 60) % 24 + 8;
        const mins = totalMins % 60;
        const day = Math.floor(totalMins / (24 * 60)) + 1;
        document.getElementById(\'clockDisplay\').innerText = \'Día \' + day + \' - \' + String(hours % 24).padStart(2, \'0\') + \':\' + String(mins).padStart(2, \'0\');

        document.getElementById(\'tech1Status\').innerText = (stations[0].currentItem || stations[4].currentItem) ? \'Ocupado\' : \'Libre\';
        document.getElementById(\'tech1Status\').className = \'px-2 py-0.5 rounded text-[10px] font-medium \' + ((stations[0].currentItem || stations[4].currentItem) ? \'bg-amber-500/20 text-amber-400 border border-amber-500/30\' : \'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30\');
        document.getElementById(\'tech1Task\').innerText = stations[0].currentItem ? \'Atendiendo Recepción\' : (stations[4].currentItem ? \'Atendiendo Entrega\' : \'Ninguna\');

        document.getElementById(\'tech2Status\').innerText = (stations[1].currentItem || stations[3].currentItem) ? \'Ocupado\' : \'Libre\';
        document.getElementById(\'tech2Status\').className = \'px-2 py-0.5 rounded text-[10px] font-medium \' + ((stations[1].currentItem || stations[3].currentItem) ? \'bg-amber-500/20 text-amber-400 border border-amber-500/30\' : \'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30\');
        document.getElementById(\'tech2Task\').innerText = stations[1].currentItem ? \'Diagnóstico técnico\' : (stations[3].currentItem ? \'Pruebas de calidad\' : \'Ninguna\');

        document.getElementById(\'tech3Status\').innerText = stations[2].currentItem ? \'Ocupado\' : \'Libre\';
        document.getElementById(\'tech3Status\').className = \'px-2 py-0.5 rounded text-[10px] font-medium \' + (stations[2].currentItem ? \'bg-amber-500/20 text-amber-400 border border-amber-500/30\' : \'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30\');
        document.getElementById(\'tech3Task\').innerText = stations[2].currentItem ? \'Reparación / Mantenimiento\' : \'Ninguna\';
    }

    function draw() {
        if (!canvas || !ctx) return;
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        ctx.strokeStyle = \'rgba(51, 65, 85, 0.2)\';
        ctx.lineWidth = 1;
        const gridSize = 40;
        for (let x = 0; x < canvas.width; x += gridSize) {
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, canvas.height); ctx.stroke();
        }
        for (let y = 0; y < canvas.height; y += gridSize) {
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
        }

        ctx.strokeStyle = \'rgba(14, 165, 233, 0.3)\';
        ctx.lineWidth = 3;
        ctx.setLineDash([6, 6]);
        ctx.beginPath();
        ctx.moveTo(canvas.width * 0.12, canvas.height * 0.35);
        ctx.lineTo(canvas.width * 0.32, canvas.height * 0.35);
        ctx.lineTo(canvas.width * 0.55, canvas.height * 0.35);
        ctx.lineTo(canvas.width * 0.75, canvas.height * 0.35);
        ctx.lineTo(canvas.width * 0.85, canvas.height * 0.35);
        ctx.lineTo(canvas.width * 0.85, canvas.height * 0.65);
        ctx.lineTo(canvas.width * 0.90, canvas.height * 0.65);
        ctx.stroke();
        ctx.setLineDash([]); 

        ctx.strokeStyle = \'rgba(239, 68, 68, 0.6)\';
        ctx.lineWidth = 2;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(canvas.width * 0.75, canvas.height * 0.22);
        ctx.quadraticCurveTo(canvas.width * 0.65, 10, canvas.width * 0.55, canvas.height * 0.22);
        ctx.stroke();
        ctx.setLineDash([]);

        ctx.fillStyle = \'rgba(239, 68, 68, 0.8)\';
        ctx.font = \'10px Inter, sans-serif\';
        ctx.textAlign = \'center\';
        ctx.fillText(\'Bucle de Retrabajo (20% Fallos)\', canvas.width * 0.65, 25);

        stations.forEach((st, idx) => {
            const pos = getStationCoords(idx);
            const radius = 42;

            ctx.beginPath();
            ctx.arc(pos.x, pos.y, radius, 0, Math.PI * 2);
            ctx.fillStyle = st.currentItem ? \'rgba(30, 41, 59, 0.95)\' : \'rgba(15, 23, 42, 0.85)\';
            ctx.fill();
            ctx.strokeStyle = st.currentItem ? \'#38bdf8\' : \'#334155\';
            ctx.lineWidth = 3;
            ctx.stroke();

            if (st.currentItem) {
                ctx.beginPath();
                ctx.arc(pos.x, pos.y, radius + 4, -Math.PI / 2, (-Math.PI / 2) + (Math.PI * 2 * (st.progress / 100)));
                ctx.strokeStyle = \'#10b981\';
                ctx.lineWidth = 3;
                ctx.stroke();
            }

            ctx.fillStyle = \'#f8fafc\';
            ctx.font = \'bold 11px Inter, sans-serif\';
            ctx.textAlign = \'center\';
            ctx.fillText(st.name, pos.x, pos.y - 12);

            ctx.fillStyle = \'#94a3b8\';
            ctx.font = \'10px Inter, sans-serif\';
            ctx.fillText(st.tech, pos.x, pos.y + 4);

            ctx.fillStyle = \'#38bdf8\';
            ctx.font = \'9px Inter, sans-serif\';
            ctx.fillText(st.duration + \' min\', pos.x, pos.y + 18);
        });

        const outPos = { x: canvas.width * 0.90, y: canvas.height * 0.85 };
        ctx.beginPath();
        ctx.fillStyle = \'rgba(16, 185, 129, 0.15)\';
        ctx.fillRect(outPos.x - 55, outPos.y - 25, 110, 50);
        ctx.strokeStyle = \'#10b981\';
        ctx.lineWidth = 2;
        ctx.strokeRect(outPos.x - 55, outPos.y - 25, 110, 50);

        ctx.fillStyle = \'#10b981\';
        ctx.font = \'bold 11px Inter, sans-serif\';
        ctx.textAlign = \'center\';
        ctx.fillText(\'Área de Salida\', outPos.x, outPos.y - 5);
        ctx.fillStyle = \'#cbd5e1\';
        ctx.font = \'10px Inter, sans-serif\';
        ctx.fillText(\'Completados: \' + completedCount, outPos.x, outPos.y + 10);

        equipments.forEach(eq => {
            ctx.beginPath();
            ctx.arc(eq.x, eq.y, 14, 0, Math.PI * 2);
            if (eq.state === \'completed\') {
                ctx.fillStyle = \'#10b981\';
            } else if (eq.state === \'processing\') {
                ctx.fillStyle = \'#38bdf8\';
            } else {
                ctx.fillStyle = \'#f59e0b\';
            }
            ctx.fill();
            ctx.strokeStyle = \'#ffffff\';
            ctx.lineWidth = 2;
            ctx.stroke();

            ctx.fillStyle = \'#0f172a\';
            ctx.font = \'bold 9px Inter, sans-serif\';
            ctx.textAlign = \'center\';
            ctx.textBaseline = \'middle\';
            ctx.fillText(eq.id, eq.x, eq.y);
            ctx.textBaseline = \'alphabetic\';
        });
    }

    let lastTime = performance.now();
    function mainLoop(timestamp) {
        const deltaTime = timestamp - lastTime;
        lastTime = timestamp;

        if (isRunning) {
            updateSimulation(deltaTime);
        }
        draw();
        animationFrameId = requestAnimationFrame(mainLoop);
    }

    animationFrameId = requestAnimationFrame(mainLoop);
  </script>
  ')
)

server <- function(input, output, session) {}

shinyApp(ui, server)