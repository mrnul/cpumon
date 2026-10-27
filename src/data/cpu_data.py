import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable

from src.data.base.generic_data import GenericData


@dataclass(frozen=True)
class CPUAttributeSpec:
    path: Path
    parser: Callable[[str], Any]


class CPUDataEnum(Enum):
    CURRENT_FREQUENCY = CPUAttributeSpec(Path("cpufreq/scaling_cur_freq"), int)
    ABSOLUTE_MIN_FREQ = CPUAttributeSpec(Path("cpufreq/cpuinfo_min_freq"), int)
    ABSOLUTE_MAX_FREQ = CPUAttributeSpec(Path("cpufreq/cpuinfo_max_freq"), int)
    SCALING_MIN_FREQ = CPUAttributeSpec(Path("cpufreq/scaling_min_freq"), int)
    SCALING_MAX_FREQ = CPUAttributeSpec(Path("cpufreq/scaling_max_freq"), int)
    ONLINE = CPUAttributeSpec(Path("online"), int)


@dataclass
class CPUData:
    cpu_path: Path
    cpu_name: str = field(init=False)
    cpu_index: int = field(init=False)
    data: dict[CPUDataEnum, GenericData] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.cpu_name = self.cpu_path.name
        for item in CPUDataEnum:
            self.data[item] = GenericData(self.cpu_path / item.value.path, "", item.value.parser)

        match = re.match(r"cpu(\d+)$", self.cpu_name)
        self.cpu_index = int(match.group(1)) if match else -1

    def read(self, item: CPUDataEnum, default: Any = None) -> Any:
        try:
            return self.data[item].read()
        except:
            return default

    def write(self, item: CPUDataEnum, value: int | str) -> bool:
        return self.data[item].write(str(value))

    def refresh_all(self) -> None:
        for item in CPUDataEnum:
            self.read(item)

    def __getitem__(self, item: CPUDataEnum) -> Any:
        if item not in self.data:
            return self.read(item)
        return self.data[item].latest_value()
