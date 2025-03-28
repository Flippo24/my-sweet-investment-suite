from PySide6.QtWidgets import (
    QApplication, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame
)
from PySide6.QtCore import Qt
#from PySide6.QtGui import QPainter, QPen, QColor
from widgets.base_widget import BaseWidget
#import sys

class CustomButtonWidget(BaseWidget):
    def __init__(self, title="Titel", description="Beschreibung", parent=None):
        super().__init__()
        
        self.title = title
        self.description = description
        self.setProperty("widgetType", "testWidget")
        
        self.init_ui()

    def init_ui(self):
        # Hauptlayout
        layout = QVBoxLayout()

        # Titel Label
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; font-size: 16px;")

        # Beschreibung Label – als Attribut speichern, um später aktualisieren zu können
        self.description_label = QLabel(self.description)
        self.description_label.setWordWrap(True)

        # Button unten rechts
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        action_button = QPushButton("Toggle Border")
        action_button.setFixedSize(100, 30)
        button_layout.addWidget(action_button)

        layout.addWidget(self.title_label)
        layout.addWidget(self.description_label)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def save_parameters(self):
        # Speichert die relevanten Parameter
        return {"title": self.title, "description": self.description}

    def restore_parameters(self, params):
        # Stellt die Parameter wieder her und aktualisiert die UI-Elemente
        params = params or {}
        self.title = params.get("title", self.title)
        self.description = params.get("description", self.description)
        self.title_label.setText(self.title)
        self.description_label.setText(self.description)

    def enterEvent(self, event):
        print("Hover gestartet")
        super().enterEvent(event)

    def leaveEvent(self, event):
        print("Hover beendet")
        super().leaveEvent(event)
