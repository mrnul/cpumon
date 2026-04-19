from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout
from superqt import QRangeSlider


class MasterSliderWidget(QWidget):
    def __init__(self):
        super().__init__()

        self._layout: QVBoxLayout = QVBoxLayout(self)
        self._slider: QRangeSlider = QRangeSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(0, 100)
        self._layout.addWidget(self._slider)

    @property
    def slider(self) -> QRangeSlider:
        return self._slider
