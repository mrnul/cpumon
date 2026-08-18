from PySide6.QtGui import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from src.data.fan_data import FanData


class FanWidget(QWidget):
    def __init__(self, data: FanData):
        super().__init__()

        self.data = data

        self.name_label = QLabel(f"{self.data.name}")
        self.temp_label = QLabel(self._format_rmp())

        self._layout = QVBoxLayout()
        self._layout.addWidget(self.name_label, alignment=Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self.temp_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(self._layout)

    def _format_rmp(self) -> str:
        return f"{self.data.value} rpm"

    def refresh_value(self):
        self.data.read_value()
        self.temp_label.setText(self._format_rmp())