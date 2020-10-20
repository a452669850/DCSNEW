from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCursor, QIcon
from PyQt5.QtWidgets import QLabel, QComboBox, QLineEdit, QPushButton, QTableView, QAbstractItemView, QVBoxLayout, \
    QWidget, QGridLayout, QMenu, QMessageBox

from DcsUi.variablecoercion.model import variableGroupModel
from utils import core
from xps.ExploreTable import smallTableModel
from xps.mythreads import mythread


class searchWindow(QWidget):
    my_Signal = QtCore.pyqtSignal(str)
    count = 0

    def __init__(self, group_name=None):
        super().__init__()
        self.setWindowIcon(QIcon(':/static/default.png'))

        self.group_name = group_name

        self.comboboxColumnlist = [
            '强制值', '当前值', 'sig_name', 'sig_type', 'chr',
            'slot', 'engineering_unit', 'rlo',
            'rhi', 'elo', 'ehi',
            'channel', 'initial', 'reg', 'block',
            'offset', 'bit'
        ]
        self.comboboxlist2 = ['And', 'Or']

        # 查询模型
        self.queryModel = None

        # 数据表
        self.tableView = None

        self.date = {
            'header': core.MainWindowConfig.header,
            'date': []
        }

        self.initUI()

    def initUI(self):
        label1 = QLabel(self)
        label2 = QLabel(self)
        label3 = QLabel(self)
        label4 = QLabel(self)
        label5 = QLabel(self)
        label1.setText('列：')
        label2.setText('值：')
        label3.setText('关联：')
        label4.setText('列：')
        label5.setText('值：')

        self.comboboxColumn1 = QComboBox(self, minimumWidth=170, minimumHeight=40)
        self.combobox = QComboBox(self, minimumWidth=100, minimumHeight=40)
        self.comboboxColumn2 = QComboBox(self, minimumWidth=170, minimumHeight=40)
        self.combobox.addItems(self.comboboxlist2)

        self.initComomboboxColumn1()
        self.initComomboboxColumn2()

        self.line1 = QLineEdit(self)
        self.line2 = QLineEdit(self)

        self.buttonsearch = QPushButton('查找')
        self.buttonsearch.clicked.connect(self.searchButtonClicked)

        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.dateUpdate)

        self.tableView = QTableView()
        self.tableView.horizontalHeader().setStretchLastSection(True)

        self.queryModel = smallTableModel(self.date['header'], self.date['date'])
        self.tableView.setModel(self.queryModel)
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.showContextMenu)
        self.tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.searchButtonClicked()
        self.queryModel.err.connect(self.errwindow)

        self.thread = mythread()
        self.thread.start()

        layout = QVBoxLayout(self)
        grid = QGridLayout()
        grid.addWidget(label1, 1, 0)
        grid.addWidget(label2, 1, 1)
        grid.addWidget(label3, 1, 2)
        grid.addWidget(label4, 1, 3)
        grid.addWidget(label5, 1, 4)
        grid.addWidget(self.comboboxColumn1, 2, 0)
        grid.addWidget(self.line1, 2, 1)
        grid.addWidget(self.combobox, 2, 2)
        grid.addWidget(self.comboboxColumn2, 2, 3)
        grid.addWidget(self.line2, 2, 4)
        grid.addWidget(self.buttonsearch, 2, 5)
        layout.addLayout(grid)
        layout.addWidget(self.tableView)
        self.setLayout(layout)

    def initComomboboxColumn1(self):
        for i in range(len(self.comboboxColumnlist)):
            self.comboboxColumn1.addItem(self.comboboxColumnlist[i])
        self.comboboxColumn1.setCurrentIndex(-1)

    def initComomboboxColumn2(self):
        for i in range(len(self.comboboxColumnlist)):
            self.comboboxColumn2.addItem(self.comboboxColumnlist[i])
        self.comboboxColumn2.setCurrentIndex(-1)

    def showContextMenu(self):
        self.tableView.contextMenu = QMenu(self)
        self.action = self.tableView.contextMenu.addAction('移除选中行')
        self.tableView.contextMenu.popup(QCursor.pos())  # 1菜单显示的位置
        self.action.triggered.connect(self.actionHandler)
        self.tableView.contextMenu.show()

    def onComboboxActivate(self):
        pass

    def searchButtonClicked(self):
        pass

    def actionHandler(self):
        pass

    def dateUpdate(self):
        pass

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.my_Signal.emit('exit')
        self.close()

    def errwindow(self, text):
        pass

    @classmethod
    def getResult(cls):
        cls.count += 1
        return cls.count

    @classmethod
    def deleteResult(cls):
        cls.count -= 1
        return cls.count


class mySearchWindow(searchWindow):
    def __init__(self, group_name=None):
        searchWindow.__init__(self, group_name)

    def onComboboxActivate(self):
        """搜索窗口下拉框函数"""
        text1 = self.line1.text()
        text2 = self.line2.text()
        conditiontext1 = self.comboboxColumn1.currentText()
        conditiontext2 = self.comboboxColumn2.currentText()
        conditiontext3 = self.combobox.currentText()
        if self.group_name == None:
            group_points = variableGroupModel.searchDate(
                column1=conditiontext1,
                column2=conditiontext2,
                value1=text1,
                value2=text2,
                relation=conditiontext3
            )
        else:
            group_points = variableGroupModel.selectGroupData(
                name=self.group_name,
                column1=conditiontext1,
                column2=conditiontext2,
                value1=text1,
                value2=text2,
                relation=conditiontext3
            )
        self.queryModel.datas = group_points

    def searchButtonClicked(self):
        """查询按钮功能函数"""
        self.onComboboxActivate()
        self.queryModel.layoutChanged.emit()

    def actionHandler(self):
        """移除选中行功能函数"""
        row = self.tableView.currentIndex().row()
        self.queryModel.remove_row(row)

    def dateUpdate(self):
        """时间卡绑定函数"""
        self.queryModel.layoutChanged.emit()

    def errwindow(self, text):
        """变量强制报错时触发函数"""
        QMessageBox.information(
            self,
            "信息提示",
            '强制值设置出错，错误原因:%s' % text,
            QMessageBox.Yes | QMessageBox.No
        )
