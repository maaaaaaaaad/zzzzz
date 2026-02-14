from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from app.models.input_event import InputEvent


@dataclass
class MappingItem:
    source: InputEvent
    target: list[InputEvent]
    enabled: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))
    delay_ms: int = 0
    turbo: bool = False
    loop: bool = False
    stop_key: InputEvent | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source.to_dict(),
            "target": [t.to_dict() for t in self.target],
            "enabled": self.enabled,
            "delay_ms": self.delay_ms,
            "turbo": self.turbo,
            "loop": self.loop,
            "stop_key": self.stop_key.to_dict() if self.stop_key else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> MappingItem:
        stop_key_data = data.get("stop_key")
        return cls(
            id=data["id"],
            source=InputEvent.from_dict(data["source"]),
            target=[InputEvent.from_dict(t) for t in data["target"]],
            enabled=data.get("enabled", True),
            delay_ms=data.get("delay_ms", 0),
            turbo=data.get("turbo", False),
            loop=data.get("loop", False),
            stop_key=InputEvent.from_dict(stop_key_data) if stop_key_data else None,
        )
