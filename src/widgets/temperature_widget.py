from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout

from src.data.temperature_data import TemperatureData


class TemperatureWidget(QWidget):
    def __init__(self, data: TemperatureData):
        super().__init__()

        self.data: TemperatureData = data

        self.name_label: QLabel = QLabel(f"{self.data.label or '<No Label>'} - {self.data.name}:")
        self.temp_label: QLabel = QLabel(self._format_temp())

        self._layout: QHBoxLayout = QHBoxLayout()
        self._layout.addWidget(self.name_label)
        self._layout.addWidget(self.temp_label)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)

    def _format_temp(self) -> str:
        if not self.data.value:
            return "<No Data>"
        return f"{self.data.value:.2f} °C"

    def refresh_value(self) -> None:
        self.data.read_value()
        self.temp_label.setText(self._format_temp())