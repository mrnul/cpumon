from pathlib import Path
from typing import TypeVar, Generic, Callable

T = TypeVar("T", str, float, int)


class GenericData(Generic[T]):
    def __init__(self, path: Path, name: str | None, parser: Callable[[str], T] = lambda x: x) -> None:
        self.path = path
        self.name = name
        self.parser = parser
        self._value: T | None = None

    def _read_raw(self) -> str:
        return self.path.read_text().strip()

    def read(self) -> T | None:
        self._value = self.parser(self._read_raw())
        return self._value

    def _write_raw(self, value: str) -> int:
        return self.path.write_text(value)

    def write(self, value: str) -> bool:
        if not value or not self._write_raw(value):
            return False
        self._value = self.parser(value)
        return True

    def latest_value(self) -> T | None:
        return self._value
