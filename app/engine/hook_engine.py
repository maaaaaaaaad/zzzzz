import ctypes
import ctypes.wintypes
import platform
import threading
import time

from pynput import keyboard, mouse
from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button

from app.models.mapping_item import MappingItem

IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    INPUT_KEYBOARD = 1
    INPUT_MOUSE = 0
    KEYEVENTF_KEYUP = 0x0002
    MOUSEEVENTF_LEFTDOWN = 0x0002
    MOUSEEVENTF_LEFTUP = 0x0004
    MOUSEEVENTF_RIGHTDOWN = 0x0008
    MOUSEEVENTF_RIGHTUP = 0x0010
    MOUSEEVENTF_MIDDLEDOWN = 0x0020
    MOUSEEVENTF_MIDDLEUP = 0x0040

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ("dx", ctypes.wintypes.LONG),
            ("dy", ctypes.wintypes.LONG),
            ("mouseData", ctypes.wintypes.DWORD),
            ("dwFlags", ctypes.wintypes.DWORD),
            ("time", ctypes.wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
        ]

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", ctypes.wintypes.WORD),
            ("wScan", ctypes.wintypes.WORD),
            ("dwFlags", ctypes.wintypes.DWORD),
            ("time", ctypes.wintypes.DWORD),
            ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)),
        ]

    class INPUT_UNION(ctypes.Union):
        _fields_ = [
            ("mi", MOUSEINPUT),
            ("ki", KEYBDINPUT),
        ]

    class INPUT(ctypes.Structure):
        _fields_ = [
            ("type", ctypes.wintypes.DWORD),
            ("union", INPUT_UNION),
        ]

    def _send_key_event(vk: int, key_up: bool = False):
        inp = INPUT()
        inp.type = INPUT_KEYBOARD
        inp.union.ki.wVk = vk
        inp.union.ki.dwFlags = KEYEVENTF_KEYUP if key_up else 0
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

    def _send_mouse_event(flags: int):
        inp = INPUT()
        inp.type = INPUT_MOUSE
        inp.union.mi.dwFlags = flags
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

VK_MAP = {
    "a": 0x41, "b": 0x42, "c": 0x43, "d": 0x44, "e": 0x45,
    "f": 0x46, "g": 0x47, "h": 0x48, "i": 0x49, "j": 0x4A,
    "k": 0x4B, "l": 0x4C, "m": 0x4D, "n": 0x4E, "o": 0x4F,
    "p": 0x50, "q": 0x51, "r": 0x52, "s": 0x53, "t": 0x54,
    "u": 0x55, "v": 0x56, "w": 0x57, "x": 0x58, "y": 0x59, "z": 0x5A,
    "0": 0x30, "1": 0x31, "2": 0x32, "3": 0x33, "4": 0x34,
    "5": 0x35, "6": 0x36, "7": 0x37, "8": 0x38, "9": 0x39,
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
    "f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
    "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
    "escape": 0x1B, "tab": 0x09, "backspace": 0x08,
    "enter": 0x0D, "space": 0x20, "delete": 0x2E, "insert": 0x2D,
    "home": 0x24, "end": 0x23, "page_up": 0x21, "page_down": 0x22,
    "up": 0x26, "down": 0x28, "left": 0x25, "right": 0x27,
    "shift": 0x10, "ctrl": 0x11, "alt": 0x12, "meta": 0x5B,
    "caps_lock": 0x14, "num_lock": 0x90, "scroll_lock": 0x91,
    "print_screen": 0x2C, "pause": 0x13,
    "minus": 0xBD, "equal": 0xBB,
    "bracket_left": 0xDB, "bracket_right": 0xDD,
    "backslash": 0xDC, "semicolon": 0xBA, "apostrophe": 0xDE,
    "comma": 0xBC, "period": 0xBE, "slash": 0xBF, "grave": 0xC0,
    "num_0": 0x60, "num_1": 0x61, "num_2": 0x62, "num_3": 0x63,
    "num_4": 0x64, "num_5": 0x65, "num_6": 0x66, "num_7": 0x67,
    "num_8": 0x68, "num_9": 0x69,
    "num_multiply": 0x6A, "num_plus": 0x6B, "num_minus": 0x6D,
    "num_decimal": 0x6E, "num_divide": 0x6F, "num_enter": 0x0D,
}

MOUSE_DOWN_UP = {
    "mouse_left": (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP) if IS_WINDOWS else (None, None),
    "mouse_right": (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP) if IS_WINDOWS else (None, None),
    "mouse_middle": (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP) if IS_WINDOWS else (None, None),
}

PYNPUT_KEY_MAP = {
    "escape": Key.esc, "tab": Key.tab, "backspace": Key.backspace,
    "enter": Key.enter, "space": Key.space, "delete": Key.delete,
    "insert": Key.insert, "home": Key.home, "end": Key.end,
    "page_up": Key.page_up, "page_down": Key.page_down,
    "up": Key.up, "down": Key.down, "left": Key.left, "right": Key.right,
    "shift": Key.shift, "ctrl": Key.ctrl, "alt": Key.alt, "meta": Key.cmd,
    "caps_lock": Key.caps_lock, "num_lock": Key.num_lock,
    "scroll_lock": Key.scroll_lock,
    "f1": Key.f1, "f2": Key.f2, "f3": Key.f3, "f4": Key.f4,
    "f5": Key.f5, "f6": Key.f6, "f7": Key.f7, "f8": Key.f8,
    "f9": Key.f9, "f10": Key.f10, "f11": Key.f11, "f12": Key.f12,
}


def _value_to_pynput_key(value: str):
    if value in PYNPUT_KEY_MAP:
        return PYNPUT_KEY_MAP[value]
    if value.startswith("num_") and len(value) == 5 and value[4].isdigit():
        return KeyCode.from_vk(96 + int(value[4]))
    if len(value) == 1:
        return KeyCode.from_char(value)
    return None


def _normalize_key(key) -> str | None:
    if isinstance(key, Key):
        name_map = {
            Key.esc: "escape", Key.tab: "tab", Key.backspace: "backspace",
            Key.enter: "enter", Key.space: "space", Key.delete: "delete",
            Key.insert: "insert", Key.home: "home", Key.end: "end",
            Key.page_up: "page_up", Key.page_down: "page_down",
            Key.up: "up", Key.down: "down", Key.left: "left", Key.right: "right",
            Key.shift: "shift", Key.shift_l: "shift", Key.shift_r: "shift",
            Key.ctrl: "ctrl", Key.ctrl_l: "ctrl", Key.ctrl_r: "ctrl",
            Key.alt: "alt", Key.alt_l: "alt", Key.alt_r: "alt",
            Key.cmd: "meta", Key.cmd_l: "meta", Key.cmd_r: "meta",
            Key.caps_lock: "caps_lock", Key.num_lock: "num_lock",
            Key.scroll_lock: "scroll_lock",
            Key.f1: "f1", Key.f2: "f2", Key.f3: "f3", Key.f4: "f4",
            Key.f5: "f5", Key.f6: "f6", Key.f7: "f7", Key.f8: "f8",
            Key.f9: "f9", Key.f10: "f10", Key.f11: "f11", Key.f12: "f12",
        }
        return name_map.get(key)
    if isinstance(key, KeyCode):
        if key.vk and 96 <= key.vk <= 105:
            return f"num_{key.vk - 96}"
        if key.vk == 106:
            return "num_multiply"
        if key.vk == 107:
            return "num_plus"
        if key.vk == 109:
            return "num_minus"
        if key.vk == 110:
            return "num_decimal"
        if key.vk == 111:
            return "num_divide"
        if key.char:
            return key.char.lower()
    return None


class HookEngine:
    def __init__(self):
        self._mappings: list[MappingItem] = []
        self._keyboard_listener: keyboard.Listener | None = None
        self._mouse_listener: mouse.Listener | None = None
        self._running = False
        self._suppressed_keys: set[str] = set()

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self, mappings: list[MappingItem]):
        if self._running:
            self.stop()

        self._mappings = [m for m in mappings if m.enabled]
        self._suppressed_keys = set()

        keyboard_sources = {
            m.source.value for m in self._mappings if m.source.event_type == "keyboard"
        }
        mouse_sources = {
            m.source.value for m in self._mappings if m.source.event_type == "mouse"
        }

        if keyboard_sources:
            self._keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release,
                suppress=True,
            )
            self._keyboard_listener.start()

        if mouse_sources:
            self._mouse_listener = mouse.Listener(
                on_click=self._on_mouse_click,
            )
            self._mouse_listener.start()

        self._running = True

    def stop(self):
        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None
        self._running = False

    def _on_key_press(self, key, injected=False):
        if injected:
            return

        normalized = _normalize_key(key)
        if normalized is None:
            return

        mapping = self._find_keyboard_mapping(normalized)
        if mapping:
            self._suppressed_keys.add(normalized)
            threading.Thread(
                target=self._execute_target, args=(mapping,), daemon=True
            ).start()
            return

        if IS_WINDOWS:
            vk = VK_MAP.get(normalized)
            if vk:
                _send_key_event(vk)
        else:
            pynput_key = _value_to_pynput_key(normalized)
            if pynput_key:
                keyboard.Controller().press(pynput_key)

    def _on_key_release(self, key, injected=False):
        if injected:
            return

        normalized = _normalize_key(key)
        if normalized is None:
            return

        if normalized in self._suppressed_keys:
            self._suppressed_keys.discard(normalized)
            return

        if IS_WINDOWS:
            vk = VK_MAP.get(normalized)
            if vk:
                _send_key_event(vk, key_up=True)
        else:
            pynput_key = _value_to_pynput_key(normalized)
            if pynput_key:
                keyboard.Controller().release(pynput_key)

    def _on_mouse_click(self, x, y, button, pressed, injected=False):
        if injected:
            return

        button_map = {
            Button.left: "mouse_left",
            Button.right: "mouse_right",
            Button.middle: "mouse_middle",
        }
        value = button_map.get(button)
        if value and pressed:
            mapping = self._find_mouse_mapping(value)
            if mapping:
                threading.Thread(
                    target=self._execute_target, args=(mapping,), daemon=True
                ).start()

    def _find_keyboard_mapping(self, value: str) -> MappingItem | None:
        for m in self._mappings:
            if m.source.event_type == "keyboard" and m.source.value == value:
                return m
        return None

    def _find_mouse_mapping(self, value: str) -> MappingItem | None:
        for m in self._mappings:
            if m.source.event_type == "mouse" and m.source.value == value:
                return m
        return None

    def _execute_target(self, mapping: MappingItem):
        delay = 0.1
        for i, event in enumerate(mapping.target):
            if i > 0:
                time.sleep(delay)
            if event.event_type == "keyboard":
                vk = VK_MAP.get(event.value)
                if vk and IS_WINDOWS:
                    _send_key_event(vk)
                    time.sleep(0.03)
                    _send_key_event(vk, key_up=True)
            elif event.event_type == "mouse":
                down_up = MOUSE_DOWN_UP.get(event.value)
                if down_up and down_up[0] and IS_WINDOWS:
                    _send_mouse_event(down_up[0])
                    time.sleep(0.03)
                    _send_mouse_event(down_up[1])
