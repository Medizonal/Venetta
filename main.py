import sys
from random import choice
from typing import Callable
import platform
import ctypes
from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenuBar,
    QMenu,
    QInputDialog,
    QDialog,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QLabel,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QAction
import requests
import validators # type: ignore


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

        self.label = QLabel("Hi")
        self.label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(self.label)

        self.menu_bar: QMenuBar = self.menuBar()

        self.add_quit_menu()

        dynamic_menus = {
            "Tools": {
                "Surprise": self.show_surprise_message,
                "Image URL Shower": self.show_image_url_view,
            }
        }
        self.create_menu(dynamic_menus)

        calculator_menu = {
            "Calculator": {
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
                try:
                    num1 = int(num1_str)
                    num2 = int(num2_str)
                    result = num1 + num2
                    self.label.setText(f"Result: {num1} + {num2} = {result}")
                except ValueError:
                    self.label.setText("Error: Please enter valid whole numbers.")

    def show_image_url_view(self) -> None:
        """
        Shows a dialog to enter an image URL and display the image.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Image URL Shower")
        layout = QVBoxLayout()

        url_input = QLineEdit()
        url_input.setPlaceholderText("Enter Image URL")
        layout.addWidget(url_input)

        load_button = QPushButton("Load Image")
        layout.addWidget(load_button)

        image_label = QLabel("Image will be shown here")
        image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(image_label)

        def load_image_from_url():
            url = url_input.text()
            if not validators.url(url):
                image_label.setText("Invalid URL format.")
                return

            if not any(
                url.lower().endswith(ext)
                for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            ):
                image_label.setText("URL must point to an image file (.jpg, .png, .gif, etc.)")
                return

            try:
                headers = {'User-Agent': 'Image-Viewer/1.0'}
                response = requests.get(
                    url, stream=True, timeout=10, headers=headers
                )
                response.raise_for_status()

                content_type = response.headers.get('content-type', '').lower()
                if not content_type.startswith('image/'):
                    image_label.setText("URL does not point to an image.")
                    return

                max_size = 5 * 1024 * 1024
                content_length = response.headers.get('content-length')
                if content_length and int(content_length) > max_size:
                    image_label.setText("Image too large. Maximum size: 5MB")
                    return

                image_data = response.content
                if len(image_data) > max_size:
                    image_label.setText("Image too large. Maximum size: 5MB")
                    return

                pixmap = QPixmap()
                if not pixmap.loadFromData(image_data):
                    image_label.setText(
                        "Failed to load image. Unsupported format or corrupt data."
                    )
                    return

                image_label.setPixmap(
                    pixmap.scaled(
                        image_label.size(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )

            except requests.exceptions.Timeout:
                image_label.setText("Request timed out. Please try again.")
            except requests.exceptions.RequestException as e:
                image_label.setText(f"Network Error: {e}")
            except Exception as e:
                image_label.setText(f"An unexpected error occurred: {e}")

        load_button.clicked.connect(load_image_from_url)

        dialog.setLayout(layout)
        dialog.resize(400, 300)
        dialog.exec()


def main() -> None:
    """
    Run the application, with a special mode for automated testing.
    """
    is_test_mode = '--test' in sys.argv

    if is_test_mode and platform.system() == "Windows":
        if ctypes.windll.kernel32.AttachConsole(-1):
            print("Successfully attached to console for test mode.")

    app = QApplication(sys.argv)

    if is_test_mode:
        print("--- Running in --test mode ---")
        try:
            print("Initializing MainWindow...")
            _ = MainWindow()
            print("MainWindow initialized successfully.")
            print("--- Test finished successfully ---")
            sys.exit(0)
        except Exception as e:
            print(f"!!! ERROR during initialization: {e}")
            sys.exit(1)
    else:
        window = MainWindow()
        window.resize(300, 200)
        window.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
