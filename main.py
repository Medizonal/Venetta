# Build 2
import sys
from random import choice
from typing import Callable
from PySide6 import QtWidgets # Import the module
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMenuBar,
    QMenu,
    QAction, # type: ignore
    QInputDialog,
    QDialog,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QLabel,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
import requests # Added for image downloading
import validators # type: ignore # Added for URL validation


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
        self.label.setAlignment(Qt.AlignCenter) # type: ignore # Changed to two lines
        self.setCentralWidget(self.label)

        self.menu_bar: QMenuBar = self.menuBar()

        self.add_quit_menu()

        dynamic_menus = {
            "Tools": {
                "Surprise": self.show_surprise_message,
                "Image URL Shower": self.show_image_url_view, # Added new menu item
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

        quit_action: QtWidgets.QAction = QtWidgets.QAction("Quit", self)
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
                action: QtWidgets.QAction = QtWidgets.QAction(action_name, self)
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

    def show_image_url_view(self) -> None:
        """
        Shows a dialog to enter an image URL and display the image.
        """
        # Placeholder for the dialog implementation
        dialog = QDialog(self)
        dialog.setWindowTitle("Image URL Shower")
        layout = QVBoxLayout()

        url_input = QLineEdit()
        url_input.setPlaceholderText("Enter Image URL")
        layout.addWidget(url_input)

        load_button = QPushButton("Load Image")
        layout.addWidget(load_button)

        image_label = QLabel("Image will be shown here")
        image_label.setAlignment(Qt.AlignCenter) # type: ignore
        layout.addWidget(image_label)

        # --- Logic for loading image ---
        def load_image_from_url():
            url = url_input.text()
            if not validators.url(url):
                image_label.setText("Invalid URL format.")
                return

            # Basic security check for image URLs
            if not any(
                url.lower().endswith(ext)
                for ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            ):
                image_label.setText("URL must point to an image file (.jpg, .png, .gif, etc.)")
                return

            try:
                # Security headers and size limit
                headers = {'User-Agent': 'Image-Viewer/1.0'}
                response = requests.get(
                    url, stream=True, timeout=10, headers=headers
                )
                response.raise_for_status()  # Raise an exception for HTTP errors

                # Check content type
                content_type = response.headers.get('content-type', '').lower()
                if not content_type.startswith('image/'):
                    image_label.setText("URL does not point to an image.")
                    return

                # Limit download size to prevent memory issues (5MB limit)
                max_size = 5 * 1024 * 1024  # 5MB
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

                # Keep aspect ratio, scale to fit label
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
            except Exception as e:  # Catch any other unexpected errors
                image_label.setText(f"An unexpected error occurred: {e}")

        load_button.clicked.connect(load_image_from_url)

        dialog.setLayout(layout)
        dialog.resize(400, 300) # Initial size, image might be larger or smaller
        dialog.exec()


def main() -> None:
    """
    Run the application, with a special mode for automated testing.
    """
    # This checks if '--test' was passed as an argument when running the script.
    is_test_mode = '--test' in sys.argv

    # We always need a QApplication instance.
    app = QApplication(sys.argv)

    if is_test_mode:
        print("--- Running in --test mode ---")
        try:
            # In test mode, we just create the main window to ensure it
            # initializes without errors.
            print("Initializing MainWindow...")
            _ = MainWindow()  # The window is created but not shown.
            print("MainWindow initialized successfully.")
            print("--- Test finished successfully ---")
            # Exit with a success code (0) without starting the app loop.
            sys.exit(0)
        except Exception as e:
            # If any error occurs during initialization, print it and exit
            # with a failure code (1). This will fail the GitHub Action.
            print(f"!!! ERROR during initialization: {e}")
            sys.exit(1)
    else:
        # This is the normal execution path for a user.
        window = MainWindow()
        window.resize(300, 200)
        window.show()
        # This starts the event loop and waits for the user to close the app.
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
