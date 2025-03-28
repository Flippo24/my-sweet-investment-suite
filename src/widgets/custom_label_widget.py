from PySide6.QtWidgets import QLabel, QVBoxLayout
from widgets.base_widget import BaseWidget

class CustomLabelWidget(BaseWidget):
    def __init__(self):
        super().__init__()
        #self.setText("Custom Label Widget")
        self.label = QLabel("Custom Label Widget", self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def save_parameters(self):
        # Speichert den angezeigten Text
        return {"text": self.label.text()}

    def restore_parameters(self, params):
        # Stellt den Text wieder her, falls vorhanden
        params = params or {}
        self.label.setText(params.get("text", "Custom Label Widget"))