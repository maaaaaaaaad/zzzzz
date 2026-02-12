from PySide6.QtCore import Signal
from PySide6.QtWidgets import QPushButton


class ToggleButton(QPushButton):
    toggled_state = Signal(bool)

    def __init__(self):
        super().__init__("Start")
        self._active = False
        self.setCheckable(True)
        self.setMinimumHeight(40)
        self._update_style()
        self.clicked.connect(self._on_clicked)

    def _on_clicked(self):
        self._active = self.isChecked()
        self._update_style()
        self.toggled_state.emit(self._active)

    def _update_style(self):
        if self._active:
            self.setText("Stop")
            self.setStyleSheet(
                "QPushButton { background-color: #e74c3c; color: white; "
                "font-weight: bold; font-size: 14px; border-radius: 6px; }"
            )
        else:
            self.setText("Start")
            self.setStyleSheet(
                "QPushButton { background-color: #2ecc71; color: white; "
                "font-weight: bold; font-size: 14px; border-radius: 6px; }"
            )

    @property
    def is_active(self) -> bool:
        return self._active
