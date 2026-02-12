from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class MacOSTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("macOS Keyboard Mapper (Intel / Apple Silicon)"))
        layout.addStretch()
