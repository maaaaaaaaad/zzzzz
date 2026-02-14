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

    ULONG_PTR = ctypes.c_ulonglong if ctypes.sizeof(ctypes.c_void_p) == 8 else ctypes.c_ulong
    INJECTED_MARKER = 0xDEAD

    class MOUSEINPUT(ctypes.Structure):
        _fields_ = [
            ("dx", ctypes.c_long),
            ("dy", ctypes.c_long),
            ("mouseData", ctypes.c_ulong),
            ("dwFlags", ctypes.c_ulong),
            ("time", ctypes.c_ulong),
            ("dwExtraInfo", ULONG_PTR),
        ]

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [
            ("wVk", ctypes.c_ushort),
            ("wScan", ctypes.c_ushort),
            ("dwFlags", ctypes.c_ulong),
            ("time", ctypes.c_ulong),
            ("dwExtraInfo", ULONG_PTR),
        ]

    class HARDWAREINPUT(ctypes.Structure):
        _fields_ = [
            ("uMsg", ctypes.c_ulong),
            ("wParamL", ctypes.c_ushort),
            ("wParamH", ctypes.c_ushort),
        ]

    class INPUT_UNION(ctypes.Union):
        _fields_ = [
            ("mi", MOUSEINPUT),
            ("ki", KEYBDINPUT),
            ("hi", HARDWAREINPUT),
        ]

    class INPUT(ctypes.Structure):
        _fields_ = [
            ("type", ctypes.c_ulong),
            ("union", INPUT_UNION),
        ]

    def _send_key_event(vk: int, key_up: bool = False):
        inp = INPUT()
        inp.type = INPUT_KEYBOARD
        inp.union.ki.wVk = vk
        inp.union.ki.dwFlags = KEYEVENTF_KEYUP if key_up else 0
        inp.union.ki.dwExtraInfo = INJECTED_MARKER
        ctypes.windll.user32.SendInput(1, ctypes.byref(inp), ctypes.sizeof(INPUT))

    def _send_mouse_event(flags: int):
        inp = INPUT()
        inp.type = INPUT_MOUSE
        inp.union.mi.dwFlags = flags
        inp.union.mi.dwExtraInfo = INJECTED_MARKER
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


TURBO_INTERVAL = 0.01


class HookEngine:
    WM_KEYDOWN = 0x0100
    WM_SYSKEYDOWN = 0x0104

    def __init__(self):
        self._mappings: list[MappingItem] = []
        self._keyboard_listener: keyboard.Listener | None = None
        self._mouse_listener: mouse.Listener | None = None
        self._running = False
        self._vk_to_mapping: dict[int, MappingItem] = {}
        self._loop_events: dict[str, threading.Event] = {}
        self._stop_vk_to_mapping_id: dict[int, str] = {}
        self._stop_mouse_to_mapping_id: dict[str, str] = {}

    @property
    def is_running(self) -> bool:
        return self._running

    VK_VARIANTS = {
        0x10: [0xA0, 0xA1],
        0x11: [0xA2, 0xA3],
        0x12: [0xA4, 0xA5],
    }

    def _register_vk(self, vk: int, value):
        self._vk_to_mapping[vk] = value
        for variant in self.VK_VARIANTS.get(vk, []):
            self._vk_to_mapping[variant] = value

    def _register_stop_vk(self, vk: int, mapping_id: str):
        self._stop_vk_to_mapping_id[vk] = mapping_id
        for variant in self.VK_VARIANTS.get(vk, []):
            self._stop_vk_to_mapping_id[variant] = mapping_id

    def start(self, mappings: list[MappingItem]):
        if self._running:
            self.stop()

        self._mappings = [m for m in mappings if m.enabled]
        self._loop_events = {}
        self._stop_vk_to_mapping_id = {}
        self._stop_mouse_to_mapping_id = {}

        mouse_sources = {
            m.source.value for m in self._mappings if m.source.event_type == "mouse"
        }

        self._vk_to_mapping = {}
        for m in self._mappings:
            if m.source.event_type == "keyboard":
                vk = VK_MAP.get(m.source.value)
                if vk:
                    self._register_vk(vk, m)

            if m.stop_key:
                if m.stop_key.event_type == "keyboard":
                    stop_vk = VK_MAP.get(m.stop_key.value)
                    if stop_vk:
                        self._register_stop_vk(stop_vk, m.id)
                elif m.stop_key.event_type == "mouse":
                    self._stop_mouse_to_mapping_id[m.stop_key.value] = m.id

        need_keyboard = bool(self._vk_to_mapping) or bool(self._stop_vk_to_mapping_id)
        need_mouse = bool(mouse_sources) or bool(self._stop_mouse_to_mapping_id)

        if need_keyboard:
            self._keyboard_listener = keyboard.Listener(
                on_press=lambda key: None,
                on_release=lambda key: None,
                win32_event_filter=self._win32_filter,
            )
            self._keyboard_listener.start()

        if need_mouse:
            self._mouse_listener = mouse.Listener(
                on_click=self._on_mouse_click,
            )
            self._mouse_listener.start()

        self._running = True

    def stop(self):
        for event in self._loop_events.values():
            event.set()
        self._loop_events.clear()

        if self._keyboard_listener:
            self._keyboard_listener.stop()
            self._keyboard_listener = None
        if self._mouse_listener:
            self._mouse_listener.stop()
            self._mouse_listener = None
        self._running = False

    def _win32_filter(self, msg, data):
        if IS_WINDOWS and data.dwExtraInfo == INJECTED_MARKER:
            return

        vk = data.vkCode

        if vk in self._stop_vk_to_mapping_id:
            if msg in (self.WM_KEYDOWN, self.WM_SYSKEYDOWN):
                mapping_id = self._stop_vk_to_mapping_id[vk]
                if mapping_id in self._loop_events:
                    self._loop_events[mapping_id].set()
            self._keyboard_listener.suppress_event()

        if vk in self._vk_to_mapping:
            if msg in (self.WM_KEYDOWN, self.WM_SYSKEYDOWN):
                mapping = self._vk_to_mapping[vk]
                self._trigger_mapping(mapping)
            self._keyboard_listener.suppress_event()

    def _on_mouse_click(self, x, y, button, pressed, injected=False):
        if injected:
            return

        button_map = {
            Button.left: "mouse_left",
            Button.right: "mouse_right",
            Button.middle: "mouse_middle",
        }
        value = button_map.get(button)
        if not value or not pressed:
            return

        if value in self._stop_mouse_to_mapping_id:
            mapping_id = self._stop_mouse_to_mapping_id[value]
            if mapping_id in self._loop_events:
                self._loop_events[mapping_id].set()
                return

        mapping = self._find_mouse_mapping(value)
        if mapping:
            self._trigger_mapping(mapping)

    def _trigger_mapping(self, mapping: MappingItem):
        if mapping.loop:
            if mapping.id in self._loop_events:
                return
            stop_event = threading.Event()
            self._loop_events[mapping.id] = stop_event
            threading.Thread(
                target=self._execute_loop, args=(mapping, stop_event), daemon=True
            ).start()
        else:
            threading.Thread(
                target=self._execute_target, args=(mapping,), daemon=True
            ).start()

    def _execute_loop(self, mapping: MappingItem, stop_event: threading.Event):
        delay = TURBO_INTERVAL if mapping.turbo else max(mapping.delay_ms / 1000, TURBO_INTERVAL)
        while not stop_event.is_set():
            self._execute_target(mapping)
            if stop_event.wait(delay):
                break
        self._loop_events.pop(mapping.id, None)

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
        MODIFIER_KEYS = {"shift", "ctrl", "alt", "meta"}

        if mapping.turbo:
            action_delay = TURBO_INTERVAL
        elif mapping.delay_ms > 0:
            action_delay = mapping.delay_ms / 1000
        else:
            action_delay = 0.05

        modifiers = []
        actions = []
        for event in mapping.target:
            if event.event_type == "keyboard" and event.value in MODIFIER_KEYS:
                modifiers.append(event)
            else:
                actions.append(event)

        if IS_WINDOWS:
            for mod in modifiers:
                vk = VK_MAP.get(mod.value)
                if vk:
                    _send_key_event(vk)
                    time.sleep(0.02)

            for i, event in enumerate(actions):
                if i > 0:
                    time.sleep(action_delay)
                if event.event_type == "keyboard":
                    vk = VK_MAP.get(event.value)
                    if vk:
                        _send_key_event(vk)
                        time.sleep(0.03)
                        _send_key_event(vk, key_up=True)
                elif event.event_type == "mouse":
                    down_up = MOUSE_DOWN_UP.get(event.value)
                    if down_up and down_up[0]:
                        _send_mouse_event(down_up[0])
                        time.sleep(0.03)
                        _send_mouse_event(down_up[1])

            for mod in reversed(modifiers):
                vk = VK_MAP.get(mod.value)
                if vk:
                    time.sleep(0.02)
                    _send_key_event(vk, key_up=True)
