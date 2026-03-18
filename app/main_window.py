import platform

from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget

from app.tabs.windows_tab import WindowsTab
from app.tabs.macos_tab import MacOSTab

IS_WINDOWS = platform.system() == "Windows"


class HotkeyListener(QObject):
    toggle_signal = Signal()

    TOGGLE_VK = 0xC0
    WM_KEYDOWN = 0x0100
    WM_SYSKEYDOWN = 0x0104

    def __init__(self):
        super().__init__()
        self._listener = None

    def start(self):
        if IS_WINDOWS:
            from pynput import keyboard
            self._listener = keyboard.Listener(
                on_press=lambda key: None,
                on_release=lambda key: None,
                win32_event_filter=self._filter,
            )
            self._listener.start()

    def stop(self):
        if self._listener:
            self._listener.stop()
            self._listener = None

    def _filter(self, msg, data):
        if data.vkCode == self.TOGGLE_VK:
            if msg in (self.WM_KEYDOWN, self.WM_SYSKEYDOWN):
                self.toggle_signal.emit()
            self._listener.suppress_event()


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

        self._hotkey = HotkeyListener()
        self._hotkey.toggle_signal.connect(self._on_hotkey_toggle)
        self._hotkey.start()

    def _on_hotkey_toggle(self):
        tab = self.tab_widget.currentWidget()
        if hasattr(tab, "_toggle"):
            tab._toggle.click()

    def closeEvent(self, event):
        self._hotkey.stop()
        super().closeEvent(event)
