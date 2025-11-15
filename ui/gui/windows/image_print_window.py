"""Image printing window widget"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QPushButton,
    QLabel,
    QSlider,
    QComboBox,
    QFileDialog,
    QMessageBox,
    QProgressBar,
)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtGui import QPixmap, QImage
from pathlib import Path
import cv2
import numpy as np

from core.config.settings import Settings
from core.image_processing.vectorizer import ImageVectorizer
from core.image_processing.path_planner import PathPlanner
from core.gcode.generator import GCodeGenerator
from core.communication.gcode_sender import GCodeSender


class ImagePrintWidget(QWidget):
    """Widget for image processing and printing"""

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.image_path = None
        self.processed_image = None
        self.gcode = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface"""
        layout = QHBoxLayout(self)

        # Left panel - controls
        left_panel = QVBoxLayout()

        # Image loading
        load_group = QGroupBox("Image")
        load_layout = QVBoxLayout()

        self.load_btn = QPushButton("Load Image")
        self.load_btn.clicked.connect(self.load_image)
        load_layout.addWidget(self.load_btn)

        self.image_label = QLabel("No image loaded")
        self.image_label.setAlignment(Qt.AlignCenter)
        load_layout.addWidget(self.image_label)

        load_group.setLayout(load_layout)
        left_panel.addWidget(load_group)

        # Processing options
        options_group = QGroupBox("Processing Options")
        options_layout = QVBoxLayout()

        # Mode selection
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Edge Detection", "Fill"])
        self.mode_combo.currentIndexChanged.connect(self.update_preview)
        mode_layout.addWidget(self.mode_combo)
        options_layout.addLayout(mode_layout)

        # Quality slider
        quality_layout = QVBoxLayout()
        quality_layout.addWidget(QLabel("Quality:"))
        self.quality_slider = QSlider(Qt.Horizontal)
        self.quality_slider.setRange(1, 255)
        self.quality_slider.setValue(100)
        self.quality_slider.valueChanged.connect(self.update_preview)
        quality_layout.addWidget(self.quality_slider)

        self.quality_label = QLabel("100")
        self.quality_slider.valueChanged.connect(
            lambda v: self.quality_label.setText(str(v))
        )
        quality_layout.addWidget(self.quality_label)
        options_layout.addLayout(quality_layout)

        # Process button
        self.process_btn = QPushButton("Generate G-code")
        self.process_btn.clicked.connect(self.generate_gcode)
        self.process_btn.setEnabled(False)
        options_layout.addWidget(self.process_btn)

        options_group.setLayout(options_layout)
        left_panel.addWidget(options_group)

        # Print controls
        print_group = QGroupBox("Print")
        print_layout = QVBoxLayout()

        self.print_btn = QPushButton("Print")
        self.print_btn.clicked.connect(self.print_image)
        self.print_btn.setEnabled(False)
        print_layout.addWidget(self.print_btn)

        self.progress_bar = QProgressBar()
        print_layout.addWidget(self.progress_bar)

        print_group.setLayout(print_layout)
        left_panel.addWidget(print_group)

        left_panel.addStretch()

        # Right panel - preview
        right_panel = QVBoxLayout()

        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()

        self.preview_label = QLabel("Load an image to see preview")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(500, 500)
        self.preview_label.setStyleSheet("border: 1px solid gray;")
        preview_layout.addWidget(self.preview_label)

        preview_group.setLayout(preview_layout)
        right_panel.addWidget(preview_group)

        # Add panels to main layout
        layout.addLayout(left_panel, 1)
        layout.addLayout(right_panel, 2)

    def load_image(self):
        """Load an image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )

        if file_path:
            self.image_path = file_path
            self.image_label.setText(Path(file_path).name)
            self.process_btn.setEnabled(True)
            self.update_preview()

    def update_preview(self):
        """Update the preview image"""
        if not self.image_path:
            return

        try:
            vectorizer = ImageVectorizer()
            img = vectorizer.load_image(self.image_path)

            mode = "edge" if self.mode_combo.currentIndex() == 0 else "fill"
            quality = self.quality_slider.value()

            if mode == "edge":
                processed = vectorizer.edge_detection(img, quality, quality)
            else:
                processed = vectorizer.threshold_image(img, quality // 2)

            # Resize for display
            height, width = processed.shape[:2]
            if height > 500 or width > 500:
                scale = min(500 / height, 500 / width)
                new_size = (int(width * scale), int(height * scale))
                processed = cv2.resize(processed, new_size)

            # Convert to QPixmap
            if len(processed.shape) == 2:
                # Grayscale
                h, w = processed.shape
                qimg = QImage(processed.data, w, h, w, QImage.Format_Grayscale8)
            else:
                # Color
                h, w, ch = processed.shape
                bytes_per_line = ch * w
                qimg = QImage(
                    processed.data, w, h, bytes_per_line, QImage.Format_RGB888
                )

            pixmap = QPixmap.fromImage(qimg)
            self.preview_label.setPixmap(pixmap)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process image: {e}")

    def generate_gcode(self):
        """Generate G-code from image"""
        if not self.image_path:
            return

        try:
            mode = "edge" if self.mode_combo.currentIndex() == 0 else "fill"
            quality = self.quality_slider.value()
            work_area = (
                self.settings.calibration.max_x,
                self.settings.calibration.max_y,
            )

            # Process image
            vectorizer = ImageVectorizer(target_size=work_area)
            paths, img_size = vectorizer.process_image(
                self.image_path, mode=mode, quality=quality
            )

            # Plan paths
            planner = PathPlanner()
            optimized_paths = planner.plan_from_image(paths, img_size, work_area)

            # Generate G-code
            generator = GCodeGenerator(
                feed_rate=self.settings.calibration.default_speed,
                rapid_rate=self.settings.calibration.rapid_speed,
            )
            generator.header()

            for path in optimized_paths:
                generator.draw_polyline(path)

            generator.footer()

            self.gcode = generator.get_gcode()
            self.print_btn.setEnabled(True)

            QMessageBox.information(
                self,
                "Success",
                f"G-code generated successfully!\n{len(self.gcode)} commands",
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate G-code: {e}")

    def print_image(self):
        """Print the generated G-code"""
        if not self.gcode:
            QMessageBox.warning(self, "Error", "No G-code generated")
            return

        # Connect and print
        port = self.settings.serial.port
        sender = GCodeSender(port, self.settings.serial.baudrate)

        if not sender.connect():
            QMessageBox.critical(self, "Error", "Failed to connect to plotter")
            return

        self.progress_bar.setValue(0)

        def update_progress(current, total):
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)

        success = sender.stream_gcode(self.gcode, progress_callback=update_progress)
        sender.disconnect()

        if success:
            QMessageBox.information(self, "Success", "Print completed!")
        else:
            QMessageBox.critical(self, "Error", "Print failed")

    def save_gcode(self):
        """Save G-code to file"""
        if not self.gcode:
            QMessageBox.warning(self, "Error", "No G-code generated")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save G-code", "", "G-code Files (*.gcode *.nc);;All Files (*)"
        )

        if file_path:
            with open(file_path, "w") as f:
                f.write("\n".join(self.gcode))
            QMessageBox.information(self, "Success", f"G-code saved to {file_path}")
