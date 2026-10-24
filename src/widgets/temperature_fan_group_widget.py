from PySide6.QtWidgets import QGridLayout

from src.data.fan_data import FanData
from src.data.temperature_data import TemperatureData
from src.various.utils import populate_grid_layout
from src.widgets.fan_widget import FanWidget
from src.widgets.temperature_widget import TemperatureWidget
from src.widgets.group_box_base import GroupBoxBase


class TemperatureFanGroupWidget(GroupBoxBase):
    def __init__(self, title: str, temp_bases: list[str], fan_bases: list[str]):
        super().__init__(title, None)

        self._temp_widgets: list[TemperatureWidget] = [TemperatureWidget(TemperatureData(item)) for item in temp_bases]
        self._fan_widgets: list[FanWidget] = [FanWidget(FanData(item)) for item in fan_bases]

        layout: QGridLayout = QGridLayout()
        populate_grid_layout(layout, self._temp_widgets + self._fan_widgets, per_row=4)

        self.setLayout(layout)

    def refresh(self):
        for item in self._fan_widgets:
            item.refresh_value()
        for item in self._temp_widgets:
            item.refresh_value()