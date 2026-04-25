from PySide6.QtCore import Qt, Slot, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QGroupBox
from superqt import QRangeSlider


class MasterSliderGroupWidget(QGroupBox):
    signal_apply = Signal()

    def __init__(self, title: str):
        super().__init__(title)

        self._label: QLabel = QLabel()

        self._slider: QRangeSlider = QRangeSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(0, 100)
        self._slider.valueChanged.connect(self._update_slider_label)

        self._apply: QPushButton = QPushButton("Apply master values")
        self._apply.clicked.connect(self.signal_apply)

        self._slider_label_layout: QHBoxLayout = QHBoxLayout()
        self._slider_label_layout.addWidget(self._label)
        self._slider_label_layout.addWidget(self._slider)

        self._layout: QVBoxLayout = QVBoxLayout()
        self._layout.addLayout(self._slider_label_layout)
        self._layout.addWidget(self._apply)
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
