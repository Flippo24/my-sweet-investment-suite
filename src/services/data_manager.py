from PySide6.QtWidgets import QApplication
from services.broker.ib.ib import Ib
from services.broker.simulator.simulator import Simulator

class DataManager:
    def __init__(self):
        self.app = QApplication.instance()
        self.setting = self.app.settings
        self.app.broker = None

        self.setBroker(self.setting.broker.selected_broker)

    def setBroker(self, broker: str):
        if self.app.broker and (broker == self.setting.broker.selected_broker):
            pass
        if self.app.broker:
            self.broker.disconnect()
        match broker:
            case "Interactive Brokers":
                self.app.broker = Ib()
                self.setting.broker.selected_broker = "Interactive Brokers"
            case "Simulator":
                self.app.broker = Simulator()
                self.setting.broker.selected_broker = "Simulator"
            case _:
                self.app.broker = Simulator()
                self.setting.broker.selected_broker = "Simulator"
    
    

