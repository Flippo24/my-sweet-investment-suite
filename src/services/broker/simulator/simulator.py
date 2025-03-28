import asyncio
import datetime
from PySide6.QtWidgets import QApplication

class SimulatorSettings:
    def __init__(self):
        self.read_only = True

    def to_dict(self):
        return self.__dict__

    def update_from_dict(self, data):
        self.__dict__.update(data)
        
class Simulator:
    """
    Simulierter Broker, der dieselbe Schnittstelle wie Ib implementiert.
    Es werden keine externen API-Aufrufe getätigt – stattdessen werden Dummy-Daten zurückgegeben.
    """
    def __init__(self, settings=None):
        self.app = QApplication.instance()
        self.setting = self.app.settings
        self.active_market_data = {}
        # Simuliere eine schnelle Verbindung
        #asyncio.create_task(self.connect())
        self.connect()

    async def connect(self):
        await asyncio.sleep(0.1)
        print("Simulator connected.")

    async def disconnect(self):
        await asyncio.sleep(0.1)
        print("Simulator disconnected.")

    # --- Live Market Data Methoden ---
    async def subscribe_market_data(self, instrument, callback, request_id):
        if request_id in self.active_market_data:
            self.active_market_data[request_id]['observers'].append(callback)
        else:
            self.active_market_data[request_id] = {
                'instrument': instrument,
                'observers': [callback]
            }
            asyncio.create_task(self._simulate_market_data(request_id))

    async def _simulate_market_data(self, request_id):
        while request_id in self.active_market_data:
            data = {"price": 100.0, "volume": 10}  # Dummy-Daten
            for observer in self.active_market_data[request_id]['observers']:
                try:
                    observer(data)
                except Exception as e:
                    print(f"Simulator observer error: {e}")
            await asyncio.sleep(1)

    async def unsubscribe_market_data(self, request_id):
        if request_id in self.active_market_data:
            del self.active_market_data[request_id]
            print(f"Simulator unsubscribed market data for request_id {request_id}")
        else:
            print(f"No active subscription in simulator for request_id {request_id}")

    # --- Historische Daten ---
    async def fetch_historical_data(self, instrument, end_datetime: datetime.datetime, duration_str: str, bar_size: str, what_to_show="MIDPOINT", use_rth=False):
        await asyncio.sleep(0.1)
        # Rückgabe von Dummy-Historischen Daten
        return [{
            "date": end_datetime.strftime("%Y%m%d"),
            "open": 100,
            "high": 105,
            "low": 95,
            "close": 102
        }]

    # --- Konto- und Portfoliodaten ---
    async def fetch_account_info(self):
        await asyncio.sleep(0.1)
        return {"account": "SIM123", "balance": 10000}

    async def fetch_portfolio(self):
        await asyncio.sleep(0.1)
        return [{"symbol": "SIM_STOCK", "position": 50, "avg_cost": 100}]

    # --- OptionChain Interface ---
    async def fetch_available_expirations(self, underlying):
        await asyncio.sleep(0.1)
        return ["20250117", "20250221"]

    async def fetch_available_strikes(self, underlying, expiration):
        await asyncio.sleep(0.1)
        return [90, 95, 100, 105, 110]

    async def fetch_option_chain(self, underlying, expiration, strike_min=None, strike_max=None, right=None):
        await asyncio.sleep(0.1)
        # Dummy-Option Chain Details
        return [{
            "strike": 100,
            "right": "C",
            "expiration": expiration
        }]

