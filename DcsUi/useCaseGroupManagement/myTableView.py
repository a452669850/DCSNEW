from PyQt5.QtWidgets import QTableView, QAbstractItemView, QHeaderView


class tableView(QTableView):

    def __init__(self, *args, **kwargs):
        QTableView.__init__(self, *args, **kwargs)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)

        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def dragEnterEvent(self, event):
        """拖拽函数"""
        position = event.pos()
        self.source_first = self.indexAt(position).row()
        self.source_first_index = self.indexAt(position)
        event.accept()

    def dropEvent(self, event):
        """删除"""
        position = event.pos()
        self.source_last = self.indexAt(position).row()
        self.source_last_index = self.indexAt(position)
        self.model().moveRow(self.source_first_index, self.source_first, self.source_last_index, self.source_last)
