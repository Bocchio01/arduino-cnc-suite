"""Main GUI application entry point"""

import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from ui.gui.windows.main_window import MainWindow
from core.config.settings import Settings


def main():
    """Launch the GUI application"""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Arduino CNC Suite")
    app.setOrganizationName("Tommaso Bocchietti")

    # Load settings
    config_path = Path("config/default_settings.yaml")
    settings = Settings.load(config_path)

    # Create and show main window
    window = MainWindow(settings)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
