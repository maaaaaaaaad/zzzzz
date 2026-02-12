from PySide6.QtCore import Signal
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
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(
            ["Active", "Input", "Output", "Edit", "Delete"]
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

    def refresh(self):
        mappings = self._store.get_all()
        self._table.setRowCount(len(mappings))

        for row, item in enumerate(mappings):
            checkbox = QCheckBox()
            checkbox.setChecked(item.enabled)
            checkbox.toggled.connect(lambda _, item_id=item.id: self._on_toggle(item_id))
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            self._table.setCellWidget(row, 0, checkbox_widget)

            source_text = item.source.display_name()
            self._table.setItem(row, 1, QTableWidgetItem(source_text))

            target_text = " + ".join(t.display_name() for t in item.target)
            self._table.setItem(row, 2, QTableWidgetItem(target_text))

            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda _, m=item: self.edit_requested.emit(m))
            self._table.setCellWidget(row, 3, edit_btn)

            del_btn = QPushButton("Delete")
            del_btn.clicked.connect(lambda _, item_id=item.id: self._on_delete(item_id))
            self._table.setCellWidget(row, 4, del_btn)

    def _on_toggle(self, item_id: str):
        self._store.toggle(item_id)
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
