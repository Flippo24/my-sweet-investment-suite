import uuid
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QMessageBox, QMenu, QInputDialog,QGraphicsView, QGraphicsScene
from PySide6.QtCore import Qt, Signal, Slot, Property
from PySide6.QtGui import QCursor, QPen, QColor, QPainter, QPixmap, QFont

from qframelesswindow import FramelessWindow

from widgets.base_widget import BaseWidget
from widgets.custom_label_widget import CustomLabelWidget
from widgets.custom_button_widget import CustomButtonWidget
from widgets.custom_tab_widget import CustomTabWidget
from widgets.custom_data_widget import CustomDataWidget
#import widgets
from services.themes.theme_list_window import ThemeListWindow
from services.themes.theme import AppState

import asyncio

class MainWindow(FramelessWindow):
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        self.settings = self.app.settings
        self.theme = self.app.theme
        self.workspace = self.app.settings.workspace

        self.titleBar.closeBtn.hide()
        self.titleBar.minBtn.hide()
        self.titleBar.maxBtn.hide()
        self.setWindowTitle("My sweet Investment Suite")
        self.setGeometry(100, 100, 600, 400)
        self.fullscreen = False

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)


    def paintWatermark(self):
        # Painter für das Wasserzeichen initialisieren
        Painter = QPainter(self)
        Painter.setRenderHint(QPainter.TextAntialiasing)

        # Stil für das Wasserzeichen definieren
        #Painter.setPen(QColor(150, 150, 150, 100))  # Grauer Text mit Transparenz
        Painter.setPen(self.palette().color(self.backgroundRole()).lighter(200))
        #Painter.setFont(QFont("Arial", 14, QFont.Normal))
        Painter.setFont(self.theme.custom_font)
        
        # Wasserzeichen-Text
        text1 = "My Sweet Investment Suite"
        text2 = "Smart Tools, Sweet Returns."

        # Position unten links berechnen
        margin = 25  # Abstand vom Rand
        text_width1 = Painter.fontMetrics().horizontalAdvance(text1)
        text_width2 = Painter.fontMetrics().horizontalAdvance(text2)
        text_height = Painter.fontMetrics().height()

        # Koordinaten
        x1 = margin
        y1 = self.height() - (2 * text_height)  # Erste Zeile
        x2 = margin
        y2 = self.height() - text_height  # Zweite Zeile

        # Wasserzeichen zeichnen
        Painter.drawText(x1, y1, text1)
        Painter.drawText(x2, y2, text2)
        
        Painter.end()

    def paintGrid(self):
        self.paintWatermark()

        """Zeichnet das Gitternetz nur im EditMode."""
        #if self.edit_mode:
        if self.app.property("appState") == "Edit":
            painter = QPainter(self)
            grid_size = 20
            #grid_color = QColor("#11151c")
            grid_color = self.palette().color(self.backgroundRole()).lighter(170)

            for x in range(0, self.width(), grid_size):
                painter.setPen(grid_color)
                painter.drawLine(x, 0, x, self.height())

            for y in range(0, self.height(), grid_size):
                painter.setPen(grid_color)
                painter.drawLine(0, y, self.width(), y)

            painter.end()

    def paintEvent(self, event):
        self.paintWatermark()
        self.paintGrid()

    def resizeEvent(self, event):
        """Update the grid and resize the graphics view when the window is resized."""
        super().resizeEvent(event)

    def closeEvent(self, event):
        # Prüfe, ob das Programm bereits im Beenden-Modus ist
        if self.app.is_closing_all:
            event.accept()
            return

        dialog = QMessageBox(self)
        dialog.setWindowTitle("Schließen")
        dialog.setText("Möchten Sie dieses Fenster schließen, das Programm beenden oder abbrechen?")
        dialog.setStandardButtons(
            QMessageBox.Close | QMessageBox.Cancel | QMessageBox.Yes
        )
        dialog.setButtonText(QMessageBox.Close, "Fenster schließen")
        dialog.setButtonText(QMessageBox.Yes, "Programm beenden")
        dialog.setButtonText(QMessageBox.Cancel, "Abbrechen")

        result = dialog.exec()

        if result == QMessageBox.Close:
            self.close_window()
            # if len(app.windows) > 1:
            #     app.windows.remove(self)
            if not self.workspace.windows:
                event.accept()
                #app.quit()  # Beende die Anwendung, wenn kein Fenster mehr übrig ist
            event.ignore()
        elif result == QMessageBox.Yes:
            # Markiere, dass das Programm beendet wird
            self.app.is_closing_all = True
            #self.app.quit()
            self.close_app()

        event.ignore()

    def close_window(self):
        if len(self.workspace.windows) > 1:
            self.hide()
            self.workspace.windows.remove(self)
            self.deleteLater()
        #self.close_app()

    def close_app(self):
        self.app.is_closing_all = True
        self.app.close_app()

    def open_context_menu(self, pos):
        mouse_pos = self.mapFromGlobal(QCursor.pos())
        target_widget = self.childAt(mouse_pos)
        menu = QMenu(self)

        # Bearbeitungsmodus umschalten
        if self.app.property("appState") == "Production":
            setEditModeAction = menu.addAction(
                "Bearbeitungsmodus aktivieren"
            )
        elif self.app.property("appState") == "Edit":
            setProductionModeAction = menu.addAction(
                "Bearbeitungsmodus deaktivieren"
            )

        # Widgets hinzufügen, nur im Bearbeitungsmodus
        if self.app.property("appState") == "Edit":
            add_widget_menu = menu.addMenu("Widget hinzufügen")
            add_resizable_action = add_widget_menu.addAction("Tab Widget")
            add_label_action = add_widget_menu.addAction("Label Widget")
            add_button_action = add_widget_menu.addAction("Button Widget")
            add_data_action = add_widget_menu.addAction("Data Widget")
            remove_action = menu.addAction("Widget entfernen")
            add_window_action = menu.addAction("Neues Fenster")
            rename_title_action = menu.addAction("Fenstertitel ändern")
            themes_action = menu.addAction("Themes...")

            # Vollbild umschalten
            fullscreen_action = menu.addAction(
                "Vollbild aktivieren" if not self.fullscreen else "Vollbild deaktivieren"
            )

            # Submenu: Layout
            layout_menu = menu.addMenu("Layout")
            layout_dummy1_action = layout_menu.addAction("Dummy1")
            layout_dummy2_action = layout_menu.addAction("Dummy2")
        else:
            # Submenu: Schließen
            close_menu = menu.addMenu("Schließen")
            close_window_action = close_menu.addAction("Fenster schließen")
            close_program_action = close_menu.addAction("Programm beenden")


        # Zeige das Kontextmenü und führe die ausgewählte Aktion aus
        action = menu.exec(QCursor.pos())

        if self.app.property("appState") == "Production" and action == setEditModeAction:
            self.app.theme.setMode("Edit")
            return

        if self.app.property("appState") == "Edit" and action == setProductionModeAction:
            self.app.theme.setMode("Production")
            return

        #if self.settings.edit_mode:
        if self.app.property("appState") == "Edit":
            if action == add_resizable_action:
                widget = CustomTabWidget("Tab Widget")
                # widget.move(pos)
                # widget.setParent(self)
                # widget.show()
            elif action == add_label_action:
                widget = CustomLabelWidget("Label Widget")
                # widget.move(pos)
                # widget.setParent(self)
                # widget.show()
            elif action == add_button_action:
                widget = CustomButtonWidget("Button Widget")
                # widget.move(pos)
                # widget.setParent(self)
                # widget.show()
            elif action == add_data_action:
                widget = CustomDataWidget()

            elif action == remove_action:
                for child in self.children():
                    if isinstance(child, BaseWidget):
                        widget_rect = child.geometry()
                        if widget_rect.contains(mouse_pos):
                            child.deleteLater()
                            break
                return
            elif action == add_window_action:
                self.add_new_window()
                return
            elif action == rename_title_action:
                self.rename_window_title()
                return
            elif action == themes_action:
                self.theme_window = ThemeListWindow()
                self.theme_window.show()
                return
            elif action == fullscreen_action:
                self.toggle_fullscreen()
                return
            elif action == layout_dummy1_action:
                print("Layout Dummy1 ausgewählt")
                return
            elif action == layout_dummy2_action:
                print("Layout Dummy2 ausgewählt")
                return
            
            # Position setzen und anzeigen
            widget.setParent(self)
            widget.move(mouse_pos)
           
            widget.objectName = str(uuid.uuid4())
            widget.show()

        #elif not self.settings.edit_mode:
        elif not self.app.property("appState") == "Edit":
            if action == close_program_action:
                self.close_app()
            elif action == close_window_action:
                self.close_window()

    def toggle_fullscreen(self):
        # self.titleBar._TitleBarBase__toggleMaxState()
        # pass
        if not self.fullscreen:
            self.showFullScreen()
        else:
            self.showNormal()
        self.fullscreen = not self.fullscreen

    def keyPressEvent(self, event):
        # Vollbild mit ESC beenden
        if event.key() == Qt.Key_Escape and self.fullscreen:
            self.toggle_fullscreen()
            
    def add_new_window(self):
        new_window = MainWindow()
        self.workspace.windows.append(new_window)
        new_window.objectName = str(uuid.uuid4())
        new_window.show()

    def rename_window_title(self):
        """
        Öffnet einen Dialog, um den Fenstertitel umzubenennen.
        """
        new_title, ok = QInputDialog.getText(self, "Fenstertitel ändern", "Neuer Titel:")
        if ok and new_title:
            self.setWindowTitle(new_title)