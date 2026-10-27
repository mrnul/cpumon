from pathlib import Path

from src.data.base.generic_data import GenericData


class TemperatureData(GenericData):
    def __init__(self, base_path: Path):
        super().__init__(
            path=base_path.with_name(base_path.name + "_input"),
            name=(base_path.parent / "name").read_text().strip(),
            parser=lambda x: float(x) / 1000.
        )
        self.read()
