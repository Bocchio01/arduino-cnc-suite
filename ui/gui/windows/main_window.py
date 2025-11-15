"""Main application window"""

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QMenuBar,
    QStatusBar,
    QMessageBox,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction

from core.config.settings import Settings
from ui.gui.windows.calibration_window import CalibrationWidget
from ui.gui.windows.image_print_window import ImagePrintWidget
from ui.gui.windows.text_print_window import TextPrintWidget


class MainWindow(QMainWindow):
    """Main application window with tabs for different functions"""

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.setup_ui()
        self.setup_menu()

    def setup_ui(self):
        """Setup the user interface"""
        self.setWindowTitle("Arduino CNC Suite")
        self.setMinimumSize(1000, 700)

        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Add tabs
        self.calibration_widget = CalibrationWidget(self.settings)
        self.tabs.addTab(self.calibration_widget, "Calibration")

        self.image_print_widget = ImagePrintWidget(self.settings)
        self.tabs.addTab(self.image_print_widget, "Print Image")

        self.text_print_widget = TextPrintWidget(self.settings)
        self.tabs.addTab(self.text_print_widget, "Print Text")

        # Status bar
        self.statusBar().showMessage("Ready")

    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open Image...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.image_print_widget.load_image)
        file_menu.addAction(open_action)

        save_gcode_action = QAction("&Save G-code...", self)
        save_gcode_action.setShortcut("Ctrl+S")
        save_gcode_action.triggered.connect(self.save_gcode)
        file_menu.addAction(save_gcode_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("&Tools")

        calibrate_action = QAction("&Calibration Wizard", self)
        calibrate_action.triggered.connect(self.show_calibration)
        tools_menu.addAction(calibrate_action)

        settings_action = QAction("&Settings", self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def save_gcode(self):
        """Save generated G-code"""
        current_widget = self.tabs.currentWidget()
        if hasattr(current_widget, "save_gcode"):
            current_widget.save_gcode()
        else:
            QMessageBox.information(
                self,
                "Save G-code",
                "Please generate G-code first by processing an image or text.",
            )

    def show_calibration(self):
        """Switch to calibration tab"""
        self.tabs.setCurrentWidget(self.calibration_widget)

    def show_settings(self):
        """Show settings dialog"""
        QMessageBox.information(
            self,
            "Settings",
            "Settings dialog not yet implemented.\n"
            "Edit config/default_settings.yaml directly.",
        )

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Arduino CNC Suite",
            "<h3>Arduino CNC Suite v2.0</h3>"
            "<p>Professional CNC plotter software with standard G-code support.</p>"
            "<p>Created by Tommaso Bocchietti</p>"
            "<p><a href='https://github.com/Bocchio01/Arduino_CNC_plotter'>"
            "GitHub Repository</a></p>",
        )
