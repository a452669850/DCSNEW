from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QTabWidget, QWidget, QTableView, QHBoxLayout, \
    QSplitter, QFrame, QAbstractItemView, QMenu

from communication.define import ProtocolType
from communication.model import VarModel, DevModel
from communication.view.dialog.newVar import newVarWindow
from communication.view.dialog.updataVar import updataWindow
from communication.view.thread.varThread import mythread
from communication.view.varCoercion import varCoercion
from xps.ExploreTable import variableModel
from xps.searchEdit import SearchLineEdit


class intermediateVarWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.createfirst()
        self.createtable()
        self.windowlayout()

        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.on_timer)

        self.threadings = mythread()

    def createfirst(self):
        self.label = QLabel('PMS 变量管理器')

        self.line_search = SearchLineEdit()
        self.line_search.searchButton.clicked.connect(self.btnsearch)

        self.line = QFrame(self)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setObjectName("line")

    def createtable(self):
        self.tabs = QTabWidget()

        self.tab1 = tabWidget()
        self.tabs.addTab(self.tab1, 'PXI')

        self.tab2 = tableWidget()
        self.tabs.addTab(self.tab2, 'HSL')

    def windowlayout(self):
        layout = QVBoxLayout(self)

        h = QHBoxLayout(self)
        h.addWidget(self.label)
        h.addWidget(QSplitter())
        h.addWidget(self.line_search)

        layout.addLayout(h)
        layout.addWidget(self.line)
        layout.addWidget(QSplitter())
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def btnsearch(self):
        lis = []
        text = self.line_search.text()
        for i in self.tabs.currentWidget().var_list:
            if text in i.sig_name:
                lis.append([i.id, i.sig_name, i.sig_type, i.slot, i.channel, ''])
        self.tabs.currentWidget().queryModel.datas = lis
        self.tabs.currentWidget().queryModel.layoutChanged.emit()

    def on_timer(self):
        page = self.tabs.currentWidget()
        if hasattr(page, 'on_timer'):
            page.on_timer()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.threadings.my_sin.emit('')


class tabWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.dic = None
        self.getdic()

        layout = QVBoxLayout(self)
        self.tableView = QTableView(self)
        self.queryModel = variableModel(self.dic['header'], self.dic['data'])
        self.tableView.setModel(self.queryModel)

        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.showContextMenu)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)

        layout.addWidget(self.tableView)
        self.setLayout(layout)

    def getdic(self):
        self.dic = {
            'header': ['ID', 'SigName', 'SigType', 'Slot', 'Channel', 'Value'],
            'data': self.getdicdata()
        }

    def showContextMenu(self):  # 创建右键菜单
        self.tableView.contextMenu = QMenu(self)
        self.actionA = self.tableView.contextMenu.addAction('变量强制')
        self.tableView.contextMenu.popup(QCursor.pos())  # 1菜单显示的位置
        self.actionA.triggered.connect(self.actionHandler1)
        self.actionB = self.tableView.contextMenu.addAction('添加')
        self.tableView.contextMenu.popup(QCursor.pos())  # 1菜单显示的位置
        self.actionB.triggered.connect(self.actionHandler2)
        self.actionC = self.tableView.contextMenu.addAction('变量修改')
        self.tableView.contextMenu.popup(QCursor.pos())  # 1菜单显示的位置
        self.actionC.triggered.connect(self.actionHandler3)
        self.tableView.contextMenu.show()

    def getdicdata(self):
        lis = []
        dev_list = DevModel.filter(DevModel.protocol == 'modbus')
        self.var_list = VarModel.filter(VarModel.slot.in_([x.slot for x in dev_list])).order_by(VarModel.id)

        for i in self.var_list:
            lis.append([i.id, i.sig_name, i.sig_type, i.slot, i.channel, ''])
        return lis

    def actionHandler1(self):
        row = self.tableView.currentIndex().row()
        var_name = self.queryModel.datas[row][1]
        var = VarModel.get(VarModel.sig_name == var_name)
        self.var_win = varCoercion(var)
        self.var_win.show()

    def actionHandler2(self):
        self.newVar = newVarWindow()
        self.newVar.my_sin.connect(self.addData)
        self.newVar.show()

    def actionHandler3(self):
        row = self.tableView.currentIndex().row()
        self.update_win = updataWindow(self.queryModel.datas[row])
        self.update_win.my_sinOut.connect(self.update_table)
        self.update_win.show()

    def update_table(self):
        self.queryModel.datas = self.getdicdata()
        self.queryModel.layoutChanged.emit()

    def addData(self, lis):
        self.queryModel.append_data(lis)

    def on_timer(self):
        self.queryModel.layoutChanged.emit()


class tableWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.dic = None
        self.list_name = []
        self.getdic()

        layout = QVBoxLayout(self)
        self.tableView = QTableView(self)
        self.queryModel = variableModel(self.dic['header'], self.dic['data'])
        self.tableView.setModel(self.queryModel)

        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.showContextMenu)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)

        layout.addWidget(self.tableView)
        self.setLayout(layout)

    def getdic(self):
        self.dic = {
            'header': ['ID', 'SigName', 'SigType', 'URI', 'Value'],
            'data': self.getdicdata()
        }

    def showContextMenu(self):  # 创建右键菜单
        self.tableView.contextMenu = QMenu(self)
        self.actionA = self.tableView.contextMenu.addAction('变量强制')
        self.tableView.contextMenu.popup(QCursor.pos())  # 1菜单显示的位置
        self.actionA.triggered.connect(self.actionHandler1)
        self.tableView.contextMenu.show()

    def getdicdata(self):
        lis = []
        dev_list = DevModel.filter(DevModel.protocol == ProtocolType.SMHSL.name)
        self.var_list = VarModel.filter(VarModel.slot.in_([x.slot for x in dev_list])).order_by(VarModel.id)

        for i in self.var_list:
            self.list_name.append(i)
            lis.append([i.id, i.sig_name, i.sig_type, i.uri, ''])
        return lis

    def on_timer(self):
        self.queryModel.layoutChanged.emit()
