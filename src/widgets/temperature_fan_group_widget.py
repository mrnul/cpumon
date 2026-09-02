from PySide6.QtWidgets import QGroupBox, QGridLayout, QVBoxLayout, QFrame

from src.data.fan_data import FanData
from src.data.temperature_data import TemperatureData
from src.widgets.temperature_widget import TemperatureWidget
from src.widgets.fan_widget import FanWidget
from src.various.utils import populate_grid_layout


class TemperatureFanGroupWidget(QGroupBox):
    def __init__(self, title: str, temp_bases: list[str], fan_bases: list[str]):
        super().__init__(title)

        self._temp_widgets: list[TemperatureWidget] = [TemperatureWidget(TemperatureData(item)) for item in temp_bases]
        self._fan_widgets: list[FanWidget] = [FanWidget(FanData(item)) for item in fan_bases]

        layout: QVBoxLayout = QVBoxLayout()
        temp_layout: QGridLayout = QGridLayout()
        fan_layout: QGridLayout = QGridLayout()

        populate_grid_layout(temp_layout, self._temp_widgets)
        layout.addLayout(temp_layout)

        if self._fan_widgets:
            populate_grid_layout(fan_layout, self._fan_widgets)
            layout.addWidget(QFrame(frameShape=QFrame.Shape.HLine))  # separator
            layout.addLayout(fan_layout)
        self.setLayout(layout)

    def refresh(self):
        for item in self._fan_widgets:
            item.refresh_value()
        for item in self._temp_widgets:
            item.refresh_value()