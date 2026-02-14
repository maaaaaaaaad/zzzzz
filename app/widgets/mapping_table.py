from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QPushButton,
    QCheckBox,
    QMessageBox,
)

from app.store.mapping_store import MappingStore
from app.models.mapping_item import MappingItem


class MappingTable(QWidget):
    mapping_changed = Signal()
    edit_requested = Signal(MappingItem)
    add_requested = Signal()

    def __init__(self, store: MappingStore):
        super().__init__()
        self._store = store

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._table = QTableWidget()
        self._table.setColumnCount(9)
        self._table.setHorizontalHeaderLabels(
            ["Active", "Input", "Output", "Delay", "Turbo", "Loop", "Stop Key", "Edit", "Delete"]
        )
        self._table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self._table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.Stretch
        )
        self._table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        layout.addWidget(self._table)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        add_btn = QPushButton("Add Mapping")
        add_btn.clicked.connect(self.add_requested.emit)
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)

        self.refresh()

    def _make_centered_checkbox(self, checked: bool, callback) -> QWidget:
        checkbox = QCheckBox()
        checkbox.setChecked(checked)
        checkbox.toggled.connect(callback)
        widget = QWidget()
        box = QHBoxLayout(widget)
        box.addWidget(checkbox)
        box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box.setContentsMargins(0, 0, 0, 0)
        return widget

    def refresh(self):
        mappings = self._store.get_all()
        self._table.setRowCount(len(mappings))

        for row, item in enumerate(mappings):
            self._table.setCellWidget(
                row, 0,
                self._make_centered_checkbox(item.enabled, lambda _, iid=item.id: self._on_toggle(iid)),
            )

            self._table.setItem(row, 1, QTableWidgetItem(item.source.display_name()))

            target_text = " → ".join(t.display_name() for t in item.target)
            self._table.setItem(row, 2, QTableWidgetItem(target_text))

            delay_item = QTableWidgetItem(str(item.delay_ms))
            delay_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 3, delay_item)

            self._table.setCellWidget(
                row, 4,
                self._make_centered_checkbox(item.turbo, lambda _, iid=item.id: self._on_toggle_turbo(iid)),
            )

            self._table.setCellWidget(
                row, 5,
                self._make_centered_checkbox(item.loop, lambda _, iid=item.id: self._on_toggle_loop(iid)),
            )

            stop_text = item.stop_key.display_name() if item.stop_key else "-"
            stop_item = QTableWidgetItem(stop_text)
            stop_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 6, stop_item)

            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda _, m=item: self.edit_requested.emit(m))
            self._table.setCellWidget(row, 7, edit_btn)

            del_btn = QPushButton("Delete")
            del_btn.clicked.connect(lambda _, item_id=item.id: self._on_delete(item_id))
            self._table.setCellWidget(row, 8, del_btn)

    def _on_toggle(self, item_id: str):
        self._store.toggle(item_id)
        self.mapping_changed.emit()

    def _on_toggle_turbo(self, item_id: str):
        self._store.toggle_turbo(item_id)
        self.mapping_changed.emit()

    def _on_toggle_loop(self, item_id: str):
        self._store.toggle_loop(item_id)
        self.mapping_changed.emit()

    def _on_delete(self, item_id: str):
        reply = QMessageBox.question(
            self,
            "Delete Mapping",
            "Are you sure you want to delete this mapping?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._store.delete(item_id)
            self.refresh()
            self.mapping_changed.emit()
