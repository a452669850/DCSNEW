from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QLineEdit, QTableView, QTextEdit, QTabWidget, QVBoxLayout, \
    QHBoxLayout, QSplitter, QFrame

from communication import skio
from communication.view.thread.myThread import myQThreading
from xps.ExploreTable import myTableModel
from xps.searchEdit import SearchLineEdit


class deviceVarWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.dic = None
        self.data = []
        self.getdic()
        self.createfirst()
        self.createtable()
        self.windowlayout()

    def createfirst(self):
        self.label = QLabel('设备管理器')

        self.btn_imp = QPushButton('导入')
        self.btn_imp.clicked.connect(self.btnImport)

        self.line_search = SearchLineEdit()
        self.line_search.searchButton.clicked.connect(self.btnsearch)

        self.line = QFrame(self)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setObjectName("line")

    def createtable(self):
        self.layout = QVBoxLayout()
        self.tabs = QTabWidget()
        self.tab = QWidget()
        self.tab.layout = QVBoxLayout(self)
        self.tableView = QTableView(self)
        self.queryModel = myTableModel(self.dic['header'], self.dic['data'])
        self.tableView.setModel(self.queryModel)
        self.tab.layout.addWidget(self.tableView)
        self.tab.setLayout(self.tab.layout)
        self.tabs.addTab(self.tab, '设备表')

        self.textEdit = QTextEdit(self)

        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.textEdit)

    def windowlayout(self):
        layout = QVBoxLayout(self)

        h = QHBoxLayout(self)
        h.addWidget(self.label)
        h.addWidget(QSplitter())
        h.addWidget(self.btn_imp)
        h.addWidget(self.line_search)

        layout.addLayout(h)
        layout.addWidget(self.line)
        layout.addWidget(QSplitter())
        layout.addLayout(self.layout)
        self.setLayout(layout)

    def getdic(self):
        self.dic = {
            'header': ['ID', 'Slot', '状态', '描述'],
            'data': self.getEquipmentValue()
        }

    def getEquipmentValue(self):
        lis = []
        self.data.clear()
        for x in skio.ping():
            self.data.append(x)
            lis.append([x.id, x.slot, x.status.name, x.description])
        return lis

    def btnImport(self):
        self.textEdit.insertPlainText('*注意*：导入配置文件将暂时中断通信，请不要在测试执行中进行操作\n')
        dirPath = QtWidgets.QFileDialog.getOpenFileName(self,
                                                        "选取文件",
                                                        "./"
                                                        )[0]
        if dirPath != '':
            self.threading = myQThreading(path=dirPath)
            self.threading.sinOut.connect(self.textset)
            self.threading.start()

    def btnsearch(self):
        lis = []
        text = self.line_search.text()
        for i in self.data:
            if text in i.slot:
                lis.append([i.id, i.slot, i.status.name, i.description])
        self.queryModel.datas = lis
        self.queryModel.layoutChanged.emit()

    def textset(self, text):
        self.textEdit.insertPlainText(text)
        if text == '导入设备表完成\n':
            self.queryModel.datas = self.getEquipmentValue()
            self.queryModel.layoutChanged.emit()
