import json
import os
import re
import urllib.request

from PySide6.QtWidgets import QApplication

class ThemeManager:
    THEMES_FILE = "themes.json"

    def __init__(self, template_path="src/resources/themes/template.qss"):
        #elf.logger = QApplication.instance().logger  # Logger aus der Application abrufen
        self.template_path = template_path
        self.themes = []
        self.active_theme = None
        try:
            self.load_themes()
            #self.logger.log("ThemeManager", "Themes loaded successfully", level="INFO")
        except Exception as e:
            #self.logger.log("ThemeManager", f"Error loading themes: {e}", level="ERROR")
            pass 

    def load_template(self):
        """Liest die QSS-Vorlage ein."""
        try:
            with open(self.template_path, 'r') as file:
                template = file.read()
            #self.logger.log("ThemeManager", "Template loaded successfully", level="DEBUG")
            return template
        except Exception as e:
            #self.logger.log("ThemeManager", f"Error loading template from {self.template_path}: {e}", level="ERROR")
            raise e

    def load_theme(self, theme_path):
        """Liest das VS Code Theme (JSON) ein."""
        try:
            with open(theme_path, 'r') as file:
                theme = json.load(file)
            #self.logger.log("ThemeManager", f"Theme loaded from {theme_path}", level="DEBUG")
            return theme
        except Exception as e:
            #self.logger.log("ThemeManager", f"Error loading theme from {theme_path}: {e}", level="ERROR")
            raise e

    def apply_theme_on_css(self, template, colors):
        def replace_color(match):
            key = match.group(1)
            return colors.get(key, match.group(0))
        return re.sub(r'\$\{([a-zA-Z0-9_.]+)\}', replace_color, template)

    def apply_theme(self, theme):
        """Ersetzt die Platzhalter im Template durch die Farben aus dem Theme."""
        try:
            template = self.load_template()
            colors = theme.get("colors", {})
            stylesheet = self.apply_theme_on_css(template, colors)
            #self.logger.log("ThemeManager", "Theme applied successfully", level="DEBUG")
            return stylesheet
        except Exception as e:
            #self.logger.log("ThemeManager", f"Error applying theme: {e}", level="ERROR")
            raise e

    def save_qss(self, output_path, stylesheet):
        """Speichert das generierte QSS."""
        try:
            with open(output_path, 'w') as file:
                file.write(stylesheet)
            #self.logger.log("ThemeManager", f"Stylesheet saved to {output_path}", level="INFO")
        except Exception as e:
            #self.logger.log("ThemeManager", f"Error saving stylesheet to {output_path}: {e}", level="ERROR")
            raise e

    def load_themes(self):
        """Lädt die Themes aus der JSON-Datei."""
        try:
            if os.path.exists(self.THEMES_FILE):
                with open(self.THEMES_FILE, 'r') as file:
                    data = json.load(file)
                    self.themes = data.get("themes", [])
                    self.active_theme = data.get("active_theme")
                #self.logger.log("ThemeManager", "Themes loaded from file", level="DEBUG")
            else:
                #self.logger.log("ThemeManager", f"Theme file {self.THEMES_FILE} does not exist. Using defaults.", level="WARNING")
                pass
        except Exception as e:
            #self.logger.log("ThemeManager", f"Error loading themes from file: {e}", level="ERROR")
            raise e

    def save_themes(self):
        """Speichert die Themes in die JSON-Datei."""
        try:
            with open(self.THEMES_FILE, 'w') as file:
                json.dump({"themes": self.themes, "active_theme": self.active_theme}, file, indent=4)
            #self.logger.log("ThemeManager", "Themes saved successfully", level="DEBUG")
        except Exception as e:
            #self.logger.log("ThemeManager", f"Error saving themes: {e}", level="ERROR")
            raise e

    def add_theme(self, name, author, project_url, theme_url, file_path):
        """Fügt ein neues Theme hinzu."""
        try:
            self.themes.append({
                "name": name,
                "author": author,
                "project_url": project_url,
                "theme_url": theme_url,
                "file_path": file_path
            })
            self.save_themes()
            #self.logger.log("ThemeManager", f"Theme '{name}' added successfully", level="INFO")
        except Exception as e:
            #self.logger.log("ThemeManager", f"Error adding theme '{name}': {e}", level="ERROR")
            raise e

    def remove_theme(self, theme_name):
        """Entfernt ein Theme."""
        try:
            theme = next((t for t in self.themes if t["name"] == theme_name), None)
            if theme:
                file_path = theme.get("file_path")
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    #self.logger.log("ThemeManager", f"Theme file {file_path} removed", level="DEBUG")
                self.themes = [t for t in self.themes if t["name"] != theme_name]
                if self.active_theme == theme_name:
                    self.active_theme = None
                self.save_themes()
                #self.logger.log("ThemeManager", f"Theme '{theme_name}' removed successfully", level="INFO")
        except Exception as e:
            #self.logger.log("ThemeManager", f"Error removing theme '{theme_name}': {e}", level="ERROR")
            raise e

    def set_active_theme(self, theme_name):
        """Setzt das aktive Theme."""
        try:
            self.active_theme = theme_name
            self.save_themes()
            #self.logger.log("ThemeManager", f"Active theme set to '{theme_name}'", level="INFO")
        except Exception as e:
            #self.logger.log("ThemeManager", f"Error setting active theme to '{theme_name}': {e}", level="ERROR")
            raise e

    def download_theme(self, url, save_path):
        """Lädt ein Theme von einer URL herunter."""
        try:
            with urllib.request.urlopen(url) as response:
                content = response.read().decode()
            with open(save_path, 'w') as file:
                file.write(content)
            #self.logger.log("ThemeManager", f"Theme downloaded successfully from {url}", level="INFO")
        except Exception as e:
            #self.logger.log("ThemeManager", f"Error downloading theme from {url}: {e}", level="ERROR")
            raise e

    def load_active_theme(self):
        """Lädt und wendet das aktive Theme an."""
        try:
            if not self.active_theme:
                #self.logger.log("ThemeManager", "No active theme set.", level="ERROR")
                raise ValueError("No active theme set.")

            theme = next((t for t in self.themes if t["name"] == self.active_theme), None)
            if not theme:
                #self.logger.log("ThemeManager", f"Active theme '{self.active_theme}' not found in themes.json.", level="ERROR")
                raise ValueError(f"Active theme '{self.active_theme}' not found in themes.json.")

            # Überprüfen, ob die Theme-Datei existiert
            if not os.path.exists(theme["file_path"]):
                if theme.get("theme_url"):
                    #self.logger.log("ThemeManager", f"Theme file for '{self.active_theme}' not found, attempting download", level="WARNING")
                    self.download_theme(theme["theme_url"], theme["file_path"])
                else:
                    raise FileNotFoundError(f"Theme file '{theme['file_path']}' not found and no URL provided.")

            theme_data = self.load_theme(theme["file_path"])
            stylesheet = self.apply_theme(theme_data)
            #self.logger.log("ThemeManager", f"Active theme '{self.active_theme}' loaded successfully", level="INFO")
            return stylesheet
        except Exception as e:
            #self.logger.log("ThemeManager", f"Error loading active theme: {e}", level="ERROR")
            raise e

    def setStylesheet(self):
        try:
            stylesheet = self.load_active_theme()
            QApplication.instance().setStyleSheet(stylesheet)
            #self.logger.log("ThemeManager", "Stylesheet set successfully", level="INFO")
        except Exception as e:
            #self.logger.log("ThemeManager", f"Failed to set stylesheet: {e}", level="ERROR")
            pass