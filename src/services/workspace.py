import sys
import json
import uuid

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QApplication

from windows.main_window import MainWindow
from widgets.base_widget import BaseWidget
from widgets.custom_label_widget import CustomLabelWidget
from widgets.custom_button_widget import CustomButtonWidget
from widgets.custom_data_widget import CustomDataWidget

class WorkspaceSettings:
    workspace_settings_updated = Signal(dict)
    def __init__(self):
        self.workspace = {}
        self.windows = []

    def save_workspace(self):
        workspace_data = {}
        for window in self.windows:
            workspace_data[window.objectName] = {
                "type": type(window).__name__,
                "objectname": window.objectName,
                "geometry": {
                    "x": window.x(),
                    "y": window.y(),
                    "width": window.width(),
                    "height": window.height(),
                },
                "name": window.windowTitle(),
                "is_fullscreen": window.isFullScreen(),
                "widgets": self.save_widgets(window),
            }
        self.workspace = workspace_data

    def save_widgets(self, parent):
        widgets_data = {}
        for child in parent.children():
            if hasattr(child, "save_parameters"):
                widgets_data[child.objectName] = {
                    "class": type(child).__name__,
                    "objectname": child.objectName,
                    "geometry": {
                        "x": child.x(),
                        "y": child.y(),
                        "width": child.width(),
                        "height": child.height(),
                    },
                    "parameters": child.save_parameters(),
                    "children": self.save_widgets(child),
                }
        return widgets_data

    def load_workspace(self):
        if self.workspace:  # Prüfe, ob Fensterdaten vorhanden sind
            for window_data in self.workspace:
                self.restore_window(self.workspace[window_data])
        else:
            print("Keine Fenster in der Layout-Datei gefunden, starte mit Standardfenster.")
            self.create_default_window()
  
    def restore_window(self, window_data):
        window = MainWindow()
        self.windows.append(window)
        window.objectName = window_data["objectname"]
        geometry = window_data["geometry"]
        window.setGeometry(geometry["x"], geometry["y"], geometry["width"], geometry["height"])
        window.setWindowTitle(window_data["name"])
        if window_data["is_fullscreen"]:
            window.showFullScreen()
        else:
            window.show()

        self.restore_widgets(window, window_data["widgets"])

    def create_default_window(self):
        default_window = MainWindow()
        self.windows.append(default_window)
        default_window.objectName = str(uuid.uuid4())
        default_window.show()

    def restore_widgets(self, parent, widgets_data):
        # Mapping von Klassennamen zu den tatsächlichen Klassen
        widget_class_mapping = {
            "BaseWidget": BaseWidget,
            "CustomLabelWidget": CustomLabelWidget,
            "CustomButtonWidget": CustomButtonWidget,
            "CustomDataWidget": CustomDataWidget,
            # weitere Widget-Klassen hier hinzufügen
        }
        
        for item in widgets_data:
            widget_data = widgets_data[item]
            class_name = widget_data.get("class")
            widget_cls = widget_class_mapping.get(class_name)
            if widget_cls is None:
                continue  # Überspringe unbekannte Klassen
            
            widget = widget_cls()  # Instanziiere das Widget
            geometry = widget_data["geometry"]
            widget.objectName = widget_data["objectname"]
            widget.setGeometry(geometry["x"], geometry["y"], geometry["width"], geometry["height"])

            # Sicherstellen, dass ein Dictionary übergeben wird
            params = widget_data.get("parameters") or {}
            widget.restore_parameters(params)

            widget.setParent(parent)
            widget.show()
            self.restore_widgets(widget, widget_data["children"])

    def to_dict(self):
        return self.workspace
        # return {
        #     "layout": self.layout
        # }

    def update_from_dict(self, data):
        self.workspace = data
