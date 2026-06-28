from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from src.data.temperature_data import TemperatureData


class TemperatureWidget(QWidget):
    def __init__(self, data: TemperatureData):
        super().__init__()

        self.data = data

        self.name_label = QLabel(self.data.name)
        self.temp_label = QLabel(self._format_temp())
        self.label_label = QLabel(self.data.label or "<No label>")

        self._layout = QVBoxLayout()
        self._layout.addWidget(self.name_label)
        self._layout.addWidget(self.temp_label)
        self._layout.addWidget(self.label_label)
        self.setLayout(self._layout)

    def _format_temp(self) -> str:
        return f"{self.data.value:.2f} °C"

    def refresh_value(self):
        self.data.read_value()
        self.temp_label.setText(self._format_temp())