from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPointF, QLineF
from PySide6.QtGui import QPainter, QPen, QPainterPath

class Connection(QWidget):
    def __init__(self, widget1, widget2, parent=None):
        super().__init__(parent)
        self.source_widget = source_widget
        self.target_widget = target_widget
        #self.setFixedSize(parent.width(), parent.height())
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setMouseTracking(True)
        #self.setCursor(Qt.PointingHandCursor)

        self.arrow = QPolygonF()
        self.update_position()
        self.hide()

    def update_position(self):
        source_center = self.source_widget.sceneBoundingRect().center()
        target_center = self.target_widget.sceneBoundingRect().center()
        line = QLineF(source_center, target_center)
        
        # Setze die Hauptlinie
        self.setLine(line)
        
        # Berechne den Winkel für die Pfeilspitze
        angle = math.atan2(line.dy(), line.dx())
        arrow_size = 10
        
        # Berechne die Pfeilspitzenpunkte
        arrow_p1 = target_center - QPointF(
            math.cos(angle - math.pi/6) * arrow_size,
            math.sin(angle - math.pi/6) * arrow_size
        )
        arrow_p2 = target_center - QPointF(
            math.cos(angle + math.pi/6) * arrow_size,
            math.sin(angle + math.pi/6) * arrow_size
        )
        
        self.arrow.clear()
        self.arrow.append(target_center)
        self.arrow.append(arrow_p1)
        self.arrow.append(arrow_p2)

    def show_connection(self):
        self.show()

    def hide_connection(self):
        self.hide()

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        painter.setBrush(Qt.red)
        painter.drawPolygon(self.arrow)

    def mouseDoubleClickEvent(self, event):
        self.source_widget.outgoing_connections.remove(self)
        self.target_widget.incoming_connections.remove(self)
        self.source_widget.connected_widgets.remove(self.target_widget)
        self.scene().removeItem(self)


    # def get_line(self):
    #     # Berechne die Linie zwischen den Zentren der beiden Widgets
    #     w1_center = self.widget1.geometry().center()
    #     w2_center = self.widget2.geometry().center()
    #     return QLineF(w1_center, w2_center)

    # def paintEvent(self, event):
    #     # Linie zeichnen
    #     painter = QPainter(self)
    #     pen = QPen(Qt.black, 3)
    #     painter.setPen(pen)
    #     line = self.get_line()
    #     painter.drawLine(line)

    # def mousePressEvent(self, event):
    #     # Prüfen, ob der Klick in der Nähe der Linie liegt
    #     line = self.get_line()
    #     path = QPainterPath()
    #     path.moveTo(line.p1())
    #     path.lineTo(line.p2())
    #     click_tolerance = 5  # Erweitere den Trefferbereich
    #     if path.contains(event.pos()):
    #         print("Connection clicked!")
    #         event.accept()
    #     else:
    #         event.ignore()

    # def mouseDoubleClickEvent(self, event):
    #     print("Connection double-clicked!")
    #     self.deleteLater()