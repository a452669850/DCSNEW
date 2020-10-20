import typing
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDockWidget, QTreeView
from DcsUi.DockCLass import NewDockWidget
from utils.WorkModels import PointGroup
from procedure.run_procedure.RunProceduree import ProcedureThread
from static.Png import *


class VarTreeDockWidget(NewDockWidget):
    def __init__(self, title, parent = None):
        NewDockWidget.__init__(self, title, parent=parent)
        self.parent = parent
        tree = QTreeView(self)
        # 隐藏标题栏
        tree.setHeaderHidden(True)
        self.model = VarTreeDockModel(self.parent)
        tree.setModel(self.model)
        self.setWidget(tree)
        tree.expandAll()
        tree.doubleClicked.connect(self.onTreeClicked)

    def onTreeClicked(self, index: QModelIndex):
        groupName = index.data()
        if groupName not in ['强制变量组', None]:
            groupId = PointGroup.get_all().where(PointGroup.group_name == index.data())[0].id
            self.parent.group = groupName
            self.parent.dockTop.addVar([groupId, groupName])

    def refreshTree(self):
        self.model.updateData()

class TreeItem(object):
    # 重写树item类
    def __init__(self):
        self.children = []
    
    def appendChild(self, child: 'TreeItem') -> None:
        child.parent = self
        self.children.append(child)

class VarTreeDockModel(QAbstractItemModel):
    def __init__(self, MainWindow):
        QAbstractItemModel.__init__(self)
        self.rootItem = None
        self.MainWindow = MainWindow
        self.updateData()

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

    def updateData(self):
        # 添加规程， 用例等节点
        if self.rootItem:
            self.rootItem = None
        self.rootItem = TreeItem()
        self.rootItem.data = 'Root'
        # self.projectRoot = TreeItem()
        # self.projectRoot.data = self.MainWindow.projectName
        # self.rootItem.appendChild(self.projectRoot)
        primary = TreeItem()
        primary.data = '强制变量组'
        primary.parent = self.rootItem
        self.rootItem.appendChild(primary)
        self.addChild('强制变量组', primary)
        self.layoutChanged.emit()

    def addChild(self, tabelName, parent):
        # 添加子节点
        allList = PointGroup.get_all()
        if allList:
            for childData in allList:
                child = TreeItem()
                child.data = childData.group_name
                child.parent = parent
                parent.appendChild(child)


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
        # if not index.isValid():
        #     parent.index = QModelIndex()
        if parent == self.rootItem:
            return QModelIndex()
        return self.createIndex(index.row(), 0, parent)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 1

    def rowCount(self, parent=QModelIndex()) -> int:
        return 999