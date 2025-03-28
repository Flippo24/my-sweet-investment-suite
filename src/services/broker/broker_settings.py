from PySide6.QtCore import Signal

from services.broker.ib.ib import IbSettings
from services.broker.simulator.simulator import SimulatorSettings

class BrokerSettings:
    broker_settings_updated = Signal(dict)
    def __init__(self):
        self.selected_broker = None
        self.ib = IbSettings()
        self.simulator = SimulatorSettings()

    def to_dict(self):
        return {
            "selected_broker": self.selected_broker,
            "ib": self.ib.to_dict(),
            "simulator": self.simulator.to_dict(),
        }

    def update_from_dict(self, data):
        self.selected_broker = data["selected_broker"]
        self.ib.update_from_dict(data["ib"])
        self.simulator.update_from_dict(data["simulator"])

