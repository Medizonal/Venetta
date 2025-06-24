import sys
from random import choice
from typing import Callable
import platform
import ctypes
from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QMenu, QInputDialog, QDialog,
    QLineEdit, QPushButton, QVBoxLayout, QLabel
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QAction, QGuiApplication
import requests
import validators  # type: ignore


class MainWindow(QMainWindow):
    def __init__(self) -> None:
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
        window_menu: QMenu = self.menu_bar.addMenu("Window")
        quit_action: QAction = QAction("Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(QApplication.quit)
        window_menu.addAction(quit_action)

    def create_menu(self, menus: dict[str, dict[str, Callable[[], None]]]) -> None:
        for menu_name, actions in menus.items():
            menu: QMenu = self.menu_bar.addMenu(menu_name)
            for action_name, callback in actions.items():
                action: QAction = QAction(action_name, self)
                action.triggered.connect(callback)
                menu.addAction(action)

    def show_surprise_message(self) -> None:
        messages = ["Hello there!", "You found me!", "Surprise 🎉", "PySide6 FTW!", "Keep clicking..."]
        self.label.setText(choice(messages))

    def perform_addition(self) -> None:
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
            if not any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']):
                image_label.setText("URL must point to an image file.")
                return
            try:
                headers = {'User-Agent': 'Image-Viewer/1.0'}
                response = requests.get(url, stream=True, timeout=10, headers=headers)
                response.raise_for_status()

                if not response.headers.get('content-type', '').lower().startswith('image/'):
                    image_label.setText("URL does not point to an image.")
                    return
                if int(response.headers.get('content-length', 0)) > 5 * 1024 * 1024:
                    image_label.setText("Image too large. Max 5MB.")
                    return

                pixmap = QPixmap()
                if not pixmap.loadFromData(response.content):
                    image_label.setText("Failed to load image.")
                    return
                image_label.setPixmap(pixmap.scaled(image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            except Exception as e:
                image_label.setText(f"Error: {e}")

        load_button.clicked.connect(load_image_from_url)

        dialog.setLayout(layout)
        dialog.resize(400, 300)
        dialog.exec()


def main() -> None:
    is_test_mode = '--test' in sys.argv

    if is_test_mode and platform.system() == "Windows":
        ctypes.windll.kernel32.AttachConsole(-1)

    app = QApplication(sys.argv)

    if is_test_mode:
        print("--- Running in --test mode ---")
        window = MainWindow()
        window.resize(400, 300)
        window.show()

        def take_screenshot_and_exit():
            screen = QGuiApplication.primaryScreen()
            if screen:
                screenshot = screen.grabWindow(0)
                screenshot.save("screenshot.png", "png")
                print("Screenshot saved.")
            else:
                print("Failed to capture screenshot.")
            app.quit()

        QTimer.singleShot(1000, take_screenshot_and_exit)  # wait 1s before screenshot
        app.exec()
    else:
        window = MainWindow()
        window.resize(300, 200)
        window.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
