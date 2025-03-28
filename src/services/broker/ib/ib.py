import asyncio
import datetime
import psutil
import os
import subprocess
from ib_async import IB, util
from ib_async.contract import *

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

class IbSettings:
    def __init__(self):
        self.ip = "127.0.0.1"
        self.port = 7496 #4001
        self.clientId = 1
        self.read_only = True
        self.connect_at_startup = False

    def to_dict(self):
        return self.__dict__

    def update_from_dict(self, data):
        self.__dict__.update(data)
        
class Ib:
    def __init__(self, settings=None):
        self.app = QApplication.instance()
        self.setting = self.app.settings
        self.ib = IB()
        # Dictionary zur Verwaltung aktiver Live-Daten-Abonnements.
        # key: request_id, value: { 'instrument': Contract, 'observers': [callback, ...] }
        self.active_market_data = {}
        self.subscription_lock = asyncio.Lock()

    async def connect(self):
        if self.setting.broker.ib.ip == "127.0.0.1":
            # Prüfen, ob TWS oder IBGateway läuft
            if not self.is_ib_gateway_running():
                print("TWS oder IBGateway ist nicht geöffnet!")
                return
        else:
            # Prüfen, ob die IP erreichbar ist (ping)
            if not await self.is_ip_reachable(self.setting.broker.ib.ip):
                print(f"Die IP {self.setting.broker.ib.ip} ist nicht erreichbar.")
                return

        try:
            await self.ib.connectAsync(
                self.setting.broker.ib.ip,
                self.setting.broker.ib.port,
                clientId=self.setting.broker.ib.clientId,
                readonly=self.setting.broker.ib.read_only,
                timeout=4
            )
            print("Verbunden mit Interactive Brokers API.")
        except Exception as e:
            print(f"Fehler beim Verbinden mit IB: {e}")

    def disconnect(self):
        if self.ib.isConnected():
            self.ib.disconnect()
            print("Verbindung zur Interactive Brokers API getrennt.")

    def is_ib_gateway_running(self):
        """
        Prüft, ob TWS oder IBGateway als Prozess läuft.
        """
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if 'java' in proc.info['name'].lower():
                for cmd in proc.info['cmdline']:
                    if '-DproductName=IB Gateway' in cmd or '-DproductName=Trader Workstation' in cmd:
                        return True
        return False

    async def is_ip_reachable(self, ip):
        """
        Prüft, ob eine IP-Adresse erreichbar ist (ping).
        """
        try:
            # Ping-Befehl je nach Betriebssystem
            if os.name == 'nt':
                # Windows: Verwendung von 'ping -n 1'
                cmd = ['ping', '-n', '1', ip]
            else:
                # Unix (Linux/Mac): Verwendung von 'ping -c 1'
                cmd = ['ping', '-c', '1', ip]
                
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return result.returncode == 0  # Rückgabewert 0 bedeutet erfolgreich
        except Exception as e:
            print(f"Fehler beim Pingen der IP {ip}: {e}")
            return False

    # --- Live Market Data Methoden ---
    async def subscribe_market_data(self, instrument, callback, request_id):
        """
        Abonnieren von Echtzeit-Marktdaten für das angegebene Instrument.
        Falls bereits ein Abo für den request_id existiert, wird der neue Observer hinzugefügt.
        :param instrument: IB Contract (z. B. Aktie, Option, etc.)
        :param callback: Funktion, die mit den aktuellen Marktdaten aufgerufen wird.
        :param request_id: Eindeutige ID, die auch zum Abbestellen benötigt wird.
        """
        async with self.subscription_lock:
            if request_id in self.active_market_data:
                # Observer zur bestehenden Subscription hinzufügen.
                self.active_market_data[request_id]['observers'].append(callback)
                return
            else:
                self.active_market_data[request_id] = {
                    'instrument': instrument,
                    'observers': [callback]
                }
                try:
                    # Abonnieren der Marktdaten via IB-API.
                    # Hier wird ein asynchroner Aufruf getätigt – passe ggf. den Parameter "genericTickList" an.
                    ticker = await self.ib.reqMktDataAsync(instrument, "", False, False, requestId=request_id)
                    # Bei Updates wird unser interner Callback aufgerufen.
                    ticker.updateEvent += lambda data: self._market_data_callback(request_id, data)
                except Exception as e:
                    print(f"Error subscribing to market data for request_id {request_id}: {e}")
                    del self.active_market_data[request_id]

    def _market_data_callback(self, request_id, data):
        """
        Interner Callback, der bei neuen Marktdaten alle registrierten Observer benachrichtigt.
        """
        if request_id in self.active_market_data:
            for observer in self.active_market_data[request_id]['observers']:
                try:
                    observer(data)
                except Exception as e:
                    print(f"Error in market data observer: {e}")

    async def unsubscribe_market_data(self, request_id):
        """
        Beendet das Abonnement von Echtzeit-Marktdaten anhand der request_id.
        """
        async with self.subscription_lock:
            if request_id in self.active_market_data:
                try:
                    await self.ib.cancelMktDataAsync(request_id)
                    del self.active_market_data[request_id]
                except Exception as e:
                    print(f"Error unsubscribing market data for request_id {request_id}: {e}")
            else:
                print(f"No active subscription with request_id {request_id}")

    # --- Historische Daten ---
    async def fetch_historical_data(self, instrument, end_datetime: datetime.datetime, duration_str: str, bar_size: str, what_to_show="MIDPOINT", use_rth=False):
        """
        Abfrage historischer Daten für ein Instrument.
        :param instrument: IB Contract.
        :param end_datetime: Endzeitpunkt als datetime.
        :param duration_str: Dauerangabe, z. B. "50 D" für 50 Tage.
        :param bar_size: Zeitintervall, z. B. "1 min", "5 mins", "1 day", "tick", etc.
        :param what_to_show: Datentyp (Standard: "MIDPOINT").
        :param use_rth: Nur reguläre Handelszeiten verwenden.
        :return: Historische Daten (z. B. als Liste von Bars).
        """
        try:
            # Format: "YYYYMMDD HH:MM:SS"
            end_str = end_datetime.strftime("%Y%m%d %H:%M:%S")
            data = await self.ib.reqHistoricalDataAsync(
                instrument,
                endDateTime=end_str,
                durationStr=duration_str,
                barSizeSetting=bar_size,
                whatToShow=what_to_show,
                useRTH=use_rth,
                formatDate=1
            )
            return data
        except Exception as e:
            print(f"Error fetching historical data: {e}")
            return None

    # --- Konto- und Portfoliodaten ---
    async def fetch_account_info(self):
        """
        Abfrage aller Kontoinformationen von IB.
        :return: Account-Daten (z. B. als Dictionary).
        """
        try:
            account_info = await self.ib.reqAccountUpdatesAsync(subscribe=False)
            return account_info
        except Exception as e:
            print(f"Error fetching account info: {e}")
            return None

    async def fetch_portfolio(self):
        """
        Abfrage der Portfoliodaten.
        :return: Portfolio-Daten.
        """
        try:
            portfolio = await self.ib.reqPositionsAsync()
            return portfolio
        except Exception as e:
            print(f"Error fetching portfolio: {e}")
            return None

# --- Dediziertes Interface für Optionsdaten ---
class OptionChain:
    """
    Diese Klasse kapselt die Abfrage von Optionsdaten für ein zugrundeliegendes Instrument.
    Zunächst werden alle verfügbaren Expiration Dates und Strike-Preise abgefragt,
    sodass anschließend detaillierte Contract Details ermittelt werden können.
    """
    def __init__(self, ib_instance: Ib):
        self.ib = ib_instance  # Instanz der Ib-Klasse

    async def fetch_available_expirations(self, underlying: Contract):
        """
        Ruft alle verfügbaren Expiration Dates für das zugrunde liegende Instrument ab.
        :param underlying: IB Contract des Underlyings.
        :return: Liste von Expiration Dates (als Strings).
        """
        try:
            # Erzeugen eines Options-Templates ohne spezifiziertes Ablaufdatum
            option = Option(
                symbol=underlying.symbol,
                exchange=underlying.exchange,
                currency=underlying.currency,
                lastTradeDateOrContractMonth=""
            )
            details = await self.ib.ib.reqContractDetailsAsync(option)
            expirations = {d.contract.lastTradeDateOrContractMonth for d in details}
            return sorted(list(expirations))
        except Exception as e:
            print(f"Error fetching available expirations: {e}")
            return []

    async def fetch_available_strikes(self, underlying: Contract, expiration: str):
        """
        Ruft alle verfügbaren Strike-Preise für ein bestimmtes Expiration Date ab.
        :param underlying: IB Contract des Underlyings.
        :param expiration: Gewünschtes Expiration Date.
        :return: Liste von Strike-Preisen.
        """
        try:
            option = Option(
                symbol=underlying.symbol,
                exchange=underlying.exchange,
                currency=underlying.currency,
                lastTradeDateOrContractMonth=expiration,
                right=""  # Beide Optionstypen (Call & Put)
            )
            details = await self.ib.ib.reqContractDetailsAsync(option)
            strikes = {d.contract.strike for d in details}
            return sorted(list(strikes))
        except Exception as e:
            print(f"Error fetching available strikes: {e}")
            return []

    async def fetch_option_chain(self, underlying: Contract, expiration: str, strike_min=None, strike_max=None, right=None):
        """
        Ruft detaillierte Optionsdaten (Option Chain) für das zugrundeliegende Instrument ab.
        :param underlying: IB Contract des Underlyings.
        :param expiration: Gewähltes Expiration Date.
        :param strike_min: Optionale Mindeststrike (zum Filtern).
        :param strike_max: Optionale Höchststrike (zum Filtern).
        :param right: "C" für Call, "P" für Put, oder leer für beide.
        :return: Liste von Contract Details für Optionen.
        """
        try:
            option = Option(
                symbol=underlying.symbol,
                exchange=underlying.exchange,
                currency=underlying.currency,
                lastTradeDateOrContractMonth=expiration,
                right=right if right in ["C", "P"] else ""
            )
            details = await self.ib.ib.reqContractDetailsAsync(option)
            if strike_min is not None or strike_max is not None:
                filtered = []
                for d in details:
                    if strike_min is not None and d.contract.strike < strike_min:
                        continue
                    if strike_max is not None and d.contract.strike > strike_max:
                        continue
                    filtered.append(d)
                details = filtered
            return details
        except Exception as e:
            print(f"Error fetching option chain: {e}")
            return []