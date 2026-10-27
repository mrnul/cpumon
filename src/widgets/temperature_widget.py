from src.data.temperature_data import TemperatureData
from src.widgets.base.label_value_widget import LabelValueWidget


class TemperatureWidget(LabelValueWidget):
    def __init__(self, data: TemperatureData):
        super().__init__()
        self.data: TemperatureData = data
        self.set_label(f"{self.data.name}:")

    def refresh_value(self) -> None:
        new_value: str
        if (value := self.data.read()) is not None:
            new_value = str(value) + " °C"
        else:
            new_value = "<No Data>"
        self.set_value(new_value)
