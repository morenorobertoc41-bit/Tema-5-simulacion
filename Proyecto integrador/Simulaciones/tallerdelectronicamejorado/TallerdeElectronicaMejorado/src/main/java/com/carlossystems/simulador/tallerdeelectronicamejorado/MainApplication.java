package com.carlossystems.simulador.tallerdeelectronicamejorado;

import javafx.application.Application;
import javafx.stage.Stage;

public class MainApplication extends Application {
    @Override
    public void start(Stage stage) {
        Taller app = new Taller();
        app.start(stage);
    }

    public static void main(String[] args) {
        launch();
    }
}
