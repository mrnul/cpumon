from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import json


@dataclass
class CPUConfig:
    cpu: str | None
    min_value: int
    max_value: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CPUConfig:
        return cls(
            cpu=data["cpu"],
            min_value=data["min_value"],
            max_value=data["max_value"],
        )


@dataclass
class Profile:
    name: str
    config: list[CPUConfig]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Profile:
        return cls(
            name=data["name"],
            config=[
                CPUConfig.from_dict(config)
                for config in data["config"]
            ],
        )


@dataclass
class Settings:
    monitor: int = 0
    profiles: list[Profile] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Settings:
        return cls(
            monitor=data.get("monitor", 0),
            profiles=[
                Profile.from_dict(profile)
                for profile in data.get("profiles", [])
            ],
        )

    @classmethod
    def from_json(cls, json_data: str) -> Settings:
        return cls.from_dict(json.loads(json_data))

    @classmethod
    def from_file(cls, path: str | Path) -> Settings:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        return cls.from_dict(data)
