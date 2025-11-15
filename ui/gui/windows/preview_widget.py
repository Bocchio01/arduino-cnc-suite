"""Preview widget for G-code visualization"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QPen, QColor
from typing import List, Tuple


class PreviewWidget(QWidget):
    """Widget for visualizing G-code paths"""

    def __init__(self):
        super().__init__()
        self.paths = []
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0

        self.setMinimumSize(500, 500)
        self.setStyleSheet("background-color: white;")

    def set_paths(self, paths: List[List[Tuple[float, float]]]):
        """Set paths to display"""
        self.paths = paths
        self.calculate_scale()
        self.update()

    def calculate_scale(self):
        """Calculate scale to fit paths in widget"""
        if not self.paths:
            return

        # Find bounds
        all_x = []
        all_y = []
        for path in self.paths:
            for x, y in path:
                all_x.append(x)
                all_y.append(y)

        if not all_x:
            return

        min_x, max_x = min(all_x), max(all_x)
        min_y, max_y = min(all_y), max(all_y)

        width = max_x - min_x
        height = max_y - min_y

        # Calculate scale with margin
        margin = 50
        scale_x = (self.width() - 2 * margin) / width if width > 0 else 1
        scale_y = (self.height() - 2 * margin) / height if height > 0 else 1

        self.scale = min(scale_x, scale_y)
        self.offset_x = margin - min_x * self.scale
        self.offset_y = margin - min_y * self.scale

    def paintEvent(self, event):
        """Paint the paths"""
        if not self.paths:
            return
