import sys
import time
from collections import deque 
from PySide6.QtWidgets import QApplication

class LoggerSettings:
    def __init__(self):
        self.logcount = 1000
        self.persist_to_file = False
        self.log_file = "app.log"

    def to_dict(self):
        return self.__dict__

    def update_from_dict(self, data):
        self.__dict__.update(data)
        
class Logger:
    def __init__(self):
        app = QApplication.instance()
        self._settings = app.settings.logger
        self.logs = deque(maxlen=self._settings.logcount)
        self.persist_to_file = self._settings.persist_to_file
        self.log_file = self._settings.log_file

    def log(self, module, message, level="INFO"):
        entry = {"module": module, "message": message, "level": level}
        print(entry)
        self.logs.append(entry)
        if self.persist_to_file:
            with open(self.log_file, "a") as f:
                f.write(f"{level}: {message}\n")

    def get_logs(self):
        return list(self.logs)

