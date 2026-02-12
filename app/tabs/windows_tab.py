from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class WindowsTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Windows 11 Keyboard Mapper"))
        layout.addStretch()
