from dataclasses import dataclass


@dataclass
class InputEvent:
    event_type: str
    value: str
    duration_ms: int = 0

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "value": self.value,
            "duration_ms": self.duration_ms,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InputEvent":
        return cls(
            event_type=data["event_type"],
            value=data["value"],
            duration_ms=data.get("duration_ms", 0),
        )

    def display_name(self) -> str:
        if self.event_type == "mouse":
            names = {
                "mouse_left": "Mouse Left",
                "mouse_right": "Mouse Right",
                "mouse_middle": "Mouse Middle",
            }
            return names.get(self.value, self.value)
        if self.event_type == "hold":
            key_name = self.value.replace("_", " ").title()
            if self.duration_ms >= 1000:
                return f"Hold {key_name} {self.duration_ms // 1000}s"
            return f"Hold {key_name} {self.duration_ms}ms"
        if self.event_type == "sleep":
            if self.duration_ms >= 1000:
                return f"Wait {self.duration_ms // 1000}s"
            return f"Wait {self.duration_ms}ms"
        return self.value.replace("_", " ").title()
