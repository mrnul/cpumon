from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QPushButton, QGroupBox

from src.data.profile import Profile
from src.various.utils import parse_profiles


class ProfileGroupWidget(QGroupBox):
    signal_profile_changed = Signal()
    signal_apply = Signal()

    DEFAULT_PROFILE: Profile = Profile(name="No selection", config=[])

    def __init__(self, title: str, profiles_path: str):
        super().__init__(title)

        self._profiles: list[Profile] = [self.DEFAULT_PROFILE] + parse_profiles(profiles_path)

        self._combobox: QComboBox = QComboBox()
        self._combobox.addItems([profile.name for profile in self._profiles])
        self._combobox.currentTextChanged.connect(self.signal_profile_changed)

        self._apply: QPushButton = QPushButton("Apply Profile")
        self._apply.clicked.connect(self.signal_apply)

        self._layout: QHBoxLayout = QHBoxLayout()
        self._layout.addWidget(self._combobox)
        self._layout.addWidget(self._apply)
        self.setLayout(self._layout)

    def get_selected_profile(self) -> Profile:
        return self._profiles[self._combobox.currentIndex()]

    def set_no_selection(self) -> None:
        self._combobox.setCurrentIndex(0)
