"""Text printing window widget"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QPushButton,
    QLabel,
    QTextEdit,
    QFontComboBox,
    QSpinBox,
    QComboBox,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from core.config.settings import Settings
from core.gcode.generator import GCodeGenerator


class TextPrintWidget(QWidget):
    """Widget for text to G-code conversion"""

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.gcode = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)

        # Text input
        input_group = QGroupBox("Text Input")
        input_layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Enter text to print...")
        self.text_edit.setMaximumHeight(100)
        input_layout.addWidget(self.text_edit)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # Text options
        options_group = QGroupBox("Text Options")
        options_layout = QVBoxLayout()

        # Font selection
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font:"))
        self.font_combo = QFontComboBox()
        font_layout.addWidget(self.font_combo)
        options_layout.addLayout(font_layout)

        # Font size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Size:"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 200)
        self.size_spin.setValue(30)
        size_layout.addWidget(self.size_spin)
        size_layout.addStretch()
        options_layout.addLayout(size_layout)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Generate button
        self.generate_btn = QPushButton("Generate G-code")
        self.generate_btn.clicked.connect(self.generate_gcode)
        layout.addWidget(self.generate_btn)

        layout.addStretch()

        # Note
        note_label = QLabel(
            "Note: Text printing generates bitmap outlines.\n"
            "For best results, use simple fonts and avoid very small sizes."
        )
        note_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(note_label)

    def generate_gcode(self):
        """Generate G-code from text"""
        text = self.text_edit.toPlainText()

        if not text:
            QMessageBox.warning(self, "Error", "Please enter some text")
            return

        try:
            # Placeholder - text to G-code conversion
            # This would need proper implementation
            QMessageBox.information(
                self,
                "Text to G-code",
                "Text to G-code conversion is not yet fully implemented.\n"
                "This feature is coming soon!",
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate G-code: {e}")
