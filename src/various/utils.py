import colorsys
import json
from pathlib import Path
from src.data.profile import Profile, CPUConfig

from src.data.proc_stat import ProcStat


def parse_proc_stat() -> dict[str, ProcStat]:
    cpu_stats = dict()

    path = Path("/proc/stat")

    with path.open('r') as f:
        for line in f:
            if not line.startswith("cpu"):
                continue

            parts = line.split()
            cpu_id = parts[0]
            stats = list(map(int, parts[1:]))

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
    t: float = float(value) / float(max_value)
    h: float = (1. - t) * 0.333
    r, g, b = colorsys.hsv_to_rgb(h, 1., 1.)
    return round(r * 255), round(g * 255), round(b * 255)


def discover_cpus() -> list[str]:
    cpu_root = Path("/sys/devices/system/cpu")

    return [
        str(p)
        for p in cpu_root.glob("cpu[0-9]*")
        if p.is_dir()
    ]


def parse_profiles(path: str) -> list[Profile]:
    result: list[Profile] = []
    try:
        with open(path, "r") as f:
            data: dict = json.load(f)
        result = [
            Profile(
                name=item['name'],
                config=[CPUConfig(**cfg) for cfg in item['config']]
            )
            for item in data
        ]
    except FileNotFoundError:
        pass
    return result
