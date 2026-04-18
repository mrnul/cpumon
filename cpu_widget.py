from PySide6 import QtGui
from PySide6.QtCore import Signal, Qt, Slot, QTimer
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSpinBox, QLabel, QPushButton, QProgressBar
from superqt import QRangeSlider

from cpu_data import CPUData, CPUDataEnum
from utils import get_rgb_based_on_value, ensure_within_range


class CPUWidget(QWidget):
    DEFAULT_PROGRESSBAR_COLOR = None

    signal_processing = Signal(bool)
    signal_message = Signal(str)

    def __init__(self, cpu_path: str):
        super().__init__()

        self._refresh_timer: QTimer = QTimer()
        self._refresh_timer.timeout.connect(self._perform_refresh)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(1000)

        self._cpu_data: CPUData = CPUData(cpu_path)
        self._label: QLabel = QLabel(self._cpu_data.name)
        self._current_freq: QProgressBar = QProgressBar(
            minimum=self._cpu_data[CPUDataEnum.ABSOLUTE_MIN_FREQ],
            maximum=self._cpu_data[CPUDataEnum.ABSOLUTE_MAX_FREQ]
        )
        self._current_freq.setFormat("%v")
        if self.DEFAULT_PROGRESSBAR_COLOR is None:
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

        self._label_governor = QLabel()
        self._label_governor.setText(self._cpu_data[CPUDataEnum.SCALING_GOVERNOR])

        self._apply: QPushButton = QPushButton("Apply")
        self._apply.clicked.connect(self._set_min_max_scaling_frequencies_from_spin_boxes)

        self._slider_min_max.valueChanged.connect(self._sync_slider_to_spinbox)
        self._spinbox_min.valueChanged.connect(self._sync_spinbox_min_to_slider)
        self._spinbox_max.valueChanged.connect(self._sync_spinbox_max_to_slider)

        self._layout: QVBoxLayout = QVBoxLayout()
        self._layout.addWidget(self._label)
        self._layout.addWidget(self._current_freq)
        self._layout.addWidget(self._slider_min_max)
        self._layout.addWidget(self._spinbox_min)
        self._layout.addWidget(self._spinbox_max)
        self._layout.addWidget(self._label_governor)
        self._layout.addWidget(self._apply)
        self.setLayout(self._layout)

    @Slot(int)
    def _sync_slider_to_spinbox(self, value: tuple[int, int]) -> None:
        self._spinbox_min.blockSignals(True)
        self._spinbox_min.setValue(value[0])
        self._spinbox_min.blockSignals(False)

        self._spinbox_max.blockSignals(True)
        self._spinbox_max.setValue(value[1])
        self._spinbox_max.blockSignals(False)

    @Slot(int)
    def _sync_spinbox_min_to_slider(self, value: int) -> None:
        self._slider_min_max.blockSignals(True)
        _, current_max = self._slider_min_max.value()
        self._slider_min_max.setValue((value, current_max))
        self._slider_min_max.blockSignals(False)

    @Slot(int)
    def _sync_spinbox_max_to_slider(self, value: int) -> None:
        self._slider_min_max.blockSignals(True)
        current_min, _ = self._slider_min_max.value()
        self._slider_min_max.setValue((current_min, value))
        self._slider_min_max.blockSignals(False)

    def set_processing_state(self, processing: bool) -> None:
        self._apply.setDisabled(processing)
        self._slider_min_max.setDisabled(processing)
        self._spinbox_max.setDisabled(processing)
        self.signal_processing.emit(processing)

    def refresh_current_freq_and_governor(self) -> None:
        try:
            frequency: int = self._cpu_data.read(CPUDataEnum.CURRENT_FREQUENCY)
            governor: str = self._cpu_data.read(CPUDataEnum.SCALING_GOVERNOR)

            rgb: tuple = get_rgb_based_on_value(
                frequency,
                self._cpu_data[CPUDataEnum.ABSOLUTE_MAX_FREQ]
            )
            self._current_freq.setValue(frequency)
            self._label_governor.setText(governor)
            palette = self._current_freq.palette()
            if frequency > self._cpu_data[CPUDataEnum.SCALING_MAX_FREQ]:
                palette.setColor(QPalette.ColorRole.Highlight, QtGui.QColor.fromString("PURPLE"))
            else:
                palette.setColor(QPalette.ColorRole.Highlight, self.DEFAULT_PROGRESSBAR_COLOR)
            palette.setColor(QPalette.ColorRole.Text, QColor(*rgb))
            self._current_freq.setPalette(palette)
        except Exception as e:
            self.signal_message.emit(f"Error getting current frequency {self._cpu_data.name}: {str(e)}")

    @Slot()
    def _set_min_max_scaling_frequencies_from_spin_boxes(self) -> None:
        if self.is_processing():
            self.signal_message.emit(f"Operation for {self._cpu_data.name} ignored")
            return

        self.set_processing_state(True)
        value_min: int = ensure_within_range(
            self._spinbox_min.value(),
            self._cpu_data[CPUDataEnum.ABSOLUTE_MIN_FREQ],
            self._cpu_data[CPUDataEnum.SCALING_MAX_FREQ]
        )

        value_max: int = ensure_within_range(
            self._spinbox_max.value(),
            self._cpu_data[CPUDataEnum.SCALING_MIN_FREQ],
            self._cpu_data[CPUDataEnum.ABSOLUTE_MAX_FREQ]
        )

        self._spinbox_min.setValue(value_min)
        self._spinbox_max.setValue(value_max)

        try:
            self._cpu_data.write(CPUDataEnum.SCALING_MIN_FREQ, value_min)
            self._cpu_data.write(CPUDataEnum.SCALING_MAX_FREQ, value_max)
            self.signal_message.emit(
                f"Scaling frequencies {self._cpu_data.name} changed to: {value_min, value_max}")
        except Exception as e:
            self.signal_message.emit(
                f"Error applying scaling frequencies {value_min, value_max}: {str(e)}"
            )
        finally:
            self.refresh_static_data()

    def set_min_max_scaling_freq(self, values: tuple[int, int]) -> None:
        if self.is_processing():
            self.signal_message.emit(f"Operation for {self._cpu_data.name} ignored")
            return

        self._spinbox_min.setValue(values[0])
        self._spinbox_max.setValue(values[1])

        self._set_min_max_scaling_frequencies_from_spin_boxes()

    def _perform_refresh(self):
        try:
            self._spinbox_min.setValue(self._cpu_data.read(CPUDataEnum.SCALING_MIN_FREQ))
            self._spinbox_max.setValue(self._cpu_data.read(CPUDataEnum.SCALING_MAX_FREQ))
            self._label_governor.setText(self._cpu_data.read(CPUDataEnum.SCALING_GOVERNOR))
        except Exception as e:
            self.signal_message.emit(f"Error refreshing static data {self._cpu_data.name}: {str(e)}")
        finally:
            self.set_processing_state(False)

    def refresh_static_data(self, now: bool = False) -> None:
        if now:
            self._perform_refresh()
        else:
            self._refresh_timer.start()

    def update_cpu_usage(self, usage: float | int) -> None:
        self._label.setText(f"{self._cpu_data.name}: {usage}%")

        rgb: tuple = get_rgb_based_on_value(usage, 100.)
        palette = self._label.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor(*rgb))
        self._label.setPalette(palette)

    def is_processing(self) -> bool:
        return not self._apply.isEnabled()

    @property
    def cpu_data(self) -> CPUData:
        return self._cpu_data
