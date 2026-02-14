from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent, QMouseEvent
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QSpinBox,
    QCheckBox,
)

from app.models.input_event import InputEvent
from app.models.mapping_item import MappingItem

KEY_MAP = {
    Qt.Key.Key_A: "a", Qt.Key.Key_B: "b", Qt.Key.Key_C: "c",
    Qt.Key.Key_D: "d", Qt.Key.Key_E: "e", Qt.Key.Key_F: "f",
    Qt.Key.Key_G: "g", Qt.Key.Key_H: "h", Qt.Key.Key_I: "i",
    Qt.Key.Key_J: "j", Qt.Key.Key_K: "k", Qt.Key.Key_L: "l",
    Qt.Key.Key_M: "m", Qt.Key.Key_N: "n", Qt.Key.Key_O: "o",
    Qt.Key.Key_P: "p", Qt.Key.Key_Q: "q", Qt.Key.Key_R: "r",
    Qt.Key.Key_S: "s", Qt.Key.Key_T: "t", Qt.Key.Key_U: "u",
    Qt.Key.Key_V: "v", Qt.Key.Key_W: "w", Qt.Key.Key_X: "x",
    Qt.Key.Key_Y: "y", Qt.Key.Key_Z: "z",
    Qt.Key.Key_0: "0", Qt.Key.Key_1: "1", Qt.Key.Key_2: "2",
    Qt.Key.Key_3: "3", Qt.Key.Key_4: "4", Qt.Key.Key_5: "5",
    Qt.Key.Key_6: "6", Qt.Key.Key_7: "7", Qt.Key.Key_8: "8",
    Qt.Key.Key_9: "9",
    Qt.Key.Key_F1: "f1", Qt.Key.Key_F2: "f2", Qt.Key.Key_F3: "f3",
    Qt.Key.Key_F4: "f4", Qt.Key.Key_F5: "f5", Qt.Key.Key_F6: "f6",
    Qt.Key.Key_F7: "f7", Qt.Key.Key_F8: "f8", Qt.Key.Key_F9: "f9",
    Qt.Key.Key_F10: "f10", Qt.Key.Key_F11: "f11", Qt.Key.Key_F12: "f12",
    Qt.Key.Key_Escape: "escape", Qt.Key.Key_Tab: "tab",
    Qt.Key.Key_Backspace: "backspace", Qt.Key.Key_Return: "enter",
    Qt.Key.Key_Enter: "enter", Qt.Key.Key_Space: "space",
    Qt.Key.Key_Delete: "delete", Qt.Key.Key_Insert: "insert",
    Qt.Key.Key_Home: "home", Qt.Key.Key_End: "end",
    Qt.Key.Key_PageUp: "page_up", Qt.Key.Key_PageDown: "page_down",
    Qt.Key.Key_Up: "up", Qt.Key.Key_Down: "down",
    Qt.Key.Key_Left: "left", Qt.Key.Key_Right: "right",
    Qt.Key.Key_CapsLock: "caps_lock", Qt.Key.Key_NumLock: "num_lock",
    Qt.Key.Key_ScrollLock: "scroll_lock", Qt.Key.Key_Print: "print_screen",
    Qt.Key.Key_Pause: "pause",
    Qt.Key.Key_Shift: "shift", Qt.Key.Key_Control: "ctrl",
    Qt.Key.Key_Alt: "alt", Qt.Key.Key_Meta: "meta",
    Qt.Key.Key_Minus: "minus", Qt.Key.Key_Equal: "equal",
    Qt.Key.Key_BracketLeft: "bracket_left",
    Qt.Key.Key_BracketRight: "bracket_right",
    Qt.Key.Key_Backslash: "backslash", Qt.Key.Key_Semicolon: "semicolon",
    Qt.Key.Key_Apostrophe: "apostrophe", Qt.Key.Key_Comma: "comma",
    Qt.Key.Key_Period: "period", Qt.Key.Key_Slash: "slash",
    Qt.Key.Key_QuoteLeft: "grave",
}

NUMPAD_MAP = {
    Qt.Key.Key_0: "num_0", Qt.Key.Key_1: "num_1", Qt.Key.Key_2: "num_2",
    Qt.Key.Key_3: "num_3", Qt.Key.Key_4: "num_4", Qt.Key.Key_5: "num_5",
    Qt.Key.Key_6: "num_6", Qt.Key.Key_7: "num_7", Qt.Key.Key_8: "num_8",
    Qt.Key.Key_9: "num_9", Qt.Key.Key_Asterisk: "num_multiply",
    Qt.Key.Key_Plus: "num_plus", Qt.Key.Key_Minus: "num_minus",
    Qt.Key.Key_Period: "num_decimal", Qt.Key.Key_Slash: "num_divide",
    Qt.Key.Key_Enter: "num_enter",
}

MOUSE_BUTTON_MAP = {
    Qt.MouseButton.LeftButton: "mouse_left",
    Qt.MouseButton.RightButton: "mouse_right",
    Qt.MouseButton.MiddleButton: "mouse_middle",
}


class KeyCaptureButton(QPushButton):
    def __init__(self, label: str = "Click to set key...", single: bool = False):
        super().__init__(label)
        self._capturing = False
        self._events: list[InputEvent] = []
        self._single = single
        self.clicked.connect(self._start_capture)

    def _start_capture(self):
        self._capturing = True
        self._events = []
        if self._single:
            self.setText("Press a key or mouse button...")
        else:
            self.setText("Press keys in sequence... (Esc to finish)")
        self.setFocus()

    def _stop_capture(self):
        self._capturing = False
        if self._events:
            self.setText(" → ".join(e.display_name() for e in self._events))
        else:
            self.setText("Click to set key...")

    def get_events(self) -> list[InputEvent]:
        return list(self._events)

    def set_events(self, events: list[InputEvent]):
        self._events = list(events)
        if events:
            self.setText(" → ".join(e.display_name() for e in events))
        else:
            self.setText("Click to set key...")

    def clear_events(self):
        self._events = []
        self._capturing = False
        self.setText("Click to set key...")

    def keyPressEvent(self, event: QKeyEvent):
        if not self._capturing:
            super().keyPressEvent(event)
            return

        if event.isAutoRepeat():
            return

        key = event.key()

        if key == Qt.Key.Key_Escape:
            self._stop_capture()
            return

        is_numpad = bool(event.modifiers() & Qt.KeyboardModifier.KeypadModifier)

        if is_numpad and key in NUMPAD_MAP:
            value = NUMPAD_MAP[key]
        elif key in KEY_MAP:
            value = KEY_MAP[key]
        else:
            return

        self._events.append(InputEvent(event_type="keyboard", value=value))
        self.setText(" → ".join(e.display_name() for e in self._events))

        if self._single:
            self._stop_capture()

    def keyReleaseEvent(self, event: QKeyEvent):
        if not self._capturing:
            super().keyReleaseEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if not self._capturing:
            super().mousePressEvent(event)
            return

        button = event.button()
        if button in MOUSE_BUTTON_MAP:
            value = MOUSE_BUTTON_MAP[button]
            self._events.append(InputEvent(event_type="mouse", value=value))
            self.setText(" → ".join(e.display_name() for e in self._events))

            if self._single:
                self._stop_capture()


PRESETS = {
    "shift_arrow_turbo": {
        "target": [
            InputEvent(event_type="keyboard", value="shift"),
            InputEvent(event_type="keyboard", value="up"),
            InputEvent(event_type="keyboard", value="down"),
            InputEvent(event_type="keyboard", value="left"),
            InputEvent(event_type="keyboard", value="right"),
        ],
        "turbo": True,
        "loop": True,
        "delay_ms": 0,
    },
}


class MappingDialog(QDialog):
    def __init__(self, parent=None, mapping: MappingItem | None = None, preset: str | None = None):
        super().__init__(parent)
        self.setWindowTitle("Edit Mapping" if mapping else "Add Mapping")
        self.setMinimumWidth(400)
        self._result_mapping: MappingItem | None = None
        self._preset_loop = False

        layout = QVBoxLayout(self)

        source_group = QGroupBox("Input (Source)")
        source_layout = QVBoxLayout(source_group)
        self._source_btn = KeyCaptureButton()
        source_layout.addWidget(self._source_btn)
        layout.addWidget(source_group)

        target_group = QGroupBox("Output (Target)")
        target_layout = QVBoxLayout(target_group)
        self._target_btn = KeyCaptureButton()
        target_layout.addWidget(self._target_btn)
        layout.addWidget(target_group)

        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout(options_group)

        delay_layout = QHBoxLayout()
        delay_layout.addWidget(QLabel("Delay between keys:"))
        self._delay_spin = QSpinBox()
        self._delay_spin.setRange(0, 99999)
        self._delay_spin.setSuffix(" ms")
        self._delay_spin.setValue(0)
        delay_layout.addWidget(self._delay_spin)
        options_layout.addLayout(delay_layout)

        self._turbo_check = QCheckBox("Turbo")
        self._turbo_check.toggled.connect(self._on_turbo_toggled)
        options_layout.addWidget(self._turbo_check)

        layout.addWidget(options_group)

        stop_key_group = QGroupBox("Loop Stop Key")
        stop_key_layout = QHBoxLayout(stop_key_group)
        self._stop_key_btn = KeyCaptureButton(single=True)
        stop_key_layout.addWidget(self._stop_key_btn)
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._stop_key_btn.clear_events)
        stop_key_layout.addWidget(clear_btn)
        layout.addWidget(stop_key_group)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self._on_ok)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

        if mapping:
            self._editing_id = mapping.id
            self._source_btn.set_events([mapping.source])
            self._target_btn.set_events(mapping.target)
            self._delay_spin.setValue(mapping.delay_ms)
            self._turbo_check.setChecked(mapping.turbo)
            if mapping.stop_key:
                self._stop_key_btn.set_events([mapping.stop_key])
        else:
            self._editing_id = None

        if preset and preset in PRESETS:
            p = PRESETS[preset]
            self._target_btn.set_events(p["target"])
            self._turbo_check.setChecked(p["turbo"])
            self._delay_spin.setValue(p["delay_ms"])
            self._preset_loop = p.get("loop", False)

    def _on_turbo_toggled(self, checked: bool):
        self._delay_spin.setEnabled(not checked)

    def _on_ok(self):
        source_events = self._source_btn.get_events()
        target_events = self._target_btn.get_events()

        if not source_events or not target_events:
            return

        stop_key_events = self._stop_key_btn.get_events()
        stop_key = stop_key_events[0] if stop_key_events else None

        self._result_mapping = MappingItem(
            source=source_events[0],
            target=target_events,
            id=self._editing_id or MappingItem(
                source=source_events[0], target=target_events
            ).id,
            delay_ms=self._delay_spin.value(),
            turbo=self._turbo_check.isChecked(),
            loop=self._preset_loop,
            stop_key=stop_key,
        )
        self.accept()

    def get_mapping(self) -> MappingItem | None:
        return self._result_mapping
