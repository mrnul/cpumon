from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout


class LabelValueWidget(QWidget):
    def __init__(self):
        super().__init__()

        self._label: QLabel = QLabel()
        self._value: QLabel = QLabel()

        self._layout: QHBoxLayout = QHBoxLayout()
        self._layout.addWidget(self._label)
        self._layout.addWidget(self._value)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(1)
        self.setLayout(self._layout)

    def set_label(self, label: str) -> None:
        self._label.setText(label)

    def set_value(self, value: str) -> None:
        self._value.setText(value)
