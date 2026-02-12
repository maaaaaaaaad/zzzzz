from dataclasses import dataclass


@dataclass
class InputEvent:
    event_type: str
    value: str

    def to_dict(self) -> dict:
        return {"event_type": self.event_type, "value": self.value}

    @classmethod
    def from_dict(cls, data: dict) -> "InputEvent":
        return cls(event_type=data["event_type"], value=data["value"])

    def display_name(self) -> str:
        if self.event_type == "mouse":
            names = {
                "mouse_left": "Mouse Left",
                "mouse_right": "Mouse Right",
                "mouse_middle": "Mouse Middle",
            }
            return names.get(self.value, self.value)
        return self.value.replace("_", " ").title()
