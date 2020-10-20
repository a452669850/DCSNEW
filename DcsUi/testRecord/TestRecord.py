import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import *

from xps.ExploreTable import myTableModel


class Record(QWidget):
    def __init__(self, *args):
        super().__init__()
        self.sec = 0
        self.setWindowTitle('测试记录')
        self.resize(1100, 750)
        self.setFixedSize(self.width(), self.height())
        self.list1 = ['全部', '规程', '用例组', '用例']
        self.list2 = ['全部', '已完成', '未完成']

        # 绑定模型查询出来的对象
        self.data = None

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
        lab2 = QLabel(self)
        lab3 = QLabel(self)
        lab4 = QLabel(self)
        lab1.setText('类型:')
        lab2.setText('是否完成:')
        lab3.setText('编号:')
        lab4.setText('名称:')

        self.all1 = QComboBox(self, minimumWidth=400, minimumHeight=40)
        self.all2 = QComboBox(self, minimumWidth=100, minimumHeight=40)
        self.all1.addItems(self.list1)
        self.all2.addItems(self.list2)

        self.qle1 = QLineEdit(self)
        self.qle2 = QLineEdit(self)

        self.qle1.returnPressed.connect(self.searchButtonClicked)
        self.qle2.returnPressed.connect(self.searchButtonClicked)

        self.btn1 = QPushButton('搜索')
        self.btn1.clicked.connect(self.searchButtonClicked)
        self.btn2 = QPushButton('导出')
        self.btn2.clicked.connect(self.menuGroup)
        self.btn3 = QPushButton('打开报告')
        self.btn3.clicked.connect(self.openReport)

        self.tableView = QTableView()
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        layout = QVBoxLayout(self)
        h1 = QHBoxLayout(self)
        h3 = QHBoxLayout(self)

        for j in (lab1, self.all1, lab2, self.all2, lab3, self.qle1, lab4, self.qle2, self.btn1):
            h1.addWidget(j)
        h3.addWidget(QSplitter())
        h3.addWidget(self.btn2)
        h3.addWidget(self.btn3)
        h3.addWidget(QSplitter())

        layout.addLayout(h1)
        layout.addWidget(self.tableView)
        layout.addLayout(h3)

        self.setLayout(layout)

        self.queryModel = myTableModel(self.dic['header'], self.dic['data'])
        self.tableView.setModel(self.queryModel)
        self.searchButtonClicked()
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.showContextMenu)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)

    def showContextMenu(self):  # 创建右键菜单
        self.tableView.contextMenu = QMenu(self)
        self.actionA = self.tableView.contextMenu.addAction('删除')
        self.tableView.contextMenu.popup(QCursor.pos())  # 2菜单显示的位置
        self.actionA.triggered.connect(self.actionHandler)
        self.tableView.contextMenu.show()

    def menuGroup(self):
        self.men = QMenu(self)
        self.exportzz = self.men.addAction('导出自证报告')
        self.exportcs = self.men.addAction('导出测试报告')
        self.men.popup(QCursor.pos())  # 1菜单显示的位置
        self.exportzz.triggered.connect(self.self_certification)
        self.exportcs.triggered.connect(self.myExport)

    def onCombobox1Activate(self):
        pass

    # 点击查询
    def searchButtonClicked(self):
        pass

    def self_certification(self):
        pass

    def myExport(self):
        pass

    def openReport(self):
        pass

    def actionHandler(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Record()
    win.show()
    sys.exit(app.exec_())
