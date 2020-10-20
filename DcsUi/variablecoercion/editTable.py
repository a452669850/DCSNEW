import peewee
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QListView, QGroupBox, QGridLayout, QSplitter, \
    QCheckBox, QVBoxLayout, QHBoxLayout, QFrame, QMessageBox

from DcsUi.variablecoercion.model import table_structure, standard_structure, variableGroupModel
from utils import core
from utils.WorkModels import PointModel, PointGroup
from xps.ExploreTable import listViewModel


class configureTable(QWidget):
    my_Signal = QtCore.pyqtSignal(str)

    def __init__(self, group_name):
        super().__init__()

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

        self.checkBox_list = []
        self.header = []
        self.resize(800, 800)
        self.group_name = group_name
        self.deleteRow = None
        self.deleteData = None
        self.addItem = None
        self.addData = None

        self._setinit_()

    def _setinit_(self):
        self.label = QLabel('组:[default]')
        self.label1 = QLabel('搜索-8000点名:')
        self.label2 = QLabel('组内点:')

        self.line = QLineEdit(self)

        self.line1 = QFrame(self)
        self.line1.setFrameShape(QFrame.HLine)
        self.line1.setFrameShadow(QFrame.Sunken)
        self.line1.setObjectName("line")

        self.btn_search = QPushButton('搜索')
        self.btn_search.clicked.connect(self.buttonSearch)

        self.btn_addgroup = QPushButton('加入组>>')
        self.btn_addgroup.clicked.connect(self.buttonAddGroup)

        self.btn_remove = QPushButton('<<移除')
        self.btn_remove.clicked.connect(self.buttonRemove)

        self.btn_confirm = QPushButton('确认')
        self.btn_confirm.clicked.connect(self.buttonConfirm)

        self.btn_cancel = QPushButton('取消')
        self.btn_cancel.clicked.connect(self.close)

        points = PointGroup.get(PointGroup.group_name == self.group_name)
        self.listView1 = QListView()
        self.listModel = listViewModel(points.points)
        self.listView1.setModel(self.listModel)
        self.listView1.clicked.connect(self.clicked1)

        points = PointModel.all_points()
        self.listView2 = QListView()
        self.listAllModel = listViewModel(points)
        self.listView2.setModel(self.listAllModel)
        self.listView2.clicked.connect(self.clicked2)

        self.createGridGroupBox()
        self.createCheckBox()

        layout = QVBoxLayout()
        h1 = QHBoxLayout()
        h2 = QHBoxLayout()
        h3 = QHBoxLayout()
        h4 = QHBoxLayout()
        smallayout = QVBoxLayout()

        h1.addWidget(self.label)
        h1.addWidget(self.label1)

        h2.addWidget(self.label2)
        h2.addWidget(QSplitter())
        h2.addWidget(self.line)
        h2.addWidget(self.btn_search)

        smallayout.addWidget(self.btn_addgroup)
        smallayout.addWidget(self.btn_remove)

        h3.addWidget(self.listView2)
        h3.addLayout(smallayout)
        h3.addWidget(self.listView1)

        h4.addWidget(QSplitter())
        h4.addWidget(self.btn_confirm)
        h4.addWidget(self.btn_cancel)
        h4.addWidget(QSplitter())

        layout.addWidget(self.groupBox)
        layout.addLayout(self.layout)
        layout.addWidget(self.line1)
        layout.addLayout(h1)
        layout.addLayout(h2)
        layout.addLayout(h3)
        layout.addLayout(h4)
        self.setLayout(layout)

    def createGridGroupBox(self):
        self.setWindowTitle('用户组设置')

        self.groupBox = QGroupBox(self)
        self.groupBox.setTitle('全选设置')

        layout = QGridLayout()

        self.btn_allUser = QPushButton('全选')
        self.btn_unAllUser = QPushButton('全不选')

        self.btn_allUser.clicked.connect(self.selectAll)
        self.btn_unAllUser.clicked.connect(self.unSelectAll)

        layout.addWidget(self.btn_allUser, 1, 0)
        layout.addWidget(self.btn_unAllUser, 1, 1)
        layout.addWidget(QSplitter(), 2, 2)

        self.groupBox.setLayout(layout)

    def createCheckBox(self):
        self.layout = QGridLayout()
        positions = [(i, j) for i in range(len(table_structure) // 4 + 1) for j in range(4)]
        for position, name in zip(positions, table_structure):
            checkBox = QCheckBox(name[1])
            self.checkBox_list.append(checkBox)
            checkBox.stateChanged.connect(self.checkDisplay)
            self.layout.addWidget(checkBox, *position)
            if name in core.MainWindowConfig.header:
                checkBox.setChecked(True)

    def buttonSearch(self):
        pass

    def buttonAddGroup(self):
        pass

    def buttonRemove(self):
        pass

    def clicked1(self, index):
        pass

    def clicked2(self, index):
        pass

    def buttonConfirm(self):
        pass

    def checkDisplay(self, state):
        pass

    def selectAll(self):
        pass

    def unSelectAll(self):
        pass


class configure(configureTable):
    def __init__(self, group_name):
        configureTable.__init__(self, group_name)

    def buttonSearch(self):
        """搜索"""
        text = self.line.text()
        lis = variableGroupModel.searchEdi(text)
        self.listAllModel.updataItem(lis)

    def buttonAddGroup(self):
        """添加行"""
        if self.addItem == None:
            QMessageBox.information(
                self,
                "信息提示",
                '所要添加行未选中',
                QMessageBox.Yes | QMessageBox.No
            )
            return
        try:
            self.listModel.addItem(self.addItem)
            variableGroupModel.addGroupData(self.group_name, self.addData)
        except peewee.IntegrityError as e:
            QMessageBox.information(
                self,
                "信息提示",
                '所要添加行已存在',
                QMessageBox.Yes | QMessageBox.No
            )
            self.listModel.deleteItem(-1)

    def buttonRemove(self):
        """删除行"""
        if self.deleteRow == None:
            QMessageBox.information(
                self,
                "信息提示",
                '所要移除行未选中',
                QMessageBox.Yes | QMessageBox.No
            )
            return
        else:
            self.listModel.deleteItem(self.deleteRow)
            variableGroupModel.deleteGroupData(self.group_name, self.deleteData)

    def clicked1(self, index):
        """QListView的列中被点击触发该函数"""
        self.deleteData = self.listModel.ListItemDate[index.row()]['data']
        self.deleteRow = index.row()

    def clicked2(self, index):
        """QListView的列中被点击触发该函数"""
        self.addData = self.listAllModel.ListItemDate[index.row()]['data']
        self.addItem = self.listAllModel.ListItemDate[index.row()]

    def buttonConfirm(self):
        """确认按钮功能函数"""
        core.MainWindowConfig.header = standard_structure + self.header
        self.my_Signal.emit('')
        self.close()

    def checkDisplay(self, state):
        """复选框勾选触发函数"""
        checkBox = self.sender()
        if state == Qt.Checked:
            for i in table_structure:
                if checkBox.text() in i:
                    self.header.append(i)
        else:
            for j in self.header:
                if checkBox.text() in j:
                    self.header.remove(j)

    def selectAll(self):
        """全选"""
        for i in self.checkBox_list:
            i.setChecked(True)

    def unSelectAll(self):
        """全不选"""
        for i in self.checkBox_list:
            i.setChecked(False)
