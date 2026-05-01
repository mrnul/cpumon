from dataclasses import dataclass


@dataclass
class CPUConfig:
    cpu: str | None
    min_value: int
    max_value: int


@dataclass
class Profile:
    name: str
    config: list[CPUConfig]
