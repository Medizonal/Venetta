# Build 2
import sys
from random import choice
from typing import Callable
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMenuBar,
    QMenu,
    QAction,
    QInputDialog,
)
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    """
    Main application window with dynamic and static menu setup.
    """

    def __init__(self) -> None:
        """
        Initialize the main window and UI.
        """
        super().__init__()
        self.setWindowTitle("Simple PySide6 App")

        self.label = QLabel("Hi", alignment=Qt.AlignCenter)
        self.setCentralWidget(self.label)

        self.menu_bar: QMenuBar = self.menuBar()

        self.add_quit_menu()

        dynamic_menus = {
            "Tools": {
                "Surprise": self.show_surprise_message
            }
        }
        self.create_menu(dynamic_menus)

        calculator_menu = {
            "Calculator": {
                ## FIXED: Renamed the menu item now that the bug is gone.
                "Add Numbers": self.perform_addition,
            }
        }
        self.create_menu(calculator_menu)

    def add_quit_menu(self) -> None:
        """
        Add the 'Window' menu with a 'Quit' action.
        """
        window_menu: QMenu = self.menu_bar.addMenu("Window")

        quit_action: QAction = QAction("Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.quit_app)

        window_menu.addAction(quit_action)

    def create_menu(self, menus: dict[str, dict[str, Callable[[], None]]]) -> None:
        """
        Dynamically create additional menus and actions.

        Parameters:
            menus (dict): A dictionary where keys are menu names and
                          values are dictionaries of action name -> callback.
        """
        for menu_name, actions in menus.items():
            menu: QMenu = self.menu_bar.addMenu(menu_name)
            for action_name, callback in actions.items():
                action: QAction = QAction(action_name, self)
                action.triggered.connect(callback)
                menu.addAction(action)

    def quit_app(self) -> None:
        """
        Quit the application.
        """
        QApplication.quit()

    def show_surprise_message(self) -> None:
        """
        Show a random surprise message in the central label.
        """
        messages = [
            "Hello there!",
            "You found me!",
            "Surprise 🎉",
            "PySide6 FTW!",
            "Keep clicking..."
        ]
        self.label.setText(choice(messages))

    def perform_addition(self) -> None:
        """Get two numbers from the user and add them."""
        num1_str, ok1 = QInputDialog.getText(self, "Addition", "Enter the first number:")
        if ok1:
            num2_str, ok2 = QInputDialog.getText(self, "Addition", "Enter the second number:")
            if ok2:
                ## FIXED: The logic is now wrapped in a try-except block
                ## to handle cases where the user enters non-numeric text.
                try:
                    # Convert the input strings to integers before adding
                    num1 = int(num1_str)
                    num2 = int(num2_str)
                    
                    # Now the '+' operator performs correct mathematical addition
                    result = num1 + num2
                    self.label.setText(f"Result: {num1} + {num2} = {result}")
                except ValueError:
                    # If conversion to int() fails, show an error.
                    self.label.setText("Error: Please enter valid whole numbers.")


def main() -> None:
    """
    Run the application.
    """
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(300, 200)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
