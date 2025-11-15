"""Calibration window widget"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QPushButton,
    QLabel,
    QSpinBox,
    QComboBox,
    QMessageBox,
    QTextEdit,
)
from PySide6.QtCore import Qt, Signal, QThread

from core.config.settings import Settings
from core.communication.gcode_sender import GCodeSender
from core.communication.serial_manager import SerialManager
from core.calibration.calibrator import Calibrator


class CalibrationWidget(QWidget):
    """Widget for plotter calibration"""

    status_message = Signal(str)

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.sender = None
        self.calibrator = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout(self)

        # Connection group
        connection_group = QGroupBox("Connection")
        connection_layout = QHBoxLayout()

        self.port_combo = QComboBox()
        self.refresh_ports()
        connection_layout.addWidget(QLabel("Port:"))
        connection_layout.addWidget(self.port_combo)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        connection_layout.addWidget(self.refresh_btn)

        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.toggle_connection)
        connection_layout.addWidget(self.connect_btn)

        connection_layout.addStretch()
        connection_group.setLayout(connection_layout)
        layout.addWidget(connection_group)

        # Servo calibration group
        servo_group = QGroupBox("Pen Servo Calibration")
        servo_layout = QVBoxLayout()

        angles_layout = QHBoxLayout()
        angles_layout.addWidget(QLabel("Pen Up Angle:"))
        self.pen_up_spin = QSpinBox()
        self.pen_up_spin.setRange(0, 180)
        self.pen_up_spin.setValue(self.settings.calibration.pen_up_angle)
        angles_layout.addWidget(self.pen_up_spin)

        angles_layout.addWidget(QLabel("Pen Down Angle:"))
        self.pen_down_spin = QSpinBox()
        self.pen_down_spin.setRange(0, 180)
        self.pen_down_spin.setValue(self.settings.calibration.pen_down_angle)
        angles_layout.addWidget(self.pen_down_spin)

        self.test_servo_btn = QPushButton("Test Servo")
        self.test_servo_btn.clicked.connect(self.test_servo)
        self.test_servo_btn.setEnabled(False)
        angles_layout.addWidget(self.test_servo_btn)
        angles_layout.addStretch()

        servo_layout.addLayout(angles_layout)
        servo_group.setLayout(servo_layout)
        layout.addWidget(servo_group)

        # Movement test group
        movement_group = QGroupBox("Movement Test")
        movement_layout = QHBoxLayout()

        self.test_movement_btn = QPushButton("Test Axes")
        self.test_movement_btn.clicked.connect(self.test_movement)
        self.test_movement_btn.setEnabled(False)
        movement_layout.addWidget(self.test_movement_btn)

        self.test_pattern_btn = QPushButton("Draw Test Pattern")
        self.test_pattern_btn.clicked.connect(self.draw_test_pattern)
        self.test_pattern_btn.setEnabled(False)
        movement_layout.addWidget(self.test_pattern_btn)

        movement_layout.addStretch()
        movement_group.setLayout(movement_layout)
        layout.addWidget(movement_group)

        # Status log
        log_group = QGroupBox("Status Log")
        log_layout = QVBoxLayout()

        self.status_log = QTextEdit()
        self.status_log.setReadOnly(True)
        self.status_log.setMaximumHeight(150)
        log_layout.addWidget(self.status_log)

        log_group.setLayout(log_layout)
        layout.addWidget(log_group)

        # Connect status signal
        self.status_message.connect(self.append_status)

        layout.addStretch()

    def refresh_ports(self):
        """Refresh available serial ports"""
        self.port_combo.clear()
        ports = SerialManager.list_ports()
        for port in ports:
            self.port_combo.addItem(str(port), port.device)

    def toggle_connection(self):
        """Connect or disconnect from plotter"""
        if self.sender and self.sender.is_connected:
            self.disconnect_plotter()
        else:
            self.connect_plotter()

    def connect_plotter(self):
        """Connect to the plotter"""
        port = self.port_combo.currentData()
        if not port:
            QMessageBox.warning(self, "Error", "No port selected")
            return

        self.status_message.emit(f"Connecting to {port}...")

        self.sender = GCodeSender(port, self.settings.serial.baudrate)

        if self.sender.connect():
            self.calibrator = Calibrator(self.sender, self.settings.calibration)
            self.status_message.emit("Connected successfully!")
            self.connect_btn.setText("Disconnect")
            self.test_servo_btn.setEnabled(True)
            self.test_movement_btn.setEnabled(True)
            self.test_pattern_btn.setEnabled(True)
        else:
            self.status_message.emit("Connection failed!")
            QMessageBox.critical(
                self, "Connection Error", "Failed to connect to plotter"
            )

    def disconnect_plotter(self):
        """Disconnect from the plotter"""
        if self.sender:
            self.sender.disconnect()
            self.status_message.emit("Disconnected")
            self.connect_btn.setText("Connect")
            self.test_servo_btn.setEnabled(False)
            self.test_movement_btn.setEnabled(False)
            self.test_pattern_btn.setEnabled(False)

    def test_servo(self):
        """Test pen servo angles"""
        if not self.calibrator:
            return

        up_angle = self.pen_up_spin.value()
        down_angle = self.pen_down_spin.value()

        self.calibrator.test_pen_servo(
            up_angle, down_angle, callback=self.status_message.emit
        )

    def test_movement(self):
        """Test axis movement"""
        if not self.calibrator:
            return

        self.calibrator.test_movement(distance=50, callback=self.status_message.emit)

    def draw_test_pattern(self):
        """Draw a test pattern"""
        if not self.calibrator:
            return

        self.calibrator.draw_test_pattern(size=50, callback=self.status_message.emit)

    def append_status(self, message: str):
        """Append message to status log"""
        self.status_log.append(message)
