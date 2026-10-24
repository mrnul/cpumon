import colorsys
from contextlib import contextmanager
from pathlib import Path

from PySide6.QtWidgets import QWidget, QGridLayout

from src.data.proc_stat import ProcStat


@contextmanager
def ui_update(widget: QWidget):
    updates_enabled: bool = widget.updatesEnabled()
    widget.setUpdatesEnabled(False)
    try:
        yield
    finally:
        widget.setUpdatesEnabled(updates_enabled)
        widget.update()


def parse_proc_stat() -> dict[str, ProcStat]:
    cpu_stats = dict()

    path = Path("/proc/stat")

    with path.open('r') as f:
        for line in f:
            if not line.startswith("cpu"):
                continue

            parts = line.split()
            if len(parts) == 0:
                continue
            cpu_id = parts[0]
            stats = list(map(int, parts[1:]))

            if len(stats) < 8:
                continue

            cpu_stats[cpu_id] = ProcStat(
                cpu_id=cpu_id,
                user_time=stats[0],
                nice_time=stats[1],
                system_time=stats[2],
                idle_time=stats[3],
                iowait_time=stats[4],
                irq_time=stats[5],
                softirq_time=stats[6],
                steal_time=stats[7],
                guest_time=stats[8] if len(stats) > 8 else 0,
                guest_nice_time=stats[9] if len(stats) > 9 else 0,
            )
    return cpu_stats


def get_rgb_based_on_value(value: int | float, max_value: int | float) -> tuple[int, int, int]:
    t: float = float(value) / float(max_value) if max_value else 0.
    h: float = (1. - t) * 0.333
    r, g, b = colorsys.hsv_to_rgb(h, 1., 1.)
    return round(r * 255), round(g * 255), round(b * 255)


def discover_dirs(root_item: str, pattern: str) -> list[Path]:
    root_path = Path(root_item)
    return [
        p
        for p in root_path.glob(pattern)
        if p.is_dir()
    ]


def discover_cpu_dirs() -> list[Path]:
    return discover_dirs("/sys/devices/system/cpu", "cpu[0-9]*")


def discover_hwmon_dirs() -> list[Path]:
    return discover_dirs("/sys/class/hwmon", "hwmon[0-9]*")


def discover_temperature_bases() -> list[str]:
    return [
        str(item).removesuffix("_input") for hwmon in discover_hwmon_dirs() for item in hwmon.iterdir()
        if item.name.startswith("temp") and item.name.endswith("input")
    ]


def discover_fan_bases() -> list[str]:
    return [
        str(item).removesuffix("_input") for hwmon in discover_hwmon_dirs() for item in hwmon.iterdir()
        if item.name.startswith("fan") and item.name.endswith("input")
    ]


def populate_grid_layout(layout: QGridLayout, widgets: list[QWidget], per_row: int = 8) -> None:
    for index, widget in enumerate(widgets):
        row, column = divmod(index, per_row)
        layout.addWidget(widget, row, column)
