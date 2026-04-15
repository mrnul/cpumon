from PySide6.QtWidgets import QApplication

from main_window import MainWindow

app = QApplication([])

main_window = MainWindow()
main_window.show()

app.exec()
