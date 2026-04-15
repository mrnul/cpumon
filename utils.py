import colorsys
from pathlib import Path

from proc_stat import ProcStat


def parse_proc_stat():
    cpu_stats = dict()

    path = Path("/proc/stat")

    with path.open('r') as f:
        for line in f:
            if not line.startswith("cpu"):
                continue

            parts = line.split()

            cpu_id = parts[0]
            stats = list(map(int, parts[1:]))
            cpu_stats.update(
                {
                    cpu_id: ProcStat(
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
                }
            )
    return cpu_stats


def get_color_based_on_value(current_freq: int | float, max_freq: int | float) -> str:
    t: float = float(current_freq) / float(max_freq)
    h: float = (1. - t) * 0.333
    r, g, b = colorsys.hsv_to_rgb(h, 1., 1.)
    return f"rgb({int(r * 255)}, {int(g * 255)}, {int(b * 255)})"


def discover_cpus() -> list[str]:
    cpu_root = Path("/sys/devices/system/cpu")

    return sorted(
        str(p)
        for p in cpu_root.glob("cpu[0-9]*")
        if p.is_dir()
    )


def read_scaling_min_freq(cpu_path: str) -> int:
    path = Path(f"{cpu_path}/cpufreq/scaling_min_freq")
    return int(path.read_text().strip())


def read_scaling_max_freq(cpu_path: str) -> int:
    path = Path(f"{cpu_path}/cpufreq/scaling_max_freq")
    return int(path.read_text().strip())


def read_absolute_min_freq(cpu_path: str) -> int:
    path = Path(f"{cpu_path}/cpufreq/cpuinfo_min_freq")
    return int(path.read_text().strip())


def read_absolute_max_freq(cpu_path: str) -> int:
    path = Path(f"{cpu_path}/cpufreq/cpuinfo_max_freq")
    return int(path.read_text().strip())


def read_current_freq(cpu_path: str) -> int:
    path = Path(f"{cpu_path}/cpufreq/scaling_cur_freq")
    return int(path.read_text().strip())


def read_available_scaling_governors(cpu_path: str) -> list[str]:
    path = Path(f"{cpu_path}/cpufreq/scaling_available_governors")
    return path.read_text().strip().split(" ")


def read_active_scaling_governor(cpu_path: str) -> str:
    path = Path(f"{cpu_path}/cpufreq/scaling_governor")
    return path.read_text().strip()


def read_proc_stat() -> list[list[str]]:
    path = Path("/proc/stat")
    return [item.split(" ") for item in path.read_text().strip().split("\n")]


def write_scaling_min_freq(cpu_path: str, value: int) -> None:
    path = Path(f"{cpu_path}/cpufreq/scaling_min_freq")
    path.write_text(str(value))


def write_scaling_max_freq(cpu_path: str, value: int) -> None:
    path = Path(f"{cpu_path}/cpufreq/scaling_max_freq")
    path.write_text(str(value))


def ensure_within_range(value, min_value, max_value):
    if value > max_value:
        return max_value
    if value < min_value:
        return min_value
    return value
