import os

from utils import (
    read_scaling_min_freq,
    read_scaling_max_freq,
    read_absolute_max_freq,
    read_current_freq, read_absolute_min_freq,
)


class CPUData:
    def __init__(self, path: str):
        self.path: str = path

        self.current_frequency: int = -1

        self.min_scaling_frequency: int = -1
        self.max_scaling_frequency: int = -1

        self.min_absolute_frequency: int = -1
        self.max_absolute_frequency: int = -1

        self.name: str = os.path.basename(self.path)
        self.index = int(self.name.replace("cpu", ""))

    def load_current_freq(self):
        self.current_frequency = read_current_freq(self.path)

    def load_static_data(self):
        self.min_scaling_frequency = read_scaling_min_freq(self.path)
        self.max_scaling_frequency = read_scaling_max_freq(self.path)
        self.min_absolute_frequency = read_absolute_min_freq(self.path)
        self.max_absolute_frequency = read_absolute_max_freq(self.path)

    def load_all_data(self):
        self.load_current_freq()
        self.load_static_data()
