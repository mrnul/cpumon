from pathlib import Path

from PySide6.QtWidgets import QGridLayout

from src.data.fan_data import FanData
from src.data.temperature_data import TemperatureData
from src.various.utils import populate_grid_layout
from src.widgets.base.group_box_widget import GroupBoxWidget
from src.widgets.fan_widget import FanWidget
from src.widgets.temperature_widget import TemperatureWidget


class TemperatureFanGroupWidgetWidget(GroupBoxWidget):
    def __init__(self, title: str, temp_bases: list[str], fan_bases: list[str]):
        super().__init__(title, None)

        self._temp_widgets: list[TemperatureWidget] = [TemperatureWidget(TemperatureData(Path(item))) for item in
                                                       temp_bases]
        self._fan_widgets: list[FanWidget] = [FanWidget(FanData(Path(item))) for item in fan_bases]

        layout: QGridLayout = QGridLayout()

        all_widgets = self._temp_widgets + self._fan_widgets

        populate_grid_layout(layout, all_widgets, per_row=4)

        self.setLayout(layout)

    def refresh(self):
        for item in self._fan_widgets:
            item.refresh_value()
        for item in self._temp_widgets:
            item.refresh_value()
