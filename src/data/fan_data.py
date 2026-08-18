from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FanData:
    base: str

    id: int = field(init=False)
    name: str = field(init=False)
    value_full_path: Path = field(init=False)
    value: float = field(init=False)

    def __post_init__(self):
        base_path = Path(self.base)

        self.id = int(base_path.name.removeprefix("fan"))
        self.name = (base_path.parent / "name").read_text().strip()

        self.value_full_path = base_path.with_name(base_path.name + "_input")
        self.read_value()

    def read_value(self) -> float:
        self.value = int(self.value_full_path.read_text().strip())
        return self.value