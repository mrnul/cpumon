from PySide6.QtCore import Qt, Slot, QSignalBlocker
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QWidget, QSpinBox, QVBoxLayout, QProgressBar
from superqt import QRangeSlider

from cpu_data import CPUDataEnum, CPUData
from utils import get_rgb_based_on_value


class FreqWidget(QWidget):
    DEFAULT_PROGRESSBAR_COLOR: QColor = None
    LOW_FREQ_COLOR: QColor = QColor(154, 205, 50)
    HIGH_FREQ_COLOR: QColor = QColor(192, 68, 143)

    def __init__(self, cpu_data: CPUData):
        super().__init__()

        self._cpu_data: CPUData = cpu_data

        self._current_freq: QProgressBar = QProgressBar(
            minimum=self._cpu_data[CPUDataEnum.ABSOLUTE_MIN_FREQ],
            maximum=self._cpu_data[CPUDataEnum.ABSOLUTE_MAX_FREQ]
        )
        if not self.DEFAULT_PROGRESSBAR_COLOR:
            self.DEFAULT_PROGRESSBAR_COLOR = self._current_freq.palette().color(QPalette.ColorRole.Highlight)

        self._slider_min_max: QRangeSlider = QRangeSlider(Qt.Orientation.Horizontal)
        self._slider_min_max.setRange(
            self._cpu_data[CPUDataEnum.ABSOLUTE_MIN_FREQ],
            self._cpu_data[CPUDataEnum.ABSOLUTE_MAX_FREQ]
        )
        self._slider_min_max.setValue(
            (self._cpu_data[CPUDataEnum.SCALING_MIN_FREQ], self._cpu_data[CPUDataEnum.SCALING_MAX_FREQ])
        )

        self._spinbox_min: QSpinBox = QSpinBox()
        self._spinbox_min.setRange(
            self._cpu_data[CPUDataEnum.ABSOLUTE_MIN_FREQ],
            self._cpu_data[CPUDataEnum.ABSOLUTE_MAX_FREQ]
        )
        self._spinbox_min.setValue(self._cpu_data[CPUDataEnum.SCALING_MIN_FREQ])

        self._spinbox_max: QSpinBox = QSpinBox()
        self._spinbox_max.setRange(
            self._cpu_data[CPUDataEnum.ABSOLUTE_MIN_FREQ],
            self._cpu_data[CPUDataEnum.ABSOLUTE_MAX_FREQ]
        )
        self._spinbox_max.setValue(self._cpu_data[CPUDataEnum.SCALING_MAX_FREQ])

        self._slider_min_max.valueChanged.connect(self._sync_slider_to_spinboxes)
        self._spinbox_min.valueChanged.connect(self._sync_spinboxes_to_slider)
        self._spinbox_max.valueChanged.connect(self._sync_spinboxes_to_slider)

        self._layout: QVBoxLayout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._current_freq)
        self._layout.addWidget(self._slider_min_max)
        self._layout.addWidget(self._spinbox_min)
        self._layout.addWidget(self._spinbox_max)
        self.setLayout(self._layout)

    def update_current_freq(self) -> None:
        frequency: int = self._cpu_data.read(CPUDataEnum.CURRENT_FREQUENCY)

        rgb: tuple = get_rgb_based_on_value(
            frequency,
            self._cpu_data[CPUDataEnum.ABSOLUTE_MAX_FREQ]
        )
        self._current_freq.setValue(frequency)

        palette = self._current_freq.palette()
        if frequency > self._cpu_data[CPUDataEnum.SCALING_MAX_FREQ]:
            self._current_freq.setFormat(f"+ {frequency} +")
            palette.setColor(QPalette.ColorRole.Highlight, self.HIGH_FREQ_COLOR)
        elif frequency < self._cpu_data[CPUDataEnum.SCALING_MIN_FREQ]:
            self._current_freq.setFormat(f"- {frequency} -")
            palette.setColor(QPalette.ColorRole.Highlight, self.LOW_FREQ_COLOR)
        else:
            self._current_freq.setFormat("%v")
            palette.setColor(QPalette.ColorRole.Highlight, self.DEFAULT_PROGRESSBAR_COLOR)

        palette.setColor(QPalette.ColorRole.Text, QColor(*rgb))
        self._current_freq.setPalette(palette)
        self._current_freq.update()

    def set_min_max(self, min_max: tuple[int, ...]) -> None:
        self._slider_min_max.setValue(min_max)

    def values(self) -> tuple[int, ...]:
        return self._slider_min_max.value()

    @Slot(tuple)
    def _sync_slider_to_spinboxes(self, value: tuple[int, int]) -> None:
        with QSignalBlocker(self._spinbox_min):
            self._spinbox_min.setValue(value[0])
        with QSignalBlocker(self._spinbox_max):
            self._spinbox_max.setValue(value[1])

    @Slot()
    def _sync_spinboxes_to_slider(self) -> None:
        min_value, max_value = self._spinbox_min.value(), self._spinbox_max.value()
        if min_value > max_value:
            min_value, max_value = max_value, min_value
            with QSignalBlocker(self._spinbox_min):
                self._spinbox_min.setValue(min_value)
                self._spinbox_max.setValue(max_value)
        with QSignalBlocker(self._slider_min_max):
            self._slider_min_max.setValue((min_value, max_value))
