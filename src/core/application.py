import asyncio
from ib_async import util

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import  QJsonDocument

from services.themes.theme_manager import ThemeManager
from services.settings import Settings
from services.workspace import WorkspaceSettings
from services.themes.theme import Theme
from services.logger.logger import Logger
from services.data_manager import DataManager


class Application(QApplication):
    def __init__(self, argv):
        super().__init__(argv)

        # Setze Appzustand auf Startup
        self.setProperty("appState", "Startup")
        self.theme = Theme()

        # load Settings
        self.settings = Settings('settings.json')

        # selt logger
        self.logger = Logger()

        # set theme
        self.theme_manager = ThemeManager()
        self.theme_manager.setStylesheet()
        
        #self.settings.load_from_file('settings.json')
        self.data_manager = DataManager()

        self.is_closing_all = False
        self.aboutToQuit.connect(self.close_app)
        #self.logger.log("bla","blub")

        self.theme.setMode("Production")

    def startup(self):
        if self.property("appState") == "Production" and self.settings.broker.ib.connect_at_startup:
            #self.broker.connect()
            asyncio.create_task(self.broker.connect())
        self.settings.workspace.load_workspace()

    def close_app(self):
        try:
            self.broker.disconnect()
        except Exception as e:
            print("Fehler beim Disconnect:", e)
        self.settings.workspace.save_workspace()
        self.settings.save_to_file()
        util.getLoop().stop()
