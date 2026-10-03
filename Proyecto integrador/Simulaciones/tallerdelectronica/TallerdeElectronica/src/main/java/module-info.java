module com.carlossystems.simulador.talleredelectronica {
    requires javafx.controls;
    requires javafx.fxml;

    opens com.carlossystems.simulador.tallerdeelectronica to javafx.fxml;
    exports com.carlossystems.simulador.tallerdeelectronica;
}