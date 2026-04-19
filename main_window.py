from PySide6.QtCore import QTimer, Slot
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QTextBrowser, QPushButton, QLabel

from cpu_group_widget import CPUGroupWidget
from master_slider_widget import MasterSliderWidget
from utils import discover_cpus


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self._central_widget: QWidget = QWidget()
        self.setCentralWidget(self._central_widget)

        self._parent_layout: QVBoxLayout = QVBoxLayout(self._central_widget)

        self._cpus_widget: CPUGroupWidget = CPUGroupWidget(discover_cpus())
        self._cpus_widget.signal_processing.connect(self._set_processing_state)
        self._cpus_widget.signal_message.connect(self._handle_message)

        self._log: QTextBrowser = QTextBrowser()
        self._log.document().setMaximumBlockCount(1000)

        self._master_slider: MasterSliderWidget = MasterSliderWidget()
        self._master_slider_label: QLabel = QLabel()
        self._master_slider.slider.valueChanged.connect(self._update_master_slider_label)
        self._master_slider.slider.setValue(self._cpus_widget.avg_min_max_scaling_freq_percentage())

        self._apply: QPushButton = QPushButton("Apply Master values")
        self._apply.clicked.connect(self._apply_master_values)

        self._refresh: QPushButton = QPushButton("Refresh All Now")
        self._refresh.clicked.connect(self._refresh_now)

        slider_layout: QHBoxLayout = QHBoxLayout()
        slider_layout.addWidget(self._master_slider_label)
        slider_layout.addWidget(self._master_slider)

        button_layout: QVBoxLayout = QVBoxLayout()
        button_layout.addWidget(self._apply)
        button_layout.addWidget(self._refresh)

        self._parent_layout.addWidget(self._cpus_widget)
        self._parent_layout.addLayout(slider_layout)
        self._parent_layout.addLayout(button_layout)
        self._parent_layout.addWidget(self._log)

        self._timer: QTimer = QTimer(self)
        self._timer.timeout.connect(self._cpus_widget.periodic_refresh)
        self._timer.start(1000)

    @Slot()
    def _refresh_now(self):
        self._cpus_widget.refresh_now()
        self._log.append("Data refreshed")

    @Slot(bool)
    def _set_processing_state(self, processing: bool) -> None:
        self._apply.setDisabled(processing)
        self._refresh.setDisabled(processing)
        self._master_slider.setDisabled(processing)
        if not processing:
            self._master_slider.slider.setValue(self._cpus_widget.avg_min_max_scaling_freq_percentage())
        self._log.append("Processing started" if processing else "Processing finished")

    @Slot()
    def _update_master_slider_label(self) -> None:
        value = self._master_slider.slider.value()
        self._master_slider_label.setText(f"Master values: {value}%")

    @Slot()
    def _apply_master_values(self) -> None:
        self._cpus_widget.apply_master_values(self._master_slider.slider.value())

    @Slot(str)
    def _handle_message(self, message: str) -> None:
        self._log.append(message)
