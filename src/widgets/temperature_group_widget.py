from PySide6.QtWidgets import QGroupBox, QHBoxLayout

from src.data.temperature_data import TemperatureData
from src.widgets.temperature_widget import TemperatureWidget


class TemperatureGroupWidget(QGroupBox):
    def __init__(self, title: str, bases: list[str]):
        super().__init__(title)

        self.widgets: list[TemperatureWidget] = []

        layout = QHBoxLayout()

        for item in bases:
            widget = TemperatureWidget(TemperatureData(item))
            self.widgets.append(widget)
            layout.addWidget(widget)
        self.setLayout(layout)

    def refresh(self):
        for item in self.widgets:
            item.refresh_value()