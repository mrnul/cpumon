from PySide6.QtCore import Signal, Slot, QMutex, QMutexLocker
from PySide6.QtWidgets import QWidget, QGridLayout

from cpu_data import CPUDataEnum
from proc_stat import ProcStat
from cpu_widget import CPUWidget
from utils import parse_proc_stat


class CPUGroupWidget(QWidget):
    signal_processing = Signal(bool)
    signal_message = Signal(str)

    def __init__(self, cpu_paths: list[str]):
        super().__init__()

        self._mutex: QMutex = QMutex()
        self._currently_processing_count: int = 0
        self._proc_stat: dict[str, ProcStat] = {}

        self._layout: QGridLayout = QGridLayout()

        self._cpu_widgets: list[CPUWidget] = [
            CPUWidget(cpu_path) for cpu_path in cpu_paths
        ]

        self._cpu_widgets.sort(key=lambda x: x.cpu_data.index)

        cpus_per_row: int = 8

        for index, cpu_widget in enumerate(self._cpu_widgets):
            cpu_widget.signal_message.connect(self.signal_message.emit)
            cpu_widget.signal_processing.connect(self._processing_update)

            row, column = divmod(index, cpus_per_row)
            self._layout.addWidget(cpu_widget, row, column)

        self.setLayout(self._layout)

    def periodic_refresh(self):
        new_proc_stat: dict[str, ProcStat] = parse_proc_stat()
        for cpu in self._cpu_widgets:
            cpu.refresh_current_freq_and_governor()
            if cpu.cpu_data.name not in self._proc_stat:
                continue

            cpu.update_cpu_usage(
                round(new_proc_stat[cpu.cpu_data.name].calculate_cpu_usage(self._proc_stat[cpu.cpu_data.name]))
            )

        self._proc_stat = new_proc_stat

    def avg_min_max_scaling_freq_percentage(self) -> tuple[float, float]:
        avg_min: float = 0.
        avg_max: float = 0.
        for cpu in self._cpu_widgets:
            avg_min += cpu.cpu_data[CPUDataEnum.SCALING_MIN_FREQ] / cpu.cpu_data[CPUDataEnum.ABSOLUTE_MAX_FREQ]
            avg_max += cpu.cpu_data[CPUDataEnum.SCALING_MAX_FREQ] / cpu.cpu_data[CPUDataEnum.ABSOLUTE_MAX_FREQ]
        return avg_min * 100. / len(self._cpu_widgets), avg_max * 100. / len(self._cpu_widgets)

    def refresh_now(self) -> None:
        for cpu in self._cpu_widgets:
            cpu.refresh_static_data(True)
        self.periodic_refresh()

    def apply_master_values(self, percentages: tuple[int, int]) -> None:
        for cpu in self._cpu_widgets:
            min_value: int = percentages[0] * cpu.cpu_data[CPUDataEnum.ABSOLUTE_MAX_FREQ] // 100
            max_value: int = percentages[1] * cpu.cpu_data[CPUDataEnum.ABSOLUTE_MAX_FREQ] // 100
            cpu.set_min_max_scaling_freq((min_value, max_value))

    @Slot(bool)
    def _processing_update(self, processing: bool) -> None:
        with QMutexLocker(self._mutex):
            if processing:
                if self._currently_processing_count == 0:
                    self.signal_processing.emit(True)
                self._currently_processing_count += 1
            else:
                if self._currently_processing_count > 0:
                    self._currently_processing_count -= 1
                    if self._currently_processing_count == 0:
                        self.signal_processing.emit(False)
