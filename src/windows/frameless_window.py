from PySide6.QtWidgets import QApplication, QGraphicsView
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMouseEvent, QPainter, QColor

class FramelessWindow(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setRenderHint(QPainter.Antialiasing)

        self.setDragMode(QGraphicsView.NoDrag)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setMouseTracking(True)  # Für Resizing
        self.resize(800, 600)

        self._drag_active = False
        self._drag_pos = QPoint()
        self._resize_active = False
        self._resize_direction = None
        
        self.setMinimumSize(400, 300)  # Mindestgröße des Fensters

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # Prüfen, ob der Klick in den oberen 25 Pixeln liegt
            if event.pos().y() >= 5 and event.pos().y() <= 25:
                self._drag_active = True
                self._drag_pos = event.globalPosition().toPoint()
            elif self._resize_direction:  # Resizing starten
                self._resize_active = True

    def mouseMoveEvent(self, event: QMouseEvent):
        if self._drag_active:  # Fenster verschieben
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()
        elif self._resize_active:  # Fenstergröße ändern
            self.resize_window(event.globalPosition().toPoint())
        else:  # Resizing-Cursor ändern
            self.update_resize_direction(event.pos())

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_active = False
            self._resize_active = False

    def resize_window(self, global_pos):
        rect = self.geometry()
        if self._resize_direction == 'top':
            diff = global_pos.y() - rect.top()
            rect.setTop(rect.top() + diff)
        elif self._resize_direction == 'bottom':
            diff = global_pos.y() - rect.bottom()
            rect.setBottom(rect.bottom() + diff)
        elif self._resize_direction == 'left':
            diff = global_pos.x() - rect.left()
            rect.setLeft(rect.left() + diff)
        elif self._resize_direction == 'right':
            diff = global_pos.x() - rect.right()
            rect.setRight(rect.right() + diff)
        elif self._resize_direction == 'top-left':
            diff_x = global_pos.x() - rect.left()
            diff_y = global_pos.y() - rect.top()
            rect.setTop(rect.top() + diff_y)
            rect.setLeft(rect.left() + diff_x)
        elif self._resize_direction == 'top-right':
            diff_x = global_pos.x() - rect.right()
            diff_y = global_pos.y() - rect.top()
            rect.setTop(rect.top() + diff_y)
            rect.setRight(rect.right() + diff_x)
        elif self._resize_direction == 'bottom-left':
            diff_x = global_pos.x() - rect.left()
            diff_y = global_pos.y() - rect.bottom()
            rect.setBottom(rect.bottom() + diff_y)
            rect.setLeft(rect.left() + diff_x)
        elif self._resize_direction == 'bottom-right':
            diff_x = global_pos.x() - rect.right()
            diff_y = global_pos.y() - rect.bottom()
            rect.setBottom(rect.bottom() + diff_y)
            rect.setRight(rect.right() + diff_x)
        self.setGeometry(rect)

    def update_resize_direction(self, local_pos):
        margin = 5
        rect = self.rect()
        self._resize_direction = None
        if local_pos.y() < margin:
            if local_pos.x() < margin:
                self._resize_direction = 'top-left'
            elif local_pos.x() > rect.width() - margin:
                self._resize_direction = 'top-right'
            else:
                self._resize_direction = 'top'
        elif local_pos.y() > rect.height() - margin:
            if local_pos.x() < margin:
                self._resize_direction = 'bottom-left'
            elif local_pos.x() > rect.width() - margin:
                self._resize_direction = 'bottom-right'
            else:
                self._resize_direction = 'bottom'
        elif local_pos.x() < margin:
            self._resize_direction = 'left'
        elif local_pos.x() > rect.width() - margin:
            self._resize_direction = 'right'
        
        # Cursor anpassen
        if self._resize_direction in ['top', 'bottom']:
            self.setCursor(Qt.SizeVerCursor)
        elif self._resize_direction in ['left', 'right']:
            self.setCursor(Qt.SizeHorCursor)
        elif self._resize_direction in ['top-left', 'bottom-right']:
            self.setCursor(Qt.SizeFDiagCursor)
        elif self._resize_direction in ['top-right', 'bottom-left']:
            self.setCursor(Qt.SizeBDiagCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def paintEvent(self, event):
        # Fensterhintergrund zeichnen
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor("#0b0e14"))
        #painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())
