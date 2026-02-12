from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

from app.store.mapping_store import MappingStore
from app.widgets.mapping_table import MappingTable
from app.widgets.mapping_dialog import MappingDialog
from app.widgets.toggle_button import ToggleButton
from app.engine.hook_engine import HookEngine
from app.models.mapping_item import MappingItem


class WindowsTab(QWidget):
    def __init__(self):
        super().__init__()

        self._store = MappingStore(os_type="windows")
        self._engine = HookEngine()

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Windows 11 Keyboard Mapper"))

        self._toggle = ToggleButton()
        self._toggle.toggled_state.connect(self._on_toggle)
        layout.addWidget(self._toggle)

        self._table = MappingTable(self._store)
        self._table.add_requested.connect(self._on_add)
        self._table.edit_requested.connect(self._on_edit)
        self._table.mapping_changed.connect(self._on_mapping_changed)
        layout.addWidget(self._table)

    def _on_toggle(self, active: bool):
        if active:
            self._engine.start(self._store.get_all())
            self.window().statusBar().showMessage("Running")
        else:
            self._engine.stop()
            self.window().statusBar().showMessage("Stopped")

    def _on_add(self):
        dialog = MappingDialog(self)
        if dialog.exec():
            mapping = dialog.get_mapping()
            if mapping:
                self._store.add(mapping)
                self._table.refresh()
                self._restart_engine_if_running()

    def _on_edit(self, mapping: MappingItem):
        dialog = MappingDialog(self, mapping=mapping)
        if dialog.exec():
            updated = dialog.get_mapping()
            if updated:
                self._store.update(updated)
                self._table.refresh()
                self._restart_engine_if_running()

    def _on_mapping_changed(self):
        self._restart_engine_if_running()

    def _restart_engine_if_running(self):
        if self._engine.is_running:
            self._engine.stop()
            self._engine.start(self._store.get_all())
