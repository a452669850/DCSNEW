from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, \
    QHBoxLayout, QLineEdit, QComboBox, QSplitter, QTableView, QAbstractItemView

from DcsUi.Config.selfChecking import Checking
from xps.ExploreTable import myTableModel, checkModel
from xps.searchEdit import SearchLineEdit


class textEnvironment(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(750, 600)
        self.setFixedSize(self.width(), self.height())
        self.label = QLabel(self)
        self.label.setText('测试环境配置')

        self.list_name = []

        # 表模型
        self.queryModel = None

        # 数据表
        self.tableView = None

        self.dic = {
            'header': ['ID', 'SigName', 'SigType', 'Slot', 'Channel'],
            'data': []
        }

        self.init()

    def init(self):
        self.btn = QPushButton('导入')
        self.btn.clicked.connect(self.leadingIn)

        self.btn1 = QPushButton('导入计时卡')
        self.btn1.clicked.connect(self.timecard)

        self.line = SearchLineEdit(self)
        self.line.searchButton.clicked.connect(self.search)

        self.tableView = QTableView()
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.queryModel = myTableModel(self.dic['header'], self.dic['data'])
        self.tableView.setModel(self.queryModel)
        layout = QVBoxLayout(self)
        h1 = QHBoxLayout(self)
        h1.addWidget(self.label)
        h1.addWidget(QSplitter())
        h1.addWidget(self.btn)
        h1.addWidget(self.btn1)
        h1.addWidget(self.line)
        layout.addLayout(h1)
        layout.addWidget(self.tableView)
        self.setLayout(layout)

    def leadingIn(self):
        pass

    def getdicdata(self):
        pass

    def textset(self, text):
        pass

    def search(self):
        pass

    def timecard(self):
        pass


class networkConfiguration(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(750, 600)
        self.setFixedSize(self.width(), self.height())
        self.label = QLabel(self)
        self.label.setText('网路环境配置')

        self.line = SearchLineEdit(self)
        self.line.searchButton.clicked.connect(self.search)

        # 表模型
        self.queryModel = None

        # 数据表
        self.tableView = None

        self.dic = {
            'header': ['ID', 'Slot', '描述', '地址'],
            'data': []
        }

        self.init()

    def init(self):
        self.tableView = QTableView()
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.queryModel = myTableModel(self.dic['header'], self.dic['data'])
        self.tableView.setModel(self.queryModel)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)

        layout = QVBoxLayout(self)
        h1 = QHBoxLayout(self)
        h2 = QHBoxLayout(self)
        h1.addWidget(self.label)
        h1.addWidget(QSplitter())
        h1.addWidget(self.line)
        h2.addWidget(self.tableView)
        layout.addLayout(h1)
        layout.addLayout(h2)
        self.setLayout(layout)

    def getdicdata(self):
        pass

    def search(self):
        pass


class environmentChecking(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(750, 600)
        self.setFixedSize(self.width(), self.height())

        # 表模型
        self.queryModel = None

        # 数据表
        self.tableView = None

        self.dic = {
            'header': [
                '序号', '模型变量', '变量类型', 'NI板卡/通道'
            ],
            'data': []
        }

        self.lis = []

        self.init()

    def init(self):
        self.btn = QPushButton('开始自检')
        self.btn.clicked.connect(self.startSelfscan)

        self.tableView = QTableView()
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.queryModel = checkModel(self.dic['header'], self.dic['data'])
        self.tableView.setModel(self.queryModel)

        self.threading = Checking()
        self.threading.sinOut.connect(self.slotAdd)

        layout = QVBoxLayout(self)
        h1 = QHBoxLayout(self)
        h2 = QHBoxLayout(self)
        h1.addWidget(self.btn)
        h1.addWidget(QSplitter())
        h2.addWidget(self.tableView)
        layout.addLayout(h1)
        layout.addLayout(h2)
        self.setLayout(layout)

    def startSelfscan(self):
        pass

    def slotAdd(self, lis):
        pass


class timeInterval(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(750, 600)
        self.setFixedSize(self.width(), self.height())

        self.label1 = QLabel(self)
        self.label2 = QLabel(self)
        self.label1.setText('规程运行配置(单位ms):')
        self.label2.setText('规程不通过是否继续运行:')

        self.btn = QPushButton('确认')
        self.btn.clicked.connect(self.confirm)

        self.qle = QLineEdit(self)
        self.qle.setText('500.0')

        self.list = ['是', '否']
        self.box = QComboBox(self, minimumWidth=30, minimumHeight=30)

        self.initCombobox()

        layout = QVBoxLayout(self)
        h1 = QHBoxLayout(self)
        h2 = QHBoxLayout(self)
        h1.addWidget(self.label1)
        h1.addWidget(self.qle)
        h1.addWidget(self.label2)
        h1.addWidget(self.box)
        h1.addWidget(QSplitter())

        h2.addWidget(QSplitter())
        h2.addWidget(self.btn)
        layout.addSpacing(50)
        layout.addLayout(h1)
        layout.addLayout(h2)
        layout.addSpacing(400)
        self.setLayout(layout)

    def initCombobox(self):
        for i in range(len(self.list)):
            self.box.addItem(self.list[i])
        self.box.setCurrentIndex(1)

    def confirm(self):
        pass
