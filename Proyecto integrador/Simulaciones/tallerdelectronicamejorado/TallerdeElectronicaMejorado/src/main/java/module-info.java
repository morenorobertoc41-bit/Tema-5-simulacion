module com.carlossystems.simulador.talleredelectronicamejorado {
    requires javafx.controls;
    requires javafx.fxml;

    opens com.carlossystems.simulador.tallerdeelectronicamejorado to javafx.fxml;
    exports com.carlossystems.simulador.tallerdeelectronicamejorado;
}