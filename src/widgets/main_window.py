from PySide6.QtCore import QTimer, Slot, QCoreApplication
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTextBrowser, QPushButton

from src.data.settings import Settings
from src.data.settings import Profile
from src.various.utils import discover_cpu_dirs, discover_fan_bases
from src.various.utils import discover_temperature_bases
from src.various.utils import ui_update
from src.widgets.cpu_group_control_widget import CPUGroupControlWidget
from src.widgets.master_slider_group_widget import MasterSliderGroupWidget
from src.widgets.profile_group_widget import ProfileGroupWidget
from src.widgets.temperature_fan_group_widget import TemperatureFanGroupWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("cpumon")

        self._central_widget: QWidget = QWidget()
        self.setCentralWidget(self._central_widget)

        self._parent_layout: QVBoxLayout = QVBoxLayout(self._central_widget)

        self._temperatures_and_fans_widget: TemperatureFanGroupWidget = TemperatureFanGroupWidget("Temperatures and Fans", discover_temperature_bases(), discover_fan_bases())

        self._cpus_widget: CPUGroupControlWidget = CPUGroupControlWidget("CPU Control", discover_cpu_dirs())
        self._cpus_widget.signal_processing.connect(self._set_processing_state)
        self._cpus_widget.signal_message.connect(self._handle_message)

        self._master_slider: MasterSliderGroupWidget = MasterSliderGroupWidget("Master Control")
        self._master_slider.signal_apply.connect(self._apply_master_values)
        self._master_slider.slider.setValue(self._cpus_widget.avg_min_max_scaling_freq_percentage())

        settings_path: str = "./settings.json"
        if len(QCoreApplication.arguments()) > 1:
            settings_path = QCoreApplication.arguments()[1]
        self._settings: Settings = Settings.from_file(settings_path)

        self._profiles: ProfileGroupWidget = ProfileGroupWidget("Profile Control", self._settings.profiles)
        self._profiles.signal_profile_clicked.connect(self._apply_profile)

        self._refresh: QPushButton = QPushButton("Refresh all Now")
        self._refresh.clicked.connect(self._refresh_now)

        self._log: QTextBrowser = QTextBrowser()
        self._log.document().setMaximumBlockCount(1000)

        self._parent_layout.addWidget(self._temperatures_and_fans_widget)
        self._parent_layout.addWidget(self._cpus_widget)
        self._parent_layout.addWidget(self._master_slider)
        self._parent_layout.addWidget(self._profiles)
        self._parent_layout.addWidget(self._refresh)
        self._parent_layout.addWidget(self._log)

        try:
            self.adjustSize()
            screen = QGuiApplication.screens()[self._settings.monitor]
            geometry = screen.availableGeometry()

            middle_x = geometry.x() + (geometry.width() - self.width()) // 2
            middle_y = geometry.y() + (geometry.height() - self.height()) // 2

            self.move(middle_x, middle_y)
        except (TypeError, IndexError) as e:
            self._log.append(str(e))
            pass

        self._timer: QTimer = QTimer(self)
        self._timer.timeout.connect(self._periodic_refresh)
        self._timer.start(1000)

        self._log.append("Ready")

    def _periodic_refresh(self):
        with ui_update(self._central_widget):
            self._cpus_widget.periodic_refresh()
            self._temperatures_and_fans_widget.refresh()

    @Slot(Profile)
    def _apply_profile(self, profile: Profile) -> None:
        with ui_update(self._central_widget):
            for item in profile.config:
                if item.cpu is None:
                    self._master_slider.slider.setValue((item.min_value,  item.max_value))
                    self._cpus_widget.set_all_cpu_percentages((item.min_value,  item.max_value))
                    self._cpus_widget.apply_all_cpu_values()
                else:
                    self._cpus_widget.set_cpu_percentages(item.cpu, (item.min_value, item.max_value))
                    self._cpus_widget.apply_cpu_freq_values(item.cpu)

    @Slot()
    def _refresh_now(self) -> None:
        with ui_update(self._central_widget):
            self._cpus_widget.refresh_now()
            self._temperatures_and_fans_widget.refresh()
            self._master_slider.slider.setValue(self._cpus_widget.avg_min_max_scaling_freq_percentage())
            self._log.append("Data refreshed")

    @Slot(bool)
    def _set_processing_state(self, processing: bool) -> None:
        with ui_update(self._central_widget):
            self._master_slider.setDisabled(processing)
            self._refresh.setDisabled(processing)
            self._profiles.setDisabled(processing)
            if not processing:
                self._master_slider.slider.setValue(self._cpus_widget.avg_min_max_scaling_freq_percentage())
            self._log.append("Processing started" if processing else "Processing finished")

    @Slot()
    def _apply_master_values(self) -> None:
        with ui_update(self._central_widget):
            self._cpus_widget.set_all_cpu_percentages(self._master_slider.slider.value())
            self._cpus_widget.apply_all_cpu_values()

    @Slot(str)
    def _handle_message(self, message: str) -> None:
        self._log.append(message)
