from PySide6.QtCore import QSize, QPoint, Slot
from PySide6.QtGui import Qt
from PySide6.QtWidgets import QApplication, QWidget, QFrame

class BaseWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.app = QApplication.instance()
        self.settings = self.app.settings
        self.setGeometry(50, 50, 150, 300)
        self.setMinimumSize(50, 50)
        self.dragging = False
        self.resizing = False
        self.resize_handle_size = 10
        self.setMouseTracking(True)

        # Standard-Properties setzen
        self.setProperty("hover", False)

    def enterEvent(self, event):
        """Aktualisiert die 'hover'-Property, wenn die Maus über das Widget fährt."""
        self.setProperty("hover", True)
        self.style().unpolish(self)
        self.style().polish(self)
        super().enterEvent(event)

    def leaveEvent(self, event):
        """Setzt die 'hover'-Property zurück, wenn die Maus das Widget verlässt."""
        self.setProperty("hover", False)
        self.style().unpolish(self)
        self.style().polish(self)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.app.property("appState") == "Edit":
            if self.is_in_resize_handle(event.position().toPoint()):
                self.resizing = True
                self.resize_start_pos = event.globalPosition().toPoint()
                self.start_size = self.size()
            else:
                self.dragging = True
                self.offset = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if self.app.property("appState") == "Edit":
            if self.resizing:
                delta = event.globalPosition().toPoint() - self.resize_start_pos
                new_width = self.start_size.width() + delta.x()
                new_height = self.start_size.height() + delta.y()
                self.resize(self.snap_to_grid(QSize(new_width, new_height)))
            elif self.dragging:
                new_pos = self.mapToParent(event.position().toPoint() - self.offset)
                self.move(self.snap_to_grid(new_pos))
            else:
                if self.is_in_resize_handle(event.position().toPoint()):
                    self.setCursor(Qt.SizeFDiagCursor)
                else:
                    self.setCursor(Qt.OpenHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.resizing = False
            self.setCursor(Qt.ArrowCursor)
    
    def is_in_resize_handle(self, pos):
        return (self.width() - self.resize_handle_size <= pos.x() <= self.width() and
                self.height() - self.resize_handle_size <= pos.y() <= self.height())

    def snap_to_grid(self, value):
        grid_size = 5
        tolerance = 2

        def snap_dimension(dimension):
            remainder = dimension % grid_size
            if remainder <= tolerance:
                return dimension - remainder
            elif remainder >= grid_size - tolerance:
                return dimension + (grid_size - remainder)
            return dimension

        if isinstance(value, QPoint):
            return QPoint(snap_dimension(value.x()), snap_dimension(value.y()))
        elif isinstance(value, QSize):
            return QSize(snap_dimension(max(value.width(), self.minimumWidth())),
                         snap_dimension(max(value.height(), self.minimumHeight())))

        return value

    def save_parameters(self):
        # Standardimplementierung: Keine Parameter
        return {}

    def restore_parameters(self, params):
        # Standardimplementierung: Nichts tun
        pass


