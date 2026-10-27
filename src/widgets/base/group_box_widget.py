from PySide6.QtGui import Qt
from PySide6.QtWidgets import QGroupBox, QWidget


class GroupBoxWidget(QGroupBox):
    def __init__(self, title: str, parent: QWidget | None):
        super().__init__(title=title, parent=parent)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.setFlat(True)
