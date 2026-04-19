from PySide6.QtCore import Signal, Slot, QTimer
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton

from cpu_data import CPUData, CPUDataEnum
from freq_widget import FreqWidget
from utils import get_rgb_based_on_value


class CPUWidget(QWidget):
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

        self._freq_widget: FreqWidget = FreqWidget(self._cpu_data)

        self._label_governor = QLabel()
        self._label_governor.setText(self._cpu_data[CPUDataEnum.SCALING_GOVERNOR])

        self._apply: QPushButton = QPushButton("Apply")
        self._apply.clicked.connect(self._set_min_max_scaling_frequencies_from_slider)

        self._layout: QVBoxLayout = QVBoxLayout()
        self._layout.addWidget(self._label)
        self._layout.addWidget(self._freq_widget)
        self._layout.addWidget(self._label_governor)
        self._layout.addWidget(self._apply)
        self.setLayout(self._layout)

    def _set_processing_state(self, processing: bool) -> None:
        self._apply.setDisabled(processing)
        self._freq_widget.setDisabled(processing)
        self.signal_processing.emit(processing)

    def refresh_current_freq_and_governor(self) -> None:
        try:
            self._label_governor.setText(self._cpu_data.read(CPUDataEnum.SCALING_GOVERNOR))
            self._freq_widget.update_current_freq()
        except Exception as e:
            self.signal_message.emit(f"Error getting current frequency {self._cpu_data.name}: {str(e)}")

    @Slot()
    def _set_min_max_scaling_frequencies_from_slider(self) -> None:
        self._set_processing_state(True)
        min_value, max_value = self._freq_widget.values()
        try:
            self._cpu_data.write(CPUDataEnum.SCALING_MIN_FREQ, min_value)
            self._cpu_data.write(CPUDataEnum.SCALING_MAX_FREQ, max_value)
            self.signal_message.emit(
                f"Scaling frequencies {self._cpu_data.name} changed to: {min_value, max_value}")
        except Exception as e:
            self.signal_message.emit(
                f"Error applying scaling frequencies {min_value, max_value}: {str(e)}"
            )
        finally:
            self.refresh_static_data()

    def set_min_max_scaling_freq(self, values: tuple[int, int]) -> None:
        self._freq_widget.set_min_max(values)
        self._set_min_max_scaling_frequencies_from_slider()

    def _perform_refresh(self):
        try:
            self._freq_widget.set_min_max(
                (self._cpu_data.read(CPUDataEnum.SCALING_MIN_FREQ), self._cpu_data.read(CPUDataEnum.SCALING_MAX_FREQ)))
            self._label_governor.setText(self._cpu_data.read(CPUDataEnum.SCALING_GOVERNOR))
        except Exception as e:
            self.signal_message.emit(f"Error refreshing static data {self._cpu_data.name}: {str(e)}")
        finally:
            self._set_processing_state(False)

    def refresh_static_data(self, now: bool = False) -> None:
        if now:
            self._perform_refresh()
        else:
            if not self._refresh_timer.isActive():
                self._refresh_timer.start()

    def update_cpu_usage(self, usage: float | int) -> None:
        self._label.setText(f"{self._cpu_data.name}: {usage}%")

        rgb: tuple = get_rgb_based_on_value(usage, 100.)
        palette = self._label.palette()
        palette.setColor(QPalette.ColorRole.WindowText, QColor(*rgb))
        self._label.setPalette(palette)

    @property
    def cpu_data(self) -> CPUData:
        return self._cpu_data
