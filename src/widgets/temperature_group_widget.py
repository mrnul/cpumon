from PySide6.QtWidgets import QGroupBox, QGridLayout

from src.data.temperature_data import TemperatureData
from src.widgets.temperature_widget import TemperatureWidget


class TemperatureGroupWidget(QGroupBox):
    def __init__(self, title: str, bases: list[str]):
        super().__init__(title)

        self._widgets: list[TemperatureWidget] = [TemperatureWidget(TemperatureData(item)) for item in bases]

        layout = QGridLayout()

        per_row: int = 8
        for index, cpu_widget in enumerate(self._widgets):
            row, column = divmod(index, per_row)
            layout.addWidget(cpu_widget, row, column)
        self.setLayout(layout)

    def refresh(self):
        for item in self._widgets:
            item.refresh_value()