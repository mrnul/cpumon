from dataclasses import dataclass, field
from enum import Enum
import re
from pathlib import Path
from typing import Any, Callable


@dataclass(frozen=True)
class CPUAttributeSpec:
    path: str
    parser: Callable[[str], Any]
    writable: bool


class CPUDataEnum(Enum):
    CURRENT_FREQUENCY = CPUAttributeSpec("cpufreq/scaling_cur_freq", int, True)
    ABSOLUTE_MIN_FREQ = CPUAttributeSpec("cpufreq/cpuinfo_min_freq", int, True)
    ABSOLUTE_MAX_FREQ = CPUAttributeSpec("cpufreq/cpuinfo_max_freq", int, True)
    SCALING_MIN_FREQ = CPUAttributeSpec("cpufreq/scaling_min_freq", int, True)
    SCALING_MAX_FREQ = CPUAttributeSpec("cpufreq/scaling_max_freq", int, True)
    SCALING_AVAILABLE_GOVERNORS = CPUAttributeSpec("cpufreq/scaling_available_governors", lambda x: x.split(), False)
    SCALING_GOVERNOR = CPUAttributeSpec("cpufreq/scaling_governor", str, True)


@dataclass
class CPUData:
    path: str
    data: dict[CPUDataEnum, Any] = field(default_factory=dict)

    name: str = field(init=False)
    index: int = field(init=False)

    _paths: dict[CPUDataEnum, Path] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.name = Path(self.path).name

        self._paths = {
            item: Path(self.path) / item.value.path
            for item in CPUDataEnum
        }

        match = re.match(r"cpu(\d+)$", self.name)
        self.index = int(match.group(1)) if match else -1

    def read(self, item: CPUDataEnum) -> Any:
        raw: str = self._paths[item].read_text().strip()
        parsed = item.value.parser(raw)
        self.data[item] = parsed
        return parsed

    def write(self, item: CPUDataEnum, value: int | str) -> None:
        if not item.value.writable:
            raise AttributeError(f"{item.name} is not writable")
        self._paths[item].write_text(str(value))
        self.data[item] = item.value.parser(str(value))

    def read_all(self) -> None:
        for item in CPUDataEnum:
            self.read(item)

    def __getitem__(self, item: CPUDataEnum) -> Any:
        if item not in self.data:
            return self.read(item)
        return self.data[item]
