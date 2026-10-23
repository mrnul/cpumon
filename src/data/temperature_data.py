from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TemperatureData:
    base: str

    id: int = field(init=False)
    name: str = field(init=False)
    label: str = field(init=False)
    value_full_path: Path = field(init=False)
    value: float | None = field(init=False)

    def __post_init__(self):
        base_path = Path(self.base)

        self.id = int(base_path.name.removeprefix("temp"))
        self.name = (base_path.parent / "name").read_text().strip()

        label_path = base_path.with_name(base_path.name + "_label")
        self.label = label_path.read_text().strip() if label_path.exists() else ""

        self.value_full_path = base_path.with_name(base_path.name + "_input")
        self.read_value()

    def read_value(self) -> float | None:
        try:
            self.value = int(self.value_full_path.read_text().strip()) / 1000.0
        except (Exception,):
            self.value = None
        return self.value
