import typing
from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDockWidget, QTreeView
from DcsUi.DockCLass import NewDockWidget
from utils.ClientModels import Procedure, Usecase, UsecaseGroup
from procedure.run_procedure.RunProceduree import ProcedureThread
from static.Png import *
import json

tabelDict = {
        '规程' : Procedure,
        '用例组' : UsecaseGroup,
        '用例' : Usecase,
        } 

class TreeDockWidget(NewDockWidget):
    def __init__(self, title, parent = None):
        NewDockWidget.__init__(self, title, parent=parent)
        self.parent = parent
        self.tree = QTreeView(self)
        # 隐藏标题栏
        self.tree.setHeaderHidden(True)
        self.model = TreeDockModel(self.parent)
        self.tree.setModel(self.model)# 设置树结构model
        
        self.setWidget(self.tree) # 将树结构放置到Dock中
        self.tree.expandAll()
        self.tree.doubleClicked.connect(self.onTreeClicked) # 绑定树结构中节点双击事件

    def onTreeClicked(self, index: QModelIndex):
        # 双击节点事件 判断节点的父节点类型来打开对应表格
        if index.parent().data() not in [self.parent.projectName, None]:
            if index.parent().data() == '规程':
                tabelDb = tabelDict[index.parent().data()]
                for x in tabelDb.get_all().where(tabelDb.name == index.data()):
                    self.parent.procedureRunPath = x.path
                    self.parent.dockTop.addExcel(x.path)
                    self.parent.dockBottom.setMaximumHeight(1000)
            elif index.parent().data() == '用例':
                self.parent.dockTop.addUseCase(index.data())
                self.parent.procedureRunPath = index.data()
            elif index.parent().data() == '用例组': 
                self.parent.dockTop.addUsecaseGroup(index.data())
                self.parent.procedureRunPath = index.data()
        else:
            self.parent.dockTop.addTree()

    def refreshTree(self):
        self.model.updateData()
        self.tree.expandAll()

class TreeItem(object):
    # 重写树item类
    def __init__(self):
        self.children = []
    
    def appendChild(self, child: 'TreeItem') -> None:
        child.parent = self
        self.children.append(child)

class TreeDockModel(QAbstractItemModel):
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
        for x in ['规程', '用例组', '用例']:
            primary = TreeItem()
            primary.data = x
            primary.parent = self.rootItem
            self.rootItem.appendChild(primary)
            self.addChild(x, primary)
        self.layoutChanged.emit()

    def addChild(self, tabelName, parent):
        # 添加子节点
        allList = [x.name for x in tabelDict[tabelName].get_all()]
        if allList:
            for childData in allList:
                child = TreeItem()
                child.data = childData
                child.parent = parent
                parent.appendChild(child)
                # if tabelName == '用例组':
                #     for chilData in json.loads(tabelDict[tabelName].select().where(tabelDict[tabelName].name == child.data)[0].usecase):
                #         usecaseChild = TreeItem()
                #         usecaseChild.data = chilData
                #         usecaseChild.parent = child
                #         child.appendChild(usecaseChild)


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