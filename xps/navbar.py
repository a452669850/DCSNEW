from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDockWidget, QTreeView


class TreeDockWidget(QDockWidget):
    def __init__(self, parent=None):
        QDockWidget.__init__(self, parent=parent)
        tree = QTreeView(self)
        model = TreeDockModel()
        tree.setModel(model)
        self.setWidget(tree)
        tree.clicked.connect(self.onTreeClicked)

    def onTreeClicked(self, index: QModelIndex):
        pass


class TreeItem(object):
    def __init__(self):
        self.data = None
        self.parent = None
        self.children = []

    def appendChild(self, child: 'TreeItem') -> None:
        child.parent = self
        self.children.append(child)


class TreeDockModel(QAbstractItemModel):
    def __init__(self):
        QAbstractItemModel.__init__(self)
        self.rootItem = None
        self.updateData()

    def updateData(self):
        if self.rootItem:
            self.rootItem = None

        self.rootItem = TreeItem()
        self.rootItem.data = 'ROOT'

        for x in range(42):
            primary = TreeItem()
            primary.data = x
            primary.parent = self.rootItem
            self.rootItem.appendChild(primary)

    def data(self, index=QModelIndex(), role=Qt.DisplayRole):
        if not index.isValid():
            return None

        # 显示图标
        if role == Qt.DecorationRole and index.column() == 0:
            return QIcon()

        # 显示数据
        if role == Qt.DisplayRole:
            item: TreeItem = index.internalPointer()
            item.data = index.row()
            return item.data

        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.ItemIsAutoTristate
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsAutoTristate

    def index(self, row: int, column: int, parent=QModelIndex()) -> QModelIndex:
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem: TreeItem = self.rootItem
        else:
            parentItem: TreeItem = parent.internalPointer()

        if row < len(parentItem.children):
            childItem = parentItem.children[row]
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child = index.internalPointer()
        parent = child.parent

        if parent == self.rootItem:
            return QModelIndex()

        return self.createIndex(parent.row(), 0, parent)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 1

    def rowCount(self, parent=QModelIndex()) -> int:
        return 42
