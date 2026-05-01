from sys import argv

from PySide6.QtWidgets import QApplication

from src.widgets.main_window import MainWindow

app = QApplication(argv)

main_window = MainWindow()
main_window.show()

app.exec()
