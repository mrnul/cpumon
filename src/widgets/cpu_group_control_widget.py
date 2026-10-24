from pathlib import Path

from PySide6.QtCore import Signal, Slot, QMutex, QMutexLocker
from PySide6.QtWidgets import QGridLayout, QVBoxLayout, QPushButton

from src.data.cpu_data import CPUDataEnum
from src.data.proc_stat import ProcStat
from src.various.utils import parse_proc_stat
from src.various.utils import populate_grid_layout
from src.widgets.single_cpu_control_group_widget import SingleCPUControlGroupWidget
from src.widgets.group_box_base import GroupBoxBase


class CPUGroupControlWidget(GroupBoxBase):
    signal_processing = Signal(bool)
    signal_message = Signal(str)

    def __init__(self, title: str, cpu_paths: list[Path]):
        super().__init__(title, None)

        self._mutex: QMutex = QMutex()
        self._currently_processing_count: int = 0
        self._proc_stat: dict[str, ProcStat] = {}

        self._layout: QVBoxLayout = QVBoxLayout()
        self._cpu_widget_layout: QGridLayout = QGridLayout()

        self._cpu_widgets = [SingleCPUControlGroupWidget(cpu_path) for cpu_path in cpu_paths]
        self._apply_all: QPushButton = QPushButton("Apply all")
        self._apply_all.clicked.connect(self.apply_all_cpu_values)
        self._map_cpu_widgets: dict[str, SingleCPUControlGroupWidget] = {
            cpu.cpu_data.name: cpu
            for cpu in self._cpu_widgets
        }

        self._cpu_widgets.sort(key=lambda x: x.cpu_data.index)

        for cpu_widget in self._cpu_widgets:
            cpu_widget.signal_message.connect(self.signal_message.emit)
            cpu_widget.signal_processing.connect(self._processing_update)

        populate_grid_layout(self._cpu_widget_layout, self._cpu_widgets)

        self._layout.addLayout(self._cpu_widget_layout)
        self._layout.addWidget(self._apply_all)
        self.setLayout(self._layout)

    def refresh_non_editable_data(self) -> None:
        new_proc_stat: dict[str, ProcStat] = parse_proc_stat()
        for cpu in self._cpu_widgets:
            cpu.refresh_non_editable_data()
            if cpu.cpu_data.name not in self._proc_stat or cpu.cpu_data.name not in new_proc_stat:
                continue

            cpu.set_cpu_usage(
                round(new_proc_stat[cpu.cpu_data.name].calculate_cpu_usage(self._proc_stat[cpu.cpu_data.name]))
            )
        self._proc_stat = new_proc_stat

    def avg_min_max_scaling_freq_percentage(self) -> tuple[float, float]:
        avg_min: float = 0.
        avg_max: float = 0.
        count: int = 0
        for cpu in self._cpu_widgets:
            abs_max_freq: int = cpu.cpu_data.read(CPUDataEnum.ABSOLUTE_MAX_FREQ, 0)
            if not abs_max_freq:
                continue
            count += 1
            avg_min += cpu.cpu_data[CPUDataEnum.SCALING_MIN_FREQ] / abs_max_freq
            avg_max += cpu.cpu_data[CPUDataEnum.SCALING_MAX_FREQ] / abs_max_freq
        return avg_min * 100. / count, avg_max * 100. / count

    def refresh_now(self) -> None:
        for cpu in self._cpu_widgets:
            cpu.refresh_editable_data(True)
        self.refresh_non_editable_data()

    def set_all_cpu_percentages(self, percentages: tuple[int, ...]) -> None:
        for cpu in self._cpu_widgets:
            self.set_cpu_percentages(cpu.cpu_data.name, percentages)

    def apply_all_cpu_values(self) -> None:
        for cpu in self._cpu_widgets:
            cpu.apply_min_max_scaling_freq()

    @Slot(bool)
    def _processing_update(self, processing: bool) -> None:
        with QMutexLocker(self._mutex):
            if not processing and self._currently_processing_count == 0:
                return

            previous_count: int = self._currently_processing_count

            if processing:
                self._currently_processing_count += 1
            elif previous_count > 0:
                self._currently_processing_count -= 1

            if previous_count == 0 or previous_count == 1:
                is_processing: bool = self._currently_processing_count > 0
                self.signal_processing.emit(is_processing)
                self._apply_all.setDisabled(is_processing)

    def set_cpu_percentages(self, cpu_name: str, percentages: tuple[int, ...]) -> None:
        cpu: SingleCPUControlGroupWidget | None = self._map_cpu_widgets.get(cpu_name)
        if not cpu:
            self.signal_message.emit(f"CPU {cpu_name} not found")
            return
        min_value: int = percentages[0] * cpu.cpu_data[CPUDataEnum.ABSOLUTE_MAX_FREQ] // 100
        max_value: int = percentages[1] * cpu.cpu_data[CPUDataEnum.ABSOLUTE_MAX_FREQ] // 100
        cpu.set_min_max_scaling_freq((min_value, max_value))

    def apply_cpu_freq_values(self, cpu_name: str) -> None:
        cpu: SingleCPUControlGroupWidget | None = self._map_cpu_widgets.get(cpu_name)
        if not cpu:
            self.signal_message.emit(f"CPU {cpu_name} not found")
            return
        cpu.apply_min_max_scaling_freq()
