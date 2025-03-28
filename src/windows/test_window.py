from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QFileDialog
from services.theme_loader import ThemeLoader

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QSS Theme Loader")

        # Layout
        layout = QVBoxLayout()

        self.label = QLabel("Lade ein Theme und generiere QSS.")
        layout.addWidget(self.label)

        load_button = QPushButton("Load and Apply Theme")
        load_button.clicked.connect(self.load_and_apply_theme)
        layout.addWidget(load_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_and_apply_theme(self):
        """Lädt das Theme und generiert das QSS."""
        # Wähle Template und Theme Dateien
        template_path, _ = QFileDialog.getOpenFileName(self, "Select QSS Template", "", "QSS Files (*.qss)")
        theme_path, _ = QFileDialog.getOpenFileName(self, "Select VS Code Theme", "", "JSON Files (*.json)")
        if not template_path or not theme_path:
            self.label.setText("Abgebrochen.")
            return

        loader = ThemeLoader(template_path, theme_path)

        try:
            template = loader.load_template()
            theme = loader.load_theme()
            stylesheet = loader.apply_theme(template, theme)

            # Speichern des generierten Stylesheets
            output_path, _ = QFileDialog.getSaveFileName(self, "Save QSS File", "output.qss", "QSS Files (*.qss)")
            if output_path:
                loader.save_qss(output_path, stylesheet)
                self.label.setText(f"QSS gespeichert: {output_path}")
            else:
                self.label.setText("Speichern abgebrochen.")

            # Anwenden des Stylesheets auf die App
            app.setStyleSheet(stylesheet)

        except Exception as e:
            self.label.setText(f"Fehler: {e}")