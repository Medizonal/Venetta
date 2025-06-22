from PySide6.QtWidgets import QApplication, QLabel, QMainWindow
from PySide6.QtCore import Qt
import sys

def add(a, b) -> float:
    return a + b

def subtract(a, b) -> float:
    return a - b

def divide(a, b) -> float:
    return a / b

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple PySide6 App")

        label = QLabel("Hi", alignment=Qt.AlignCenter)
        self.setCentralWidget(label)


if __name__ == "__main__":
    print(add(10, 5))
    print(divide(20, 4))

    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(300, 200)
    window.show()
    sys.exit(app.exec())
