from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider


class MasterSliderWidget(QWidget):
    def __init__(self):
        super().__init__()

        self._layout: QVBoxLayout = QVBoxLayout(self)
        self._slider: QSlider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(0, 100)
        self._layout.addWidget(self._slider)

    @property
    def slider(self) -> QSlider:
        return self._slider
