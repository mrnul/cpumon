from PySide6 import QtCore
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QSlider, QSpinBox, QLabel, QPushButton

from cpu_data import CPUData
from utils import write_scaling_max_freq, get_color_based_on_value, ensure_within_range


class CPUWidget(QWidget):
    signal_processing = Signal(bool)
    signal_message = Signal(str)

    def __init__(self, cpu_path: str = ""):
        super().__init__()

        self._cpu_data = CPUData(cpu_path)
        self._cpu_data.load_all_data()

        self._label = QLabel(self._cpu_data.name)
        self._label.setToolTip(self._cpu_data.path)

        self._current_freq = QLabel()

        self._slider = QSlider(Qt.Orientation.Horizontal)
        self._slider.setRange(self._cpu_data.min_absolute_frequency, self._cpu_data.max_absolute_frequency)
        self._slider.setValue(self._cpu_data.max_scaling_frequency)

        self._spinbox_max = QSpinBox()
        self._spinbox_max.setRange(self._cpu_data.min_absolute_frequency, self._cpu_data.max_absolute_frequency)
        self._spinbox_max.setValue(self._cpu_data.max_scaling_frequency)

        self._apply = QPushButton("Apply")
        self._apply.clicked.connect(self._set_max_scaling_freq_from_spinbox)

        self._slider.valueChanged.connect(lambda value: self._spinbox_max.setValue(value))
        self._spinbox_max.valueChanged.connect(lambda value: self._slider.setValue(value))

        self._layout = QVBoxLayout()
        self._layout.addWidget(self._label)
        self._layout.addWidget(self._current_freq)
        self._layout.addWidget(self._slider)
        self._layout.addWidget(self._spinbox_max)
        self._layout.addWidget(self._apply)
        self.setLayout(self._layout)

    def set_processing_state(self, processing: bool) -> None:
        self._apply.setDisabled(processing)
        self._slider.setDisabled(processing)
        self._spinbox_max.setDisabled(processing)
        self.signal_processing.emit(processing)


    def refresh_current_freq(self) -> None:
        try:
            self._cpu_data.load_current_freq()
            color: str = get_color_based_on_value(self._cpu_data.current_frequency,
                                                  self._cpu_data.max_absolute_frequency)
            self._current_freq.setText(f"{self._cpu_data.current_frequency}")
            style: str = f"color: {color};"
            if self._cpu_data.current_frequency > self.cpu_data.max_scaling_frequency:
                style += f" border: 1px solid {color};"
            self._current_freq.setStyleSheet(style)
        except Exception as e:
            self.signal_message.emit(f"Error getting current frequency {self._cpu_data.name}: {str(e)}")

    def _set_max_scaling_freq_from_spinbox(self) -> None:
        if self.is_processing():
            self.signal_message.emit(f"Operation for {self._cpu_data.name} ignored")
            return
        try:
            self.set_processing_state(True)

            value: int = ensure_within_range(
                self._spinbox_max.value(),
                self._cpu_data.min_scaling_frequency,
                self._cpu_data.max_absolute_frequency
            )

            self._spinbox_max.setValue(value)
            self._cpu_data.max_scaling_frequency = value
            write_scaling_max_freq(self._cpu_data.path, self._spinbox_max.value())
            self.signal_message.emit(f"Max scaling frequency {self._cpu_data.name} changed to: {self._spinbox_max.value()}")
        except Exception as e:
            self.signal_message.emit(f"Error applying max scaling frequency {self._spinbox_max.value()}: {str(e)}")
        finally:
            self.refresh_static_data()

    def set_max_scaling_freq(self, value: int) -> None:
        if self.is_processing():
            self.signal_message.emit(f"Operation for {self._cpu_data.name} ignored")
            return

        self._spinbox_max.setValue(value)
        self._set_max_scaling_freq_from_spinbox()

    def refresh_static_data(self, now: bool = False) -> None:
        def perform_refresh():
            try:
                self._cpu_data.load_static_data()
                self._spinbox_max.setValue(self._cpu_data.max_scaling_frequency)
            except Exception as e:
                self.signal_message.emit(f"Error refreshing static data {self._cpu_data.name}: {str(e)}")
            finally:
                self.set_processing_state(False)

        if now:
            perform_refresh()
        else:
            tmp_timer = QtCore.QTimer(self)
            tmp_timer.setSingleShot(True)
            tmp_timer.timeout.connect(perform_refresh)
            tmp_timer.start(1000)

    def update_cpu_usage(self, usage: float | int) -> None:
        self._label.setText(f"{self.cpu_data.name}: {usage}%")

        color: str = get_color_based_on_value(usage, 100.)
        style: str = f"color: {color};"
        self._label.setStyleSheet(style)

    def is_processing(self) -> bool:
        return not self._apply.isEnabled()

    @property
    def cpu_data(self) -> CPUData:
        return self._cpu_data
