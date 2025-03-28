import sys
import json
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Signal, QObject

from services.workspace import WorkspaceSettings
from services.logger.logger import LoggerSettings
from services.broker.broker_settings import BrokerSettings

class Settings(QObject):
    def __init__(self, filename):
        super().__init__()
        self._edit_mode = False
        self.settings_file = filename
        #self.theme = Theme()
        self.workspace = WorkspaceSettings()
        self.logger = LoggerSettings()
        self.broker = BrokerSettings()

        self.load_from_file()

    def to_dict(self):
        return {
            "workspace": self.workspace.to_dict(),
            "logger": self.logger.to_dict(),
            "broker": self.broker.to_dict(),
        }

    def update_from_dict(self, data):
        self.workspace.update_from_dict(data["workspace"])
        self.logger.update_from_dict(data["logger"])
        self.broker.update_from_dict(data["broker"])

    def save_to_file(self):
        """Save the settings to a JSON file."""
        with open(self.settings_file, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)

    def load_from_file(self):
        """Load settings from a JSON file."""
        if not os.path.exists(self.settings_file):
            print(f"Settings file '{self.settings_file}' does not exist. Loading default settings.")
            return
            #raise FileNotFoundError(f"Settings file '{self.settings_file}' does not exist.")
        with open(self.settings_file, 'r') as f:
            data = json.load(f)
        self.update_from_dict(data)
        