from enum import Enum, auto
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Property
from PySide6.QtGui import QFontDatabase, QFont

class AppState(Enum):
    Startup = auto()
    Production = auto()
    Edit = auto()
    Closing = auto()

class Theme(QObject):
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        self.setMode("Startup")

        self.custom_font = None
        self.loadFonts()

        with open("src/resources/stylesheet.qss", "r") as file:
            self.app.setStyleSheet(file.read())

    def setMode(self, state):
        """Setzt den Zustand der Applikation"""
        self.app.setProperty("appState", state)
        for widget in self.app.topLevelWidgets():
            # Stylesheet neu anwenden und Widget neu zeichnen
            widget.update()

    def loadFonts(self):
        # Schriftart aus Datei laden
        font_path = "src/resources/fonts/Pacifico-Regular.ttf"
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print("Fehler: Schriftart konnte nicht geladen werden.")
        else:
            self.custom_font = QFont(QFontDatabase.applicationFontFamilies(font_id)[0])
            self.custom_font.setPointSize(12)  # Schriftgröße setzen
        print(f"Geladene Schriftarten: {QFontDatabase.applicationFontFamilies(font_id)}")