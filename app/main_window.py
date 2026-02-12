from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget

from app.tabs.windows_tab import WindowsTab
from app.tabs.macos_tab import MacOSTab


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keyboard Mapper")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.resize(800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(WindowsTab(), "Windows 11")
        self.tab_widget.addTab(MacOSTab(), "macOS")
        layout.addWidget(self.tab_widget)

        self.statusBar().showMessage("Ready")
