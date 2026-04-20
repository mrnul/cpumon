from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout
from superqt import QRangeSlider


class MasterSliderWidget(QWidget):
    signal_apply = Signal()

    def __init__(self):
        super().__init__()

        self._label: QLabel = QLabel()

        self._slider: QRangeSlider = QRangeSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(0, 100)
        self._slider.valueChanged.connect(self._update_slider_label)

        self._apply: QPushButton = QPushButton("Apply Master values")
        self._apply.clicked.connect(self.signal_apply)

        self._slider_label_layout: QHBoxLayout = QHBoxLayout()
        self._slider_label_layout.addWidget(self._label)
        self._slider_label_layout.addWidget(self._slider)

        self._layout: QVBoxLayout = QVBoxLayout()
        self._layout.addLayout(self._slider_label_layout)
        self._layout.addWidget(self._apply)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)

    @Slot()
    def _update_slider_label(self) -> None:
        value = self._slider.value()
        self._label.setText(f"Master values: {value}%")

    @property
    def slider(self) -> QRangeSlider:
        return self._slider

    @property
    def label(self) -> QLabel:
        return self._label
