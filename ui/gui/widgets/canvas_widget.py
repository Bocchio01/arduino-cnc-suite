"""Canvas widget for freehand drawing"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QPainter, QPen, QPixmap, QColor


class CanvasWidget(QWidget):
    """Widget for freehand drawing"""

    drawing_finished = Signal()

    def __init__(self):
        super().__init__()
        self.drawing = False
        self.last_point = QPoint()
        self.image = QPixmap(500, 500)
        self.image.fill(Qt.white)

        self.pen_color = QColor(0, 0, 0)
        self.pen_width = 2

        self.setMinimumSize(500, 500)
        self.setMaximumSize(500, 500)

    def clear_canvas(self):
        """Clear the canvas"""
        self.image.fill(Qt.white)
        self.update()

    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        """Handle mouse move"""
        if event.buttons() & Qt.LeftButton and self.drawing:
            painter = QPainter(self.image)
            painter.setPen(
                QPen(
                    self.pen_color,
                    self.pen_width,
                    Qt.SolidLine,
                    Qt.RoundCap,
                    Qt.RoundJoin,
                )
            )
            painter.drawLine(self.last_point, event.pos())
            self.last_point = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.drawing_finished.emit()

    def paintEvent(self, event):
        """Paint the widget"""
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.image)

    def get_image(self):
        """Get the current image"""
        return self.image.toImage()
