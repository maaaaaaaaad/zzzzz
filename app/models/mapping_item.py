from dataclasses import dataclass, field
from uuid import uuid4

from app.models.input_event import InputEvent


@dataclass
class MappingItem:
    source: InputEvent
    target: list[InputEvent]
    enabled: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source.to_dict(),
            "target": [t.to_dict() for t in self.target],
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MappingItem":
        return cls(
            id=data["id"],
            source=InputEvent.from_dict(data["source"]),
            target=[InputEvent.from_dict(t) for t in data["target"]],
            enabled=data["enabled"],
        )
