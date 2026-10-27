from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton

from src.data.settings import Profile
from src.widgets.base.group_box_widget import GroupBoxWidget


class ProfileGroupWidgetWidget(GroupBoxWidget):
    signal_profile_clicked = Signal(Profile)

    def __init__(self, title: str, profiles: list[Profile]):
        super().__init__(title, None)

        self._profiles: list[Profile] = profiles
        self._buttons: list[QPushButton] = [
            QPushButton(profile.name, self) for profile in self._profiles
        ]

        self._layout: QHBoxLayout = QHBoxLayout()
        for i, button in enumerate(self._buttons):
            button.clicked.connect(
                lambda _, idx=i: self._on_button_clicked(self._profiles[idx])
            )
            self._layout.addWidget(button)
        self.setLayout(self._layout)

    def _on_button_clicked(self, profile: Profile) -> None:
        self.signal_profile_clicked.emit(profile)
