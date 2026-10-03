package com.carlossystems.simulador.tallerdeelectronicamejorado;

import javafx.animation.AnimationTimer;
import javafx.application.Application;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.canvas.Canvas;
import javafx.scene.canvas.GraphicsContext;
import javafx.scene.control.*;
import javafx.scene.layout.*;
import javafx.scene.paint.Color;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;
import javafx.stage.Stage;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

public class Taller extends Application {

    private boolean isRunning = false;
    private double simSpeed = 5.0;
    private double simulationTime = 480;
    private int totalEquipmentsTarget = 50;
    private int equipmentsSpawned = 0;
    private double nextSpawnIn = 0;
    private int completedCount = 0;
    private double totalTimeAccumulated = 0;

    // Control de técnicos en la estación de reparación (Índice 2)
    private int repairTechsCount = 1;

    private Label clockLbl;
    private Label statTotalLbl, statProcessLbl, statCompletedLbl, statAvgLbl;
    private Button btnPlay, btnPause, btnReset, btnTechsChange;
    private ComboBox<String> speedCombo;
    private StackPane canvasContainer;
    private Label overlayMsg;

    private final List<Station> stations = new ArrayList<>();
    private final List<Equipment> equipments = new ArrayList<>();
    private final List<TechInfo> techs = new ArrayList<>();

    public static class Station {
        String id, name, tech, subtext;
        double x, y;
        double duration;
        int capacity; // Capacidad simultánea de técnicos
        List<Equipment> queue = new ArrayList<>();
        List<Equipment> currentItems = new ArrayList<>(); // Soporta múltiples elementos procesándose en paralelo
        List<Double> progressList = new ArrayList<>();

        public Station(String id, String name, double x, double y, double duration, int capacity, String tech, String subtext) {
            this.id = id; this.name = name; this.x = x; this.y = y; this.duration = duration; this.capacity = capacity; this.tech = tech; this.subtext = subtext;
        }
    }

    public static class Equipment {
        int id;
        String name;
        int currentStationIndex = 0;
        String state = "waiting_queue";
        double x, y;
        double entryTime;
        boolean hasRetried = false;

        public Equipment(int id, double entryTime) {
            this.id = id;
            this.name = String.format("EQ-%02d", id);
            this.entryTime = entryTime;
            this.x = 50; this.y = 200;
        }
    }

    public static class TechInfo {
        String name, role, details;
        Label statusLbl, taskLbl;
        public TechInfo(String name, String role, String details) {
            this.name = name; this.role = role; this.details = details;
        }
    }

    @Override
    public void start(Stage stage) {
        stations.add(new Station("recepcion", "1. Recepción", 0.12, 0.35, 5, 1, "Técnico 1", "5 min"));
        stations.add(new Station("diagnostico", "2. Diagnóstico", 0.32, 0.35, 15, 1, "Técnico 2", "15 min"));
        stations.add(new Station("reparacion", "3. Reparación", 0.55, 0.35, 45, repairTechsCount, "Técnico 3", "45 min"));
        stations.add(new Station("calidad", "4. Pruebas de Calidad", 0.75, 0.35, 10, 1, "Técnico 2", "10 min"));
        stations.add(new Station("entrega", "5. Entrega y Fact.", 0.75, 0.68, 5, 1, "Técnico 1", "5 min"));

        techs.add(new TechInfo("Técnico 1", "Recepción & Entrega/Facturación", "Recepción & Entrega/Facturación"));
        techs.add(new TechInfo("Técnico 2", "Diagnóstico & Pruebas de calidad", "Diagnóstico & Pruebas de calidad"));
        techs.add(new TechInfo("Técnico 3", "Reparación y mantenimiento + Retrabajo", "Reparación y mantenimiento + Retrabajo"));

        BorderPane root = new BorderPane();
        root.setStyle("-fx-background-color: #030712;");

        // --- HEADER ---
        HBox header = new HBox(12);
        header.setPadding(new Insets(10, 15, 10, 15));
        header.setStyle("-fx-background-color: #0f172a; -fx-alignment: center-left; -fx-border-color: #1e293b;");

        Label titleLbl = new Label("Taller de Electrónica 2D");
        titleLbl.setFont(Font.font("Inter", FontWeight.BOLD, 14));
        titleLbl.setTextFill(Color.web("#38bdf8"));

        btnTechsChange = new Button("🔧 Técnicos Reparación: " + repairTechsCount);
        btnTechsChange.setStyle("-fx-background-color: #0284c7; -fx-text-fill: white; -fx-font-weight: bold; -fx-cursor: hand;");
        btnTechsChange.setOnAction(e -> {
            repairTechsCount = (repairTechsCount % 3) + 1; // Rota entre 1, 2 y 3
            btnTechsChange.setText("🔧 Técnicos Reparación: " + repairTechsCount);
            stations.get(2).capacity = repairTechsCount;
        });

        Region spacer = new Region();
        HBox.setHgrow(spacer, Priority.ALWAYS);

        btnPlay = new Button("▶ Iniciar");
        btnPlay.setStyle("-fx-background-color: #059669; -fx-text-fill: white; -fx-font-weight: bold; -fx-cursor: hand;");
        btnPlay.setOnAction(e -> startSim());

        btnPause = new Button("⏸ Pausar");
        btnPause.setStyle("-fx-background-color: #d97706; -fx-text-fill: white; -fx-font-weight: bold; -fx-cursor: hand;");
        btnPause.setDisable(true);
        btnPause.setOnAction(e -> pauseSim());

        btnReset = new Button("🔄 Reiniciar");
        btnReset.setStyle("-fx-background-color: #475569; -fx-text-fill: white; -fx-font-weight: bold; -fx-cursor: hand;");
        btnReset.setOnAction(e -> resetSim());

        Label speedLbl = new Label("Vel:");
        speedLbl.setTextFill(Color.web("#94a3b8"));

        speedCombo = new ComboBox<>();
        speedCombo.getItems().addAll("1x Normal", "2x Rápido", "5x Rápido", "10x Muy Rápido");
        speedCombo.setValue("5x Rápido");
        speedCombo.setStyle("-fx-background-color: #1e293b; -fx-text-fill: white;");
        speedCombo.setOnAction(e -> {
            String val = speedCombo.getValue();
            if (val.startsWith("1x")) simSpeed = 1.0;
            else if (val.startsWith("2x")) simSpeed = 2.0;
            else if (val.startsWith("5x")) simSpeed = 5.0;
            else if (val.startsWith("10x")) simSpeed = 10.0;
        });

        header.getChildren().addAll(titleLbl, btnTechsChange, spacer, btnPlay, btnPause, btnReset, speedLbl, speedCombo);
        root.setTop(header);

        // --- CENTER PANE ---
        BorderPane centerPane = new BorderPane();
        centerPane.setPadding(new Insets(10));

        VBox leftCol = new VBox(10);
        VBox.setVgrow(leftCol, Priority.ALWAYS);

        // Canvas Card
        VBox canvasCard = new VBox();
        canvasCard.setStyle("-fx-background-color: #0f172a; -fx-border-color: #1e293b;");
        VBox.setVgrow(canvasCard, Priority.ALWAYS);

        HBox canvasTopBar = new HBox();
        canvasTopBar.setPadding(new Insets(10));
        Label canvasTitle = new Label("Plano General del Taller (Estaciones y Técnicos)");
        canvasTitle.setTextFill(Color.web("#f8fafc"));
        canvasTitle.setFont(Font.font("Inter", FontWeight.BOLD, 12));

        Region spacer2 = new Region();
        HBox.setHgrow(spacer2, Priority.ALWAYS);

        clockLbl = new Label("Día 1 - 08:00");
        clockLbl.setStyle("-fx-background-color: #082f49; -fx-text-fill: #38bdf8; -fx-padding: 5 10; -fx-background-radius: 4;");
        canvasTopBar.getChildren().addAll(canvasTitle, spacer2, clockLbl);

        canvasContainer = new StackPane();
        VBox.setVgrow(canvasContainer, Priority.ALWAYS);

        Canvas canvas = new Canvas(850, 450);
        canvas.widthProperty().bind(canvasContainer.widthProperty());
        canvas.heightProperty().bind(canvasContainer.heightProperty());

        overlayMsg = new Label("Presiona Iniciar para comenzar el flujo de los 50 equipos.");
        overlayMsg.setStyle("-fx-background-color: #0f172a; -fx-text-fill: #94a3b8; -fx-padding: 8 12; -fx-border-color: #1e293b;");
        StackPane.setAlignment(overlayMsg, Pos.BOTTOM_LEFT);
        StackPane.setMargin(overlayMsg, new Insets(15));

        canvasContainer.getChildren().addAll(canvas, overlayMsg);
        canvasCard.getChildren().addAll(canvasTopBar, canvasContainer);

        // Metrics Grid at bottom-left
        GridPane metricsGrid = new GridPane();
        metricsGrid.setHgap(10);
        statTotalLbl = createMetricCard(metricsGrid, "Equipos Totales", "0", 0);
        statProcessLbl = createMetricCard(metricsGrid, "En Proceso", "0", 1);
        statCompletedLbl = createMetricCard(metricsGrid, "Completados", "0", 2);
        statAvgLbl = createMetricCard(metricsGrid, "Tiempo Promedio", "0 min", 3);

        leftCol.getChildren().addAll(canvasCard, metricsGrid);
        centerPane.setCenter(leftCol);

        // --- RIGHT SIDEBAR ---
        VBox rightCol = new VBox(10);
        rightCol.setPrefWidth(320);
        rightCol.setPadding(new Insets(0, 0, 0, 10));

        // Techs Card
        VBox techCard = new VBox(8);
        techCard.setPadding(new Insets(12));
        techCard.setStyle("-fx-background-color: #0f172a; -fx-border-color: #1e293b;");
        Label techTitle = new Label("Personal Técnico Asignado");
        techTitle.setTextFill(Color.web("#38bdf8"));
        techTitle.setFont(Font.font("Inter", FontWeight.BOLD, 12));
        techCard.getChildren().add(techTitle);

        for (TechInfo t : techs) {
            VBox box = new VBox(3);
            box.setPadding(new Insets(8));
            box.setStyle("-fx-background-color: #1e293b; -fx-background-radius: 4;");

            HBox topBox = new HBox();
            Label nameLbl = new Label(t.name);
            nameLbl.setTextFill(Color.web("#38bdf8"));
            nameLbl.setFont(Font.font("Inter", FontWeight.BOLD, 11));

            Region r = new Region();
            HBox.setHgrow(r, Priority.ALWAYS);

            t.statusLbl = new Label("Libre");
            t.statusLbl.setTextFill(Color.web("#10b981"));
            t.statusLbl.setStyle("-fx-font-size: 10px; -fx-font-weight: bold;");
            topBox.getChildren().addAll(nameLbl, r, t.statusLbl);

            Label roleLbl = new Label(t.role);
            roleLbl.setTextFill(Color.web("#94a3b8"));
            roleLbl.setStyle("-fx-font-size: 10px;");

            t.taskLbl = new Label("Carga actual: Ninguna");
            t.taskLbl.setTextFill(Color.web("#f8fafc"));
            t.taskLbl.setStyle("-fx-font-size: 10px; -fx-font-style: italic;");

            box.getChildren().addAll(topBox, roleLbl, t.taskLbl);
            techCard.getChildren().add(box);
        }

        // Parameters Card
        VBox paramCard = new VBox(6);
        paramCard.setPadding(new Insets(12));
        paramCard.setStyle("-fx-background-color: #0f172a; -fx-border-color: #1e293b;");
        Label paramTitle = new Label("Parámetros de la Simulación");
        paramTitle.setTextFill(Color.web("#c084fc"));
        paramTitle.setFont(Font.font("Inter", FontWeight.BOLD, 12));

        Label paramContent = new Label(
                "• 50 equipos totales.\n" +
                        "• Llegada: ~15 min promedio.\n" +
                        "• Recepción: 5 min\n" +
                        "• Diagnóstico: 15 min\n" +
                        "• Reparación: 45 min (Multitécnico)\n" +
                        "• Calidad: 10 min (20% retrabajo)\n" +
                        "• Entrega: 5 min"
        );
        paramContent.setTextFill(Color.web("#94a3b8"));
        paramContent.setStyle("-fx-font-size: 11px;");
        paramCard.getChildren().addAll(paramTitle, paramContent);

        rightCol.getChildren().addAll(techCard, paramCard);
        centerPane.setRight(rightCol);
        root.setCenter(centerPane);

        // --- ANIMATION TIMER ---
        GraphicsContext gc = canvas.getGraphicsContext2D();
        final long[] lastTime = {System.nanoTime()};

        AnimationTimer timer = new AnimationTimer() {
            @Override
            public void handle(long now) {
                double deltaTime = (now - lastTime[0]) / 1_000_000.0;
                lastTime[0] = now;

                if (isRunning) updateSimulation(deltaTime);
                drawCanvas(gc, canvas.getWidth(), canvas.getHeight());
                updateTechsAndMetricsUI();
            }
        };
        timer.start();

        Scene scene = new Scene(root, 1280, 720);
        stage.setTitle("Taller de Electrónica 2D - Simulación");
        stage.setScene(scene);
        stage.show();
    }

    private Label createMetricCard(GridPane parent, String title, String initialVal, int col) {
        VBox card = new VBox(3);
        card.setPadding(new Insets(10));
        card.setStyle("-fx-background-color: #0f172a; -fx-border-color: #1e293b;");
        GridPane.setHgrow(card, Priority.ALWAYS);
        parent.add(card, col, 0);

        Label tLbl = new Label(title);
        tLbl.setTextFill(Color.web("#94a3b8"));
        tLbl.setStyle("-fx-font-size: 11px;");
        Label vLbl = new Label(initialVal);
        vLbl.setTextFill(Color.web("#f8fafc"));
        vLbl.setFont(Font.font("Inter", FontWeight.BOLD, 14));

        card.getChildren().addAll(tLbl, vLbl);
        return vLbl;
    }

    private void startSim() { isRunning = true; btnPlay.setDisable(true); btnPause.setDisable(false); overlayMsg.setVisible(false); }
    private void pauseSim() { isRunning = false; btnPlay.setDisable(false); btnPause.setDisable(true); }
    private void resetSim() {
        isRunning = false; simulationTime = 480; equipmentsSpawned = 0; nextSpawnIn = 0;
        equipments.clear(); completedCount = 0; totalTimeAccumulated = 0;
        for (Station s : stations) { s.queue.clear(); s.currentItems.clear(); s.progressList.clear(); }
        btnPlay.setDisable(false); btnPause.setDisable(true); overlayMsg.setVisible(true);
    }

    private void updateSimulation(double deltaTime) {
        double minutesElapsed = (deltaTime / 1000.0) * (simSpeed * 2);
        simulationTime += minutesElapsed;

        if (equipmentsSpawned < totalEquipmentsTarget) {
            nextSpawnIn -= minutesElapsed;
            if (nextSpawnIn <= 0) {
                equipmentsSpawned++;
                Equipment eq = new Equipment(equipmentsSpawned, simulationTime);
                stations.get(0).queue.add(eq);
                equipments.add(eq);
                nextSpawnIn = 10 + new Random().nextDouble() * 10;
            }
        }

        for (int index = 0; index < stations.size(); index++) {
            Station station = stations.get(index);

            // Asignar elementos de la cola si hay capacidad libre en la estación
            while (station.currentItems.size() < station.capacity && !station.queue.isEmpty()) {
                Equipment nextEq = station.queue.remove(0);
                nextEq.state = "processing";
                station.currentItems.add(nextEq);
                station.progressList.add(0.0);
            }

            // Procesar los elementos actuales en paralelo
            for (int i = 0; i < station.currentItems.size(); i++) {
                double currentProg = station.progressList.get(i);
                currentProg += (minutesElapsed / station.duration) * 100.0;
                station.progressList.set(i, currentProg);

                if (currentProg >= 100) {
                    Equipment finishedItem = station.currentItems.remove(i);
                    station.progressList.remove(i);
                    i--;

                    if (index == 2) { // Reparación -> Calidad
                        finishedItem.currentStationIndex = 3;
                        stations.get(3).queue.add(finishedItem);
                    } else if (index == 3) { // Calidad -> Retrabajo (20%) o Entrega
                        if (!finishedItem.hasRetried && new Random().nextDouble() < 0.20) {
                            finishedItem.hasRetried = true;
                            finishedItem.currentStationIndex = 2; // Reparación
                            stations.get(2).queue.add(finishedItem);
                        } else {
                            finishedItem.currentStationIndex = 4; // Entrega
                            stations.get(4).queue.add(finishedItem);
                        }
                    } else {
                        finishedItem.currentStationIndex++;
                        if (finishedItem.currentStationIndex < stations.size()) {
                            stations.get(finishedItem.currentStationIndex).queue.add(finishedItem);
                        } else {
                            finishedItem.state = "completed";
                            completedCount++;
                            totalTimeAccumulated += (simulationTime - finishedItem.entryTime);
                        }
                    }
                }
            }
        }

        for (Equipment eq : equipments) {
            double targetX, targetY;
            double cWidth = canvasContainer.getWidth() > 0 ? canvasContainer.getWidth() : 850;
            double cHeight = canvasContainer.getHeight() > 0 ? canvasContainer.getHeight() : 450;

            if (eq.state.equals("completed")) {
                targetX = cWidth * 0.75; targetY = cHeight * 0.88;
            } else {
                Station st = stations.get(eq.currentStationIndex);
                double stX = cWidth * st.x; double stY = cHeight * st.y;

                int activeIndex = st.currentItems.indexOf(eq);
                if (activeIndex != -1) {
                    // Si hay varios técnicos, distribuimos las bolitas dentro del círculo de la estación
                    if (st.capacity > 1) {
                        double offsetX = (activeIndex - (st.capacity - 1) / 2.0) * 22;
                        targetX = stX + offsetX; targetY = stY - 10;
                    } else {
                        targetX = stX; targetY = stY;
                    }
                } else {
                    int qPos = st.queue.indexOf(eq);
                    if (qPos == -1) qPos = st.queue.size();

                    if (eq.currentStationIndex == 0) {
                        // Cola de recepción apilada en filas hacia abajo si excede espacio
                        int col = qPos % 10;
                        int row = qPos / 10;
                        targetX = stX - 50 - (col * 22);
                        targetY = stY + 25 + (row * 22);
                    } else {
                        targetX = stX - 50 - (qPos * 20);
                        targetY = stY + 45;
                    }
                }
            }
            eq.x += (targetX - eq.x) * 0.15;
            eq.y += (targetY - eq.y) * 0.15;
        }
    }

    private void drawCanvas(GraphicsContext gc, double width, double height) {
        if (width <= 0 || height <= 0) return;

        gc.setFill(Color.web("#070b14"));
        gc.fillRect(0, 0, width, height);

        gc.setStroke(Color.web("#111827"));
        gc.setLineWidth(1);
        for (double x = 0; x < width; x += 30) gc.strokeLine(x, 0, x, height);
        for (double y = 0; y < height; y += 30) gc.strokeLine(0, y, width, y);

        // Líneas punteadas de conexión
        gc.setStroke(Color.web("#38bdf8"));
        gc.setLineWidth(2.5);
        gc.setLineDashes(6, 6);

        double x1 = width * stations.get(0).x, y1 = height * stations.get(0).y;
        double x2 = width * stations.get(1).x, y2 = height * stations.get(1).y;
        double x3 = width * stations.get(2).x, y3 = height * stations.get(2).y;
        double x4 = width * stations.get(3).x, y4 = height * stations.get(3).y;
        double x5 = width * stations.get(4).x, y5 = height * stations.get(4).y;

        gc.strokeLine(x1, y1, x2, y2);
        gc.strokeLine(x2, y2, x3, y3);
        gc.strokeLine(x3, y3, x4, y4);
        gc.strokeLine(x4, y4, x5, y4);
        gc.strokeLine(x5, y4, x5, y5);
        gc.setLineDashes(null);

        // Dibujar Estaciones
        for (Station st : stations) {
            double sx = width * st.x; double sy = height * st.y;
            gc.setFill(!st.currentItems.isEmpty() ? Color.web("#1e293b") : Color.web("#0f172a"));
            gc.setStroke(Color.web("#38bdf8"));
            gc.setLineWidth(2);
            gc.fillOval(sx - 32, sy - 32, 64, 64);
            gc.strokeOval(sx - 32, sy - 32, 64, 64);

            gc.setFill(Color.web("#f8fafc"));
            gc.setFont(Font.font("Inter", FontWeight.BOLD, 11));
            gc.fillText(st.name, sx - 28, sy - 42);

            gc.setFill(Color.web("#38bdf8"));
            gc.setFont(Font.font("Inter", FontWeight.NORMAL, 10));
            gc.fillText(st.id.equals("reparacion") ? "Técnicos: " + st.currentItems.size() + "/" + st.capacity : st.tech, sx - 25, sy + 45);
            gc.fillText(st.subtext, sx - 16, sy + 58);
        }

        // Área de Salida
        double exitX = width * 0.75 - 70;
        double exitY = height * 0.88 - 30;
        gc.setFill(Color.web("#064e3b"));
        gc.setStroke(Color.web("#10b981"));
        gc.setLineWidth(2);
        gc.fillRect(exitX, exitY, 140, 50);
        gc.strokeRect(exitX, exitY, 140, 50);

        gc.setFill(Color.web("#34d399"));
        gc.setFont(Font.font("Inter", FontWeight.BOLD, 11));
        gc.fillText("Área de Salida", exitX + 28, exitY + 20);
        gc.setFill(Color.web("#f8fafc"));
        gc.fillText("Completados: " + completedCount, exitX + 26, exitY + 38);

        // Equipos
        for (Equipment eq : equipments) {
            gc.setFill(eq.state.equals("completed") ? Color.web("#10b981") : Color.web("#38bdf8"));
            gc.fillOval(eq.x - 9, eq.y - 9, 18, 18);
        }
    }

    private void updateTechsAndMetricsUI() {
        int inProcess = 0;
        for (Equipment e : equipments) if (!e.state.equals("completed")) inProcess++;

        statTotalLbl.setText(String.valueOf(equipmentsSpawned));
        statProcessLbl.setText(String.valueOf(inProcess));
        statCompletedLbl.setText(String.valueOf(completedCount));
        statAvgLbl.setText((completedCount > 0 ? (int)(totalTimeAccumulated / completedCount) : 0) + " min");

        int totalMins = (int) simulationTime;
        clockLbl.setText(String.format("Día %d - %02d:%02d", totalMins / 1440 + 1, (totalMins / 60) % 24 + 8, totalMins % 60));

        // Actualizar tarjetas del panel derecho
        for (TechInfo t : techs) {
            String activeItem = "Ninguna";
            boolean busy = false;
            for (Station st : stations) {
                if (st.tech.equals(t.name) && !st.currentItems.isEmpty()) {
                    busy = true;
                    List<String> names = new ArrayList<>();
                    for (Equipment eq : st.currentItems) names.add(eq.name);
                    activeItem = String.join(", ", names) + " (" + st.name + ")";
                }
            }
            if (busy) {
                t.statusLbl.setText("Ocupado");
                t.statusLbl.setTextFill(Color.web("#f59e0b"));
                t.taskLbl.setText("Carga actual: " + activeItem);
            } else {
                t.statusLbl.setText("Libre");
                t.statusLbl.setTextFill(Color.web("#10b981"));
                t.taskLbl.setText("Carga actual: Ninguna");
            }
        }
    }
}