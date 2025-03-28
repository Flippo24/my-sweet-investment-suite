import os
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QLabel, QListWidget, QHBoxLayout, QPushButton,
    QWidget, QMessageBox, QDialog)
from services.themes.theme_add_dialog import ThemeDialog

class ThemeListWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        self.theme_manager = self.app.theme_manager
        self.logger = self.app.logger  # Logger-Instanz abrufen

        self.setWindowTitle("Theme Manager")
        self.init_ui()

    def init_ui(self):
        """Erstellt die Benutzeroberfläche."""
        layout = QVBoxLayout()

        self.active_theme_label = QLabel("aktuelles Theme: {self.theme_manager.active_theme}")
        self.update_active_theme_label()
        layout.addWidget(self.active_theme_label)

        self.theme_list = QListWidget()
        self.load_theme_list()
        layout.addWidget(self.theme_list)

        button_layout = QHBoxLayout()

        add_button = QPushButton("Add Theme")
        add_button.clicked.connect(self.add_theme)
        button_layout.addWidget(add_button)

        remove_button = QPushButton("Remove Theme")
        remove_button.clicked.connect(self.remove_theme)
        button_layout.addWidget(remove_button)

        apply_button = QPushButton("Apply Theme")
        apply_button.clicked.connect(self.apply_theme)
        button_layout.addWidget(apply_button)

        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def update_active_theme_label(self):
        """Aktualisiert die Anzeige des aktiven Themes."""
        active_theme = self.theme_manager.active_theme or "None"
        self.active_theme_label.setText(f"Active Theme: {active_theme}")

    def load_theme_list(self):
        """Lädt die Themes in die Liste."""
        self.theme_list.clear()
        try:
            for theme in self.theme_manager.themes:
                self.theme_list.addItem(f"{theme['name']} (by {theme['author']})")
            self.logger.log("ThemeListWindow", "Theme list loaded successfully", level="DEBUG")
        except Exception as e:
            self.logger.log("ThemeListWindow", f"Error loading theme list: {e}", level="ERROR")
            QMessageBox.critical(self, "Error", f"Error loading theme list: {e}")

    def add_theme(self):
        """Fügt ein neues Theme hinzu."""
        dialog = ThemeDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            self.logger.log("ThemeListWindow", f"Add theme dialog accepted with data: {data}", level="INFO")
            if data["theme_url"]:
                file_path = os.path.join(os.getcwd(), f"{data['name']}.json")
                try:
                    self.logger.log("ThemeListWindow", f"Attempting to download theme from {data['theme_url']}", level="DEBUG")
                    self.theme_manager.download_theme(data["theme_url"], file_path)
                    data["file_path"] = file_path
                    self.logger.log("ThemeListWindow", "Theme downloaded successfully", level="INFO")
                except Exception as e:
                    self.logger.log("ThemeListWindow", f"Failed to download theme: {e}", level="ERROR")
                    QMessageBox.critical(self, "Error", f"Failed to download theme: {e}")
                    return

            if not data["file_path"] or not os.path.exists(data["file_path"]):
                self.logger.log("ThemeListWindow", "No valid theme file provided", level="WARNING")
                QMessageBox.warning(self, "Warning", "No valid theme file provided.")
                return

            try:
                self.theme_manager.add_theme(data["name"], data["author"], data["project_url"],
                                             data["theme_url"], data["file_path"])
                self.logger.log("ThemeListWindow", f"Theme '{data['name']}' added successfully", level="INFO")
                self.load_theme_list()
            except Exception as e:
                self.logger.log("ThemeListWindow", f"Failed to add theme: {e}", level="ERROR")
                QMessageBox.critical(self, "Error", f"Failed to add theme: {e}")

    def remove_theme(self):
        """Entfernt ein Theme."""
        current_item = self.theme_list.currentItem()
        if not current_item:
            self.logger.log("ThemeListWindow", "No theme selected for removal", level="WARNING")
            QMessageBox.warning(self, "Warning", "No theme selected.")
            return

        theme_name = current_item.text().split(" (by ")[0]
        try:
            self.theme_manager.remove_theme(theme_name)
            self.logger.log("ThemeListWindow", f"Theme '{theme_name}' removed successfully", level="INFO")
            self.load_theme_list()
            self.update_active_theme_label()
        except Exception as e:
            self.logger.log("ThemeListWindow", f"Failed to remove theme '{theme_name}': {e}", level="ERROR")
            QMessageBox.critical(self, "Error", f"Failed to remove theme: {e}")

    def apply_theme(self):
        """Wendet ein ausgewähltes Theme an."""
        current_item = self.theme_list.currentItem()
        if not current_item:
            self.logger.log("ThemeListWindow", "No theme selected for application", level="WARNING")
            QMessageBox.warning(self, "Warning", "No theme selected.")
            return

        theme_name = current_item.text().split(" (by ")[0]
        theme = next((t for t in self.theme_manager.themes if t["name"] == theme_name), None)
        if not theme:
            self.logger.log("ThemeListWindow", f"Selected theme '{theme_name}' not found", level="ERROR")
            QMessageBox.critical(self, "Error", "Selected theme not found.")
            return

        try:
            if not os.path.exists(theme["file_path"]):
                self.logger.log("ThemeListWindow", f"Theme file for '{theme_name}' not found, attempting download", level="WARNING")
                self.theme_manager.download_theme(theme["theme_url"], theme["file_path"])
            theme_data = self.theme_manager.load_theme(theme["file_path"])
            stylesheet = self.theme_manager.apply_theme(theme_data)
            QApplication.instance().setStyleSheet(stylesheet)
            self.theme_manager.set_active_theme(theme_name)
            self.logger.log("ThemeListWindow", f"Theme '{theme_name}' applied successfully", level="INFO")
            self.update_active_theme_label()
        except Exception as e:
            self.logger.log("ThemeListWindow", f"Failed to apply theme '{theme_name}': {e}", level="ERROR")
            QMessageBox.critical(self, "Error", f"Failed to apply theme: {e}")
