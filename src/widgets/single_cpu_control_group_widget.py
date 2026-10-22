from pathlib import Path

from PySide6.QtCore import Signal, Slot, QTimer
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QVBoxLayout, QPushButton, QGroupBox, QProgressBar

from src.data.cpu_data import CPUData, CPUDataEnum
from src.various.utils import get_rgb_based_on_value
from src.widgets.freq_widget import FreqWidget


class SingleCPUControlGroupWidget(QGroupBox):
    signal_processing = Signal(bool)
    signal_message = Signal(str)

    def __init__(self, cpu_path: Path):
        super().__init__("")

        self._cpu_data: CPUData = CPUData(cpu_path)
        self._utilization_bar: QProgressBar = QProgressBar()
        self._utilization_bar.setRange(0, 100)
        self._utilization_bar.setValue(0)

        self.setTitle(self._cpu_data.name)
        self.setToolTip(str(cpu_path))

        self._freq_widget: FreqWidget = FreqWidget(self._cpu_data)

        self._disable: QPushButton = QPushButton("Disable")
        self._disable.setCheckable(True)
        self._disable.clicked.connect(self._disable_clicked)

        self._apply: QPushButton = QPushButton("Apply")
        self._apply.clicked.connect(self.apply_min_max_scaling_freq)

        self._layout: QVBoxLayout = QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._utilization_bar)
        self._layout.addWidget(self._freq_widget)
        self._layout.addWidget(self._disable)
        self._layout.addWidget(self._apply)
        self.setLayout(self._layout)

    @Slot(bool)
    def _disable_clicked(self, checked: bool) -> None:
        self._set_processing_state(True)
        new_state: int = 0 if checked else 1
        try:
            self._cpu_data.write(CPUDataEnum.ONLINE, new_state)
        except Exception as e:
            self.signal_message.emit(
                f"Error changing online status: {str(e)}"
            )
        finally:
            self.refresh_editable_data()
            self._freq_widget.refresh_all()
            self.set_cpu_usage(0)

    def _refresh_disabled(self) -> None:
        if not self._disable.isCheckable():
            return

        current_state: bool | None = self._cpu_data.read(CPUDataEnum.ONLINE, None)
        new_state: bool = not current_state
        if current_state is None:
            new_state = False
            self._disable.setCheckable(False)
            self._disable.setChecked(False)
            self._disable.setEnabled(False)

        new_text: str = "Disable" if not new_state else "Enable"

        self._disable.setChecked(new_state)
        self._disable.setText(new_text)

    def _set_processing_state(self, processing: bool) -> None:
        self.setDisabled(processing)
        self.signal_processing.emit(processing)

    def periodic_refresh(self) -> None:
        try:
            self._refresh_disabled()
            self._freq_widget.refresh_current_freq()
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
            self.refresh_editable_data()

    def set_min_max_scaling_freq(self, values: tuple[int, ...]) -> None:
        self._freq_widget.set_min_max(values)

    def refresh_editable_data(self, now: bool = False) -> None:
        def _perform_refresh() -> None:
            try:
                self._freq_widget.set_min_max((
                    self._cpu_data.read(CPUDataEnum.SCALING_MIN_FREQ, 0),
                    self._cpu_data.read(CPUDataEnum.SCALING_MAX_FREQ, 0)
                ))
                self._refresh_disabled()
            except Exception as e:
                self.signal_message.emit(f"Error refreshing static data {self._cpu_data.name}: {str(e)}")
            finally:
                self._set_processing_state(False)

        if now:
            _perform_refresh()
        else:
            QTimer.singleShot(1000, _perform_refresh)

    def set_cpu_usage(self, usage: float | int) -> None:
        self._utilization_bar.setValue(int(usage))

        rgb: tuple = get_rgb_based_on_value(usage, 100.)
        palette = self._utilization_bar.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor(*rgb))
        self._utilization_bar.setPalette(palette)

    @property
    def cpu_data(self) -> CPUData:
        return self._cpu_data
