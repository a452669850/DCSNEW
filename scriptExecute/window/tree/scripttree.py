from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtWidgets import QGroupBox, QTreeView, QVBoxLayout

from utils.ClientModels import Script


class TreeGroup(QGroupBox):
    tree_Signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        QGroupBox.__init__(self, parent=parent)
        self.parent = parent
        self.tree = QTreeView(self)
        self.tree.setHeaderHidden(True)
        self.model = ScriptTree()
        self.tree.setModel(self.model)
        layout = QVBoxLayout(self)
        layout.addWidget(self.tree)
        self.setLayout(layout)
        self.tree.clicked.connect(self.onTreeClicked)

    def onTreeClicked(self, index: QModelIndex):
        if index.parent().data() not in [self.parent, None]:
            if len(index.data()) > 1:
                self.tree_Signal.emit(index.data())

    def refreshTree(self):
        self.model.updateData()
        self.tree.expandAll()

class TreeItem(object):
    def __init__(self):
        self.data = None
        self.parent = None
        self.children = []

    def appendChild(self, child: 'TreeItem') -> None:
        child.parent = self
        self.children.append(child)


class ScriptTree(QAbstractItemModel):
    def __init__(self):
        QAbstractItemModel.__init__(self)
        self.rootItem = None
        self.updateData()

    def updateData(self):
        if self.rootItem:
            self.rootItem = None

        self.rootItem = TreeItem()
        self.rootItem.data = 'ROOT'
        self.projectRoot = TreeItem()
        self.projectRoot.data = '时间响应脚本'
        self.rootItem.appendChild(self.projectRoot)

        data = [i.serial for i in Script.select()]
        for x in data:
            primary = TreeItem()
            primary.data = x
            primary.parent = self.rootItem
            self.projectRoot.appendChild(primary)
            self.addChild(x, primary)
        self.layoutChanged.emit()

    def addChild(self, tabelName, parent):
        allList = [i.name for i in Script.select().where(Script.serial == tabelName)]
        if allList:
            for i in allList:
                child = TreeItem()
                child.data = i
                child.parent = parent
                parent.appendChild(child)
        else:
            return

    def data(self, index=QModelIndex(), role=Qt.DisplayRole):
        if not index.isValid():
            return None

        # 显示数据
        if role == Qt.DisplayRole:
            item: TreeItem = index.internalPointer()
            item.data = index.internalPointer().data
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

        return self.createIndex(index.row(), 0, parent)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 1

    def rowCount(self, parent=QModelIndex()) -> int:
        return 999


def Duplicate_Removal(data):
    lis = []
    for i in data:
        if i not in lis:
            lis.append(i)
    return lis
