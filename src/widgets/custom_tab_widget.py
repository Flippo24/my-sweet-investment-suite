from PySide6.QtWidgets import QTabWidget, QWidget
from widgets.base_widget import BaseWidget

class CustomTabWidget(BaseWidget, QTabWidget):
    def __init__(self, text="Tab-Widget"):
        BaseWidget.__init__(self, text)
        QTabWidget.__init__(self)
        self.setText("Custom Tab Widget")
        self.addTab(QWidget(), "Tab 1")
        self.addTab(QWidget(), "Tab 2")