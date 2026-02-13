import json
import sys
from pathlib import Path

from app.models.mapping_item import MappingItem


class MappingStore:
    def __init__(self, os_type: str):
        if getattr(sys, "frozen", False):
            base_dir = Path(sys.executable).parent
        else:
            base_dir = Path(__file__).resolve().parent.parent.parent
        self._config_dir = base_dir / "config"
        self._config_dir.mkdir(exist_ok=True)
        self._file_path = self._config_dir / f"{os_type}_mappings.json"
        self._mappings: list[MappingItem] = []
        self.load()

    def load(self):
        if self._file_path.exists():
            data = json.loads(self._file_path.read_text(encoding="utf-8"))
            self._mappings = [MappingItem.from_dict(item) for item in data]
        else:
            self._mappings = []

    def save(self):
        data = [item.to_dict() for item in self._mappings]
        self._file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def get_all(self) -> list[MappingItem]:
        return list(self._mappings)

    def add(self, item: MappingItem):
        self._mappings.append(item)
        self.save()

    def update(self, item: MappingItem):
        for i, existing in enumerate(self._mappings):
            if existing.id == item.id:
                self._mappings[i] = item
                break
        self.save()

    def delete(self, item_id: str):
        self._mappings = [m for m in self._mappings if m.id != item_id]
        self.save()

    def toggle(self, item_id: str):
        for item in self._mappings:
            if item.id == item_id:
                item.enabled = not item.enabled
                break
        self.save()
