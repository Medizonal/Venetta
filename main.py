from PySide6.QtWidgets import QApplication, QLabel, QMainWindow
from PySide6.QtCore import Qt
import sys

def add(a, b) -> float:
    """
    Return the sum of two numbers.
    
    Parameters:
        a: First number to add.
        b: Second number to add.
    
    Returns:
        float: The sum of a and b.
    """
    return a + b

def subtract(a, b) -> float:
    """
    Return the difference between two numbers.
    
    Parameters:
        a (float): The number to subtract from.
        b (float): The number to subtract.
    
    Returns:
        float: The result of a minus b.
    """
    return a - b

def divide(a, b) -> float:
    """
    Return the quotient of two numbers.
    
    Parameters:
        a (float): Dividend.
        b (float): Divisor.
    
    Returns:
        float: The result of dividing a by b.
    """
    return a / b

class MainWindow(QMainWindow):
    def __init__(self):
        """
        Initialize the main window with a centered label displaying "Hi" and set the window title to "Simple PySide6 App".
        """
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
