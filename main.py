import sys
from pathlib import Path

from PySide6.QtCore import QLockFile, QDir
from PySide6.QtWidgets import QApplication, QMessageBox

from src.widgets.main_window import MainWindow


def main():
    app: QApplication = QApplication(sys.argv)

    lock_path: Path = Path(QDir.tempPath()) / "cpumon.lock"
    lock: QLockFile = QLockFile(str(lock_path))

    if not lock.tryLock(0):
        QMessageBox.information(
            None,
            "Already Running",
            "Application is already running."
        )
        return 1

    app.aboutToQuit.connect(lock.unlock)

    main_window: MainWindow = MainWindow()
    main_window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())