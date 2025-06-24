import sys
from random import choice
from typing import Callable
import platform
import ctypes

# All necessary imports for the entire application
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from PySide6.QtCore import Qt, QTimer, QUrl, QObject, Slot, QFile, QIODevice
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QMenuBar, QMenu, QInputDialog, QDialog,
    QLineEdit, QPushButton, QVBoxLayout, QLabel, QTabWidget, QWidget,
    QProgressBar
)
from PySide6.QtGui import QPixmap, QAction, QGuiApplication
import requests
import validators

class Bridge(QObject):
    @Slot()
    def custom_button_clicked(self):
        print("[SUCCESS] 'Download with Rimsort' button was clicked!")

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DRAGO TEST ENV")
        print("[DEBUG] Application starting...")

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.original_tab = QWidget()
        self.original_tab_layout = QVBoxLayout()
        self.label = QLabel("Hi")
        self.label.setAlignment(Qt.AlignCenter)
        self.original_tab_layout.addWidget(self.label)
        self.original_tab.setLayout(self.original_tab_layout)
        self.tabs.addTab(self.original_tab, "Welcome")

        self.create_browser_tab()

        self.menu_bar: QMenuBar = self.menuBar()
        self.add_quit_menu()
        dynamic_menus = { "Tools": { "Surprise": self.show_surprise_message, "Image URL Shower": self.show_image_url_view, } }
        self.create_menu(dynamic_menus)
        calculator_menu = { "Calculator": { "Add Numbers": self.perform_addition, } }
        self.create_menu(calculator_menu)

    def create_browser_tab(self):
        print("[DEBUG] Creating browser tab...")
        browser_container = QWidget()
        browser_layout = QVBoxLayout(browser_container)
        browser_layout.setContentsMargins(0, 5, 0, 0)
        browser_layout.setSpacing(5)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL and press Enter")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        browser_layout.addWidget(self.url_bar)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumHeight(20)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        browser_layout.addWidget(self.progress_bar)

        self.browser = QWebEngineView()
        browser_layout.addWidget(self.browser)
        self.tabs.addTab(browser_container, "Browser")

        self.browser.urlChanged.connect(self.update_url_bar)
        self.browser.loadStarted.connect(lambda: self.progress_bar.setVisible(True))
        self.browser.loadProgress.connect(self.progress_bar.setValue)
        
        # --- Using the reliable loadFinished signal for injection ---
        self.browser.loadFinished.connect(self.inject_and_replace_button)

        # Prepare the WebChannel bridge
        js_file = QFile(":/qtwebchannel/qwebchannel.js")
        if js_file.open(QIODevice.ReadOnly):
            self.qwebchannel_js = js_file.readAll().data().decode('utf-8')
            js_file.close()
        else:
            print("FATAL: Could not load qwebchannel.js")
            self.qwebchannel_js = ""

        self.channel = QWebChannel()
        self.bridge = Bridge()
        self.channel.registerObject("py_bridge", self.bridge)
        self.browser.page().setWebChannel(self.channel)
        print("[DEBUG] WebChannel has been set up.")

        self.browser.load(QUrl("https://www.google.com"))

    def inject_and_replace_button(self, ok):
        print(f"[DEBUG] Page load finished. Success: {ok}. Attempting to replace button.")
        QTimer.singleShot(1000, lambda: self.progress_bar.setVisible(False))

        if not ok or not self.qwebchannel_js:
            return

        # This JavaScript performs a precise replacement of the original button.
        injection_script = """
            (function() {
                // Check if our button has already been injected to avoid duplicates.
                if (document.getElementById('rimsort-download-btn')) {
                    console.log('[JS DEBUG] Rimsort button already exists.');
                    return;
                }

                // 1. Find the main parent container.
                const parentDiv = document.querySelector('.game_area_purchase_game');
                if (!parentDiv) {
                    console.log('[JS DEBUG] Parent container .game_area_purchase_game not found.');
                    return;
                }

                // 2. Find the specific div that contains the original Steam button.
                const originalButtonContainer = parentDiv.querySelector('div');
                if (!originalButtonContainer) {
                    console.log('[JS DEBUG] Original button container div not found.');
                    return;
                }

                console.log('[JS DEBUG] Found target. Creating and swapping button...');

                // 3. Create a new container div for our button.
                const newButtonContainer = document.createElement('div');

                // 4. Define the HTML for our button, adding a style to prevent text wrapping.
                //    THE FIX IS HERE: style="white-space: nowrap; padding: 0 15px;"
                newButtonContainer.innerHTML = `
                    <a id="rimsort-download-btn" class="btn_green_white_innerfade btn_border_2px btn_medium" style="white-space: nowrap; padding: 0 15px;">
                        <span class="subscribeText">Download with Rimsort</span>
                    </a>
                `;

                // 5. KEY ACTION: Replace the original button's container with our new one.
                originalButtonContainer.replaceWith(newButtonContainer);

                // 6. Connect the new button's click event to our Python code.
                new QWebChannel(qt.webChannelTransport, function(channel) {
                    const py_bridge = channel.objects.py_bridge;
                    const rimsortButton = document.getElementById('rimsort-download-btn');
                    if (rimsortButton) {
                        rimsortButton.onclick = function() {
                            py_bridge.custom_button_clicked();
                        };
                        console.log('[JS DEBUG] Rimsort button successfully replaced and connected.');
                    }
                });
            })();
        """

        final_script = self.qwebchannel_js + injection_script
        self.browser.page().runJavaScript(final_script)

    def navigate_to_url(self):
        url_text = self.url_bar.text()
        print(f"[DEBUG] Navigating to URL: {url_text}")
        if not (url_text.startswith("http://") or url_text.startswith("https://")):
            url_text = "https://" + url_text
        self.browser.setUrl(QUrl(url_text))

    def update_url_bar(self, qurl):
        self.url_bar.setText(qurl.toString())

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
                    num1, num2 = int(num1_str), int(num2_str)
                    self.label.setText(f"Result: {num1} + {num2} = {num1 + num2}")
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

### --- YOUR TEST AND LAUNCH CODE, UNTOUCHED --- ###
def main() -> None:
    is_test_mode = '--test' in sys.argv

    if is_test_mode and platform.system() == "Windows":
        ctypes.windll.kernel32.AttachConsole(-1)

    app = QApplication(sys.argv)

    if is_test_mode:
        print("--- Running in --test mode ---")
        window = MainWindow()
        window.resize(1280, 800)
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
        window.resize(1280, 800)
        window.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()