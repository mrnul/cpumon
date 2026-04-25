from PySide6.QtCore import Signal, Slot, QTimer
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QGroupBox, QProgressBar

from cpu_data import CPUData, CPUDataEnum
from freq_widget import FreqGroupWidget
from utils import get_rgb_based_on_value


class CPUGroupWidget(QGroupBox):
    signal_processing = Signal(bool)
    signal_message = Signal(str)

    def __init__(self, cpu_path: str):
        super().__init__("")

        self._cpu_data: CPUData = CPUData(cpu_path)
        self._utilization_bar: QProgressBar = QProgressBar()
        self._utilization_bar.setRange(0, 100)
        self._utilization_bar.setValue(0)

        self.setTitle(self._cpu_data.name)
        self.setToolTip(cpu_path)

        self._freq_widget: FreqGroupWidget = FreqGroupWidget(self._cpu_data)

        self._label_governor = QLabel()
        self._label_governor.setText(self._cpu_data[CPUDataEnum.SCALING_GOVERNOR])

        self._apply: QPushButton = QPushButton("Apply")
        self._apply.clicked.connect(self.apply_min_max_scaling_freq)

        self._layout: QVBoxLayout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._utilization_bar)
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
    def apply_min_max_scaling_freq(self) -> None:
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

    def set_min_max_scaling_freq(self, values: tuple[int, ...]) -> None:
        self._freq_widget.set_min_max(values)

    def _perform_refresh(self) -> None:
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
            QTimer.singleShot(1000, self._perform_refresh)

    def update_cpu_usage(self, usage: float | int) -> None:
        self._utilization_bar.setValue(int(usage))

        rgb: tuple = get_rgb_based_on_value(usage, 100.)
        palette = self._utilization_bar.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor(*rgb))
        self._utilization_bar.setPalette(palette)

    @property
    def cpu_data(self) -> CPUData:
        return self._cpu_data
