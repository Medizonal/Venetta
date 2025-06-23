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
