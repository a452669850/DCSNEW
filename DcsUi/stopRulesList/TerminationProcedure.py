import sys

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import *

from xps.ExploreTable import myTableModel


class TerminationProcedure(QWidget):
    my_Signal = QtCore.pyqtSignal(str)

    def __init__(self, mainwindow):
        super().__init__()
        self.mainwindow = mainwindow
        self.sec = 0
        self.setWindowTitle('中止规程列表')
        self.resize(1100, 750)
        self.setFixedSize(self.width(), self.height())

        self.list1 = ['全部', '规程', '用例组', '用例']

        # 查询模型
        self.queryModel = None

        # 数据表
        self.tableView = None

        self.dic = {
            'header': ['类型', '编号', '名称', '测试时间', '是否完成'],
            'data': []
        }

        self.runList = []

        self.init()

    def init(self):
        lab1 = QLabel(self)
        lab3 = QLabel(self)
        lab4 = QLabel(self)
        lab1.setText('类型:')
        lab3.setText('编号:')
        lab4.setText('名称:')

        self.all1 = QComboBox(self, minimumWidth=400, minimumHeight=40)
        self.all1.addItems(self.list1)

        self.qle1 = QLineEdit(self)
        self.qle2 = QLineEdit(self)

        self.btn1 = QPushButton('搜索')
        self.btn1.clicked.connect(self.searchButtonClicked)

        self.tableView = QTableView()
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        layout = QVBoxLayout(self)
        h1 = QHBoxLayout(self)
        h2 = QHBoxLayout(self)
        h3 = QHBoxLayout(self)

        for j in (lab1, self.all1, lab3, self.qle1, lab4, self.qle2, self.btn1):
            h1.addWidget(j)
        h2.addWidget(self.tableView)

        layout.addLayout(h1)
        layout.addLayout(h2)
        layout.addLayout(h3)

        self.setLayout(layout)

        self.queryModel = myTableModel(self.dic['header'], self.dic['data'])
        self.searchButtonClicked()
        self.tableView.setModel(self.queryModel)
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.showContextMenu)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)

    def showContextMenu(self):  # 创建右键菜单
        self.tableView.contextMenu = QMenu(self)
        self.actionA = self.tableView.contextMenu.addAction('继续运行')
        self.tableView.contextMenu.popup(QCursor.pos())
        self.actionA.triggered.connect(self.actionHandler1)
        self.actionB = self.tableView.contextMenu.addAction('删除')
        self.tableView.contextMenu.popup(QCursor.pos())
        self.actionB.triggered.connect(self.actionHandler2)
        self.tableView.contextMenu.show()

    def onCombobox1Activate(self):
        pass

    # 点击查询
    def searchButtonClicked(self):
        pass

    def actionHandler1(self):
        pass

    def actionHandler2(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = TerminationProcedure()
    win.show()
    sys.exit(app.exec_())
