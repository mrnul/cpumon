from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtWidgets import QPushButton, QVBoxLayout
from superqt import QRangeSlider

from src.widgets.base.group_box_widget import GroupBoxWidget


class MasterSliderGroupWidgetWidget(GroupBoxWidget):
    signal_apply = Signal()

    def __init__(self, title: str):
        super().__init__(title, None)

        self._slider: QRangeSlider = QRangeSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(0, 100)
        self._slider.valueChanged.connect(self._update_slider_label)

        self._apply: QPushButton = QPushButton("Apply master values")
        self._apply.clicked.connect(self.signal_apply)

        self._layout: QVBoxLayout = QVBoxLayout()
        self._layout.addWidget(self._slider)
        self._layout.addWidget(self._apply)
        self.setLayout(self._layout)

    @Slot()
    def _update_slider_label(self) -> None:
        value = self._slider.value()
        self.setTitle(f"Master values: {value}%")

    @property
    def slider(self) -> QRangeSlider:
        return self._slider
