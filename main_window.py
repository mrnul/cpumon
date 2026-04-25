from PySide6.QtCore import QTimer, Slot, QCoreApplication
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTextBrowser, QPushButton

from cpu_group_widget import CPUGroupBox
from master_slider_widget import MasterSliderGroupWidget
from profile import Profile
from profile_widget import ProfileGroupWidget
from utils import discover_cpus


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("cpumon")

        self._central_widget: QWidget = QWidget()
        self.setCentralWidget(self._central_widget)

        self._parent_layout: QVBoxLayout = QVBoxLayout(self._central_widget)

        self._cpus_widget: CPUGroupBox = CPUGroupBox("CPU Control", discover_cpus())
        self._cpus_widget.signal_processing.connect(self._set_processing_state)
        self._cpus_widget.signal_message.connect(self._handle_message)

        self._master_slider: MasterSliderGroupWidget = MasterSliderGroupWidget("Master Control")
        self._master_slider.signal_apply.connect(self._apply_master_values)
        self._master_slider.slider.setValue(self._cpus_widget.avg_min_max_scaling_freq_percentage())

        profiles_path: str = "./profiles.json"
        if len(QCoreApplication.arguments()) > 1:
            profiles_path = QCoreApplication.arguments()[1]

        self._profiles: ProfileGroupWidget = ProfileGroupWidget("Profile Control", profiles_path)
        self._profiles.signal_profile_changed.connect(self._profile_changed)
        self._profiles.signal_apply.connect(self._apply_profile)

        self._refresh: QPushButton = QPushButton("Refresh all Now")
        self._refresh.clicked.connect(self._refresh_now)

        self._log: QTextBrowser = QTextBrowser()
        self._log.document().setMaximumBlockCount(1000)

        self._parent_layout.addWidget(self._cpus_widget)
        self._parent_layout.addWidget(self._master_slider)
        self._parent_layout.addWidget(self._profiles)
        self._parent_layout.addWidget(self._refresh)
        self._parent_layout.addWidget(self._log)

        self._timer: QTimer = QTimer(self)
        self._timer.timeout.connect(self._cpus_widget.periodic_refresh)
        self._timer.start(1000)

    @Slot()
    def _profile_changed(self) -> None:
        profile: Profile = self._profiles.get_selected_profile()
        if not profile.config:
            self._log.append("Empty profile")
        for item in profile.config:
            if item.cpu is None:
                self._cpus_widget.set_all_cpu_percentages((item.min_value, item.max_value))
                self._master_slider.slider.setValue((item.min_value, item.max_value))
            else:
                self._cpus_widget.set_cpu_percentages(item.cpu, (item.min_value, item.max_value))

    @Slot()
    def _apply_profile(self) -> None:
        profile: Profile = self._profiles.get_selected_profile()
        self._profile_changed()
        for item in profile.config:
            if item.cpu is None:
                self._cpus_widget.apply_all_cpu_values()
            else:
                self._cpus_widget.apply_cpu_freq_values(item.cpu)

    @Slot()
    def _refresh_now(self) -> None:
        self._cpus_widget.refresh_now()
        self._master_slider.slider.setValue(self._cpus_widget.avg_min_max_scaling_freq_percentage())
        self._profiles.set_no_selection()
        self._log.append("Data refreshed")

    @Slot(bool)
    def _set_processing_state(self, processing: bool) -> None:
        self._master_slider.setDisabled(processing)
        self._refresh.setDisabled(processing)
        self._master_slider.setDisabled(processing)
        self._profiles.setDisabled(processing)
        if not processing:
            self._master_slider.slider.setValue(self._cpus_widget.avg_min_max_scaling_freq_percentage())
        self._log.append("Processing started" if processing else "Processing finished")

    @Slot()
    def _apply_master_values(self) -> None:
        self._cpus_widget.set_all_cpu_percentages(self._master_slider.slider.value())
        self._cpus_widget.apply_all_cpu_values()

    @Slot(str)
    def _handle_message(self, message: str) -> None:
        self._log.append(message)
