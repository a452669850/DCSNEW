from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtWidgets import QDockWidget, QTreeView

treeDict = {
    '系统参数': 'sysParameter',
    '通讯设备': 'comEqu',
    '数据库配置': {
        '设备变量': 'deviceVar',
        '中间变量': 'intermediateVar',
        '系统变量': 'deviceVar'
    },
    '数据库管理': 'databaseManage'
}

class TreeDockWidget(QDockWidget):
    tree_Signal = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        QDockWidget.__init__(self, parent=parent)
        self.parent = parent
        tree = QTreeView(self)
        tree.setHeaderHidden(True)
        model = TreeDockModel()
        tree.setModel(model)
        self.setWidget(tree)
        tree.clicked.connect(self.onTreeClicked)

    def onTreeClicked(self, index: QModelIndex):
        if index.parent().data() not in [self.parent, None]:
            for i in treeDict:
                if isinstance(treeDict[i], (dict)):
                    for name in treeDict[i]:
                        if name == index.data():
                            self.tree_Signal.emit(treeDict[i][name])
                else:
                    if i == index.data():
                        self.tree_Signal.emit(treeDict[i])


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
        self.projectRoot = TreeItem()
        self.projectRoot.data = '工程'
        self.rootItem.appendChild(self.projectRoot)

        for x in ['系统参数', '通讯设备', '数据库配置', '数据库管理', ]:
            primary = TreeItem()
            primary.data = x
            primary.parent = self.rootItem
            self.projectRoot.appendChild(primary)
            self.addChild(x, primary)
        self.layoutChanged.emit()

    def addChild(self, tabelName, parent):
        allList = treeDict[tabelName]
        if isinstance(allList, (dict)):
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

        # 显示图标
        # if role == Qt.DecorationRole and index.column() == 0:
        #     return QIcon()

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
