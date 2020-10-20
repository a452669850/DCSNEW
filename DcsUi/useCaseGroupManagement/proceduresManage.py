import json

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QMenu
from PyQt5.QtWidgets import QTableView, QAbstractItemView, QVBoxLayout
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QSplitter, \
    QPushButton

# from DcsUi.useCaseGroupManagement.PopupWindow import NewRules
from DcsUi.useCaseGroupManagement.SQLOperation import sqlOperation
from DcsUi.useCaseGroupManagement.dialogWin import newBuildWindow
from DcsUi.useCaseGroupManagement.dialogWindow import editUsecaseGroup
from DcsUi.userManagement.AccountManagement import AccountManagement
from procedure.manage_procedure.import_procedure import parse_procedure
from utils.ClientModels import UsecaseGroup
from xps.ExploreTable import myTableModel
from xps.searchEdit import SearchLineEdit


class useCaseDroupList(QWidget):
    my_Signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.sec = 0
        self.setWindowTitle('用例组列表')
        self.resize(750, 600)
        self.setFixedSize(self.width(), self.height())

        self.dic = None

        self.dicValue()

        self.createTable()

    def createTable(self):
        h1 = QHBoxLayout()
        self.label = QLabel("用例组列表")
        h1.addWidget(self.label)
        h1.addWidget(QSplitter())
        self.btn = QPushButton('新建用例组')
        self.btn.clicked.connect(self.newBuild)
        h1.addWidget(self.btn)
        self.line = SearchLineEdit(self)
        self.line.searchButton.clicked.connect(self.search)
        h1.addWidget(self.line)

        # 设置表格属性
        self.tableView = QTableView()
        # 表格宽度的自适应调整
        self.tableView.horizontalHeader().setStretchLastSection(True)

        self.queryModel = myTableModel(self.dic['header'], self.dic['data'])
        self.tableView.setModel(self.queryModel)
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.showContextMenu)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)

        # 创建界面
        mainLayout = QVBoxLayout(self)
        mainLayout.addLayout(h1)
        mainLayout.addWidget(self.tableView)
        self.setLayout(mainLayout)

    def showContextMenu(self):  # 创建右键菜单
        self.tableView.contextMenu = QMenu(self)
        self.actionA = self.tableView.contextMenu.addAction('编辑')
        self.tableView.contextMenu.popup(QCursor.pos())  # 1菜单显示的位置
        self.actionA.triggered.connect(self.actionHandler1)
        self.actionB = self.tableView.contextMenu.addAction('删除')
        self.tableView.contextMenu.popup(QCursor.pos())  # 2菜单显示的位置
        self.actionB.triggered.connect(self.actionHandler2)
        self.tableView.contextMenu.show()

    def dicValue(self):
        pass
        # self.dic = {
        #     'header': ['编号', '名称', '用例组'],
        #     'data': self.getTableValue()
        # }

    def getTableValue(self):
        pass
        # return sqlOperation.selectusecasegroup()

    def newBuild(self):
        pass
        # self.newBuildUsecaseGroup = NewRules()
        # self.newBuildUsecaseGroup.my_Signal.connect(self.active_exit)
        # self.newBuildUsecaseGroup.show()

    def active_exit(self):
        pass
        # self.queryModel.datas = self.getTableValue()
        # self.queryModel.layoutChanged.emit()
        # self.my_Signal.emit('')

    def actionHandler1(self):
        pass
        # row = self.tableView.currentIndex().row()
        # self.editWindow = editUsecaseGroup(self.queryModel.datas[row][1])
        # self.editWindow.my_Signal.connect(self.active_exit)
        # self.editWindow.show()

    def actionHandler2(self):
        pass
        # row = self.tableView.currentIndex().row()
        # usecase = UsecaseGroup.get(UsecaseGroup.name == self.queryModel.datas[row][1])
        # UsecaseGroup.delete_obj(usecase.id)
        # self.queryModel.remove_row(row)
        # self.my_Signal.emit('')

    def search(self):
        pass
        # text = self.line.text()
        # self.queryModel.datas = sqlOperation.searchUsecaseGroup(text)
        # self.queryModel.layoutChanged.emit()


class useCaseDroup(useCaseDroupList):
    def __init__(self):
        useCaseDroupList.__init__(self)

    def dicValue(self):
        """这个函数是用来初始化渲染表模型用的"""
        self.dic = {
            'header': ['编号', '名称', '用例组'],
            'data': self.getTableValue()
        }

    def getTableValue(self):
        """获取所有用例组"""
        return sqlOperation.selectusecasegroup()

    def newBuild(self):
        """新建"""
        self.newBuildUsecaseGroup = newBuildWindow()
        self.newBuildUsecaseGroup.my_Signal.connect(self.active_exit)
        self.newBuildUsecaseGroup.show()

    def active_exit(self):
        """新建窗口退出后运行此函数，用于刷新表格数据"""
        self.queryModel.datas = self.getTableValue()
        self.queryModel.layoutChanged.emit()
        self.my_Signal.emit('')

    def actionHandler1(self):
        """"编辑"""
        row = self.tableView.currentIndex().row()
        self.editWindow = editUsecaseGroup(self.queryModel.datas[row][1])
        self.editWindow.my_Signal.connect(self.active_exit)
        self.editWindow.show()

    def actionHandler2(self):
        """删除"""
        row = self.tableView.currentIndex().row()
        usecase = UsecaseGroup.get(UsecaseGroup.name == self.queryModel.datas[row][1])
        UsecaseGroup.delete_obj(usecase.id)
        self.queryModel.remove_row(row)
        self.my_Signal.emit('')

    def search(self):
        """查询"""
        text = self.line.text()
        self.queryModel.datas = sqlOperation.searchUsecaseGroup(text)
        self.queryModel.layoutChanged.emit()


class proceduresList(useCaseDroupList):
    my_Signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('规程列表')
        self.label.setText('规程列表')
        self.btn.setText('导入规程')

    def showContextMenu(self):  # 创建右键菜单
        self.tableView.contextMenu = QMenu(self)
        self.action = self.tableView.contextMenu.addAction('删除')
        self.tableView.contextMenu.popup(QCursor.pos())  # 2菜单显示的位置
        self.action.triggered.connect(self.actionHandler)
        self.tableView.contextMenu.show()

    def dicValue(self):
        """这个函数是用来初始化渲染表模型用的"""
        self.dic = {
            'header': ['编号', '名称', '用例'],
            'data': self.getTableValue()
        }

    def getTableValue(self):
        """获取所有规程"""
        return sqlOperation.selectProcedures()

    def newBuild(self):
        """导入规程"""
        self.procedurePath, filetype = QtWidgets.QFileDialog.getOpenFileName(
            self, '选择文件', '',
            'Excel files(*.xlsx , *.xls)'
        )
        if self.procedurePath:
            parse_procedure(self.procedurePath)
            self.queryModel.datas = self.getTableValue()
            self.queryModel.layoutChanged.emit()
            self.my_Signal.emit('')

    def actionHandler(self):
        """删除规程"""
        row = self.tableView.currentIndex().row()
        sqlOperation.deleteProcedures(self.queryModel.datas[row][0])
        for i in json.loads(self.queryModel.datas[row][2]):
            sqlOperation.deleteUsecase(i)
        self.queryModel.remove_row(row)
        self.my_Signal.emit('')

    def search(self):
        """查找"""
        text = self.line.text()
        self.queryModel.datas = sqlOperation.searchProcedures(text)
        self.queryModel.layoutChanged.emit()


class proceduresWindow(AccountManagement):
    proced_Signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def _setdata_(self):
        """初始化最外层窗口"""
        win8 = useCaseDroup()
        win9 = proceduresList()
        self.lis_name = ['用例组管理', '规程管理']
        self.lis_win = [win8, win9]
        self.lis_img = [
            ':/static/environment_settings_icon0.png',
            ':/static/NetworkSettings.png',
        ]

    def changeData(self):
        """在选项卡切换的时候触发此函数防止卡死"""
        win = self.right_widget.currentWidget()
        win.queryModel.datas = win.getTableValue()
        win.queryModel.layoutChanged.emit()
        win.my_Signal.connect(self.treeViewUpdate)

    def treeViewUpdate(self):
        """表格刷新"""
        self.proced_Signal.emit('')
