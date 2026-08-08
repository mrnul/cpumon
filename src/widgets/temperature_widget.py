from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from src.data.temperature_data import TemperatureData


class TemperatureWidget(QWidget):
    def __init__(self, data: TemperatureData):
        super().__init__()

        self.data = data

        self.name_label = QLabel(f"{self.data.label or '<No Label>'} - {self.data.name}")
        self.temp_label = QLabel(self._format_temp())

        self._layout = QVBoxLayout()
        self._layout.addWidget(self.name_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self.temp_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self._layout)

    def _format_temp(self) -> str:
        return f"{self.data.value:.2f} °C"

    def refresh_value(self):
        self.data.read_value()
        self.temp_label.setText(self._format_temp())