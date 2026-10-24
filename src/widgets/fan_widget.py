from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout

from src.data.fan_data import FanData


class FanWidget(QWidget):
    def __init__(self, data: FanData):
        super().__init__()

        self.data: FanData = data

        self.name_label: QLabel = QLabel(f"{self.data.name}:")
        self.temp_label: QLabel = QLabel(self._format_rmp())

        self._layout: QHBoxLayout = QHBoxLayout()
        self._layout.addWidget(self.name_label)
        self._layout.addWidget(self.temp_label)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)

    def _format_rmp(self) -> str:
        if not self.data.value:
            return "<No Data>"
        return f"{self.data.value} rpm"

    def refresh_value(self) -> None:
        self.data.read_value()
        self.temp_label.setText(self._format_rmp())