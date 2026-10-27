from src.data.fan_data import FanData
from src.widgets.base.label_value_widget import LabelValueWidget


class FanWidget(LabelValueWidget):
    def __init__(self, data: FanData):
        super().__init__()
        self.data: FanData = data
        self.set_label(f"{self.data.name}:")

    def refresh_value(self) -> None:
        new_value: str
        if (value := self.data.read()) is not None:
            new_value = str(value) + " rpm"
        else:
            new_value = "<No Data>"
        self.set_value(new_value)
