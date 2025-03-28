import sys
import asyncio
from ib_async import IB, util
from PySide6.QtCore import QTimer
from core.application import Application

if __name__ == "__main__":
    util.patchAsyncio()
    app = Application(sys.argv)
    util.useQt('PySide6', qtContext=app)
    loop = asyncio.get_event_loop()
    loop.call_soon(app.startup)
    sys.exit(IB.run())

