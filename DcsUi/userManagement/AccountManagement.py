from PyQt5.QtCore import QSize
from PyQt5.QtGui import QCursor
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QListWidget, QStackedWidget
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import (QWidget, QTableView, QHeaderView, QAbstractItemView, QMenu)

from DcsUi.userManagement.minwindow import *
from xps.ExploreTable import *


class userList(QWidget):

    def __init__(self):
        super().__init__()

        self.resize(750, 600)
        self.setFixedSize(self.width(), self.height())

        self.dic = {
            'header': ['序号', '用户名', '姓名', '所属组'],
            'data': []
        }

        self.queryModel = None
        # 数据表
        self.tableView = None

        self.createWindow()

    # 创建窗口
    def createWindow(self):
        # 操作布局
        h1 = QHBoxLayout()
        self.label = QLabel("用户列表")
        h1.addWidget(self.label)
        h1.addWidget(QSplitter())
        self.btn = QPushButton('新建用户')
        self.btn.clicked.connect(self.newBuild)
        h1.addWidget(self.btn)

        # 设置表格属性
        self.tableView = QTableView()
        # 表格宽度的自适应调整
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # self.dic['data'] = self.getTableValue()
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
        self.actionC = self.tableView.contextMenu.addAction('修改密码')
        self.tableView.contextMenu.popup(QCursor.pos())  # 3菜单显示的位置
        self.actionC.triggered.connect(self.actionHandler3)
        self.tableView.contextMenu.show()

    def getTableValue(self):
        pass

    def newBuild(self):
        pass

    def active_exit(self):
        pass

    def actionHandler1(self):
        pass

    def actionHandler2(self):
        pass

    def actionHandler3(self):
        pass


class userGroupList(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(750, 600)
        self.setFixedSize(self.width(), self.height())

        # 查询模型
        self.queryModel = None

        # 数据表
        self.tableView = None

        self.dic = {
            'header': ['序号', '组名', '成员', '组描述', '组权限'],
            'data': []
        }
        self.createWindow()

    # 创建窗口
    def createWindow(self):
        # 操作布局
        h1 = QHBoxLayout()
        self.label = QLabel("用户组列表")
        h1.addWidget(self.label)
        h1.addWidget(QSplitter())
        self.btn = QPushButton('新建组')
        self.btn.clicked.connect(self.newBuild)
        h1.addWidget(self.btn)

        # 设置表格属性
        self.tableView = QTableView()
        # 表格宽度的自适应调整
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # self.dic['data'] = self.getTableValue()
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

    def showContextMenu(self):
        self.tableView.contextMenu = QMenu(self)
        self.actionA = self.tableView.contextMenu.addAction('设置')
        self.tableView.contextMenu.popup(QCursor.pos())  # 1菜单显示的位置
        self.actionA.triggered.connect(self.actionHandler1)
        self.actionB = self.tableView.contextMenu.addAction('删除')
        self.tableView.contextMenu.popup(QCursor.pos())  # 2菜单显示的位置
        self.actionB.triggered.connect(self.actionHandler2)
        self.tableView.contextMenu.show()

    def getTableValue(self):
        pass

    def newBuild(self):
        pass

    def active_exit(self):
        pass

    def actionHandler1(self):
        pass

    def actionHandler2(self):
        pass


class AccountManagement(QWidget):
    '''左侧选项栏'''

    def __init__(self):
        super(AccountManagement, self).__init__()
        self.resize(900, 600)
        self.setObjectName('账户管理')
        self.lis_name = None
        self.lis_win = None
        self.lis_img = None

        self._setdata_()

        self.setFixedSize(self.width(), self.height())

        self.setWindowTitle('账户管理')

        self.main_layout = QHBoxLayout(self, spacing=0)  # 窗口的整体布局
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.left_widget = QListWidget()  # 左侧选项列表
        self.main_layout.addWidget(self.left_widget)

        self.right_widget = QStackedWidget()
        self.main_layout.addWidget(self.right_widget)
        self.right_widget.currentChanged.connect(self.changeData)

        self._setup_ui()

    def _setup_ui(self):
        '''加载界面ui'''

        self.left_widget.currentRowChanged.connect(self.right_widget.setCurrentIndex)  # list和右侧窗口的index对应绑定

        self.left_widget.setFrameShape(QListWidget.NoFrame)  # 去掉边框

        self.left_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 隐藏滚动条
        self.left_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        for i in range(len(self.lis_name)):
            self.item = QListWidgetItem(
                QIcon(self.lis_img[i]),
                self.lis_name[i],
                self.left_widget
            )  # 左侧选项的添加
            self.item.setSizeHint(QSize(30, 60))
            self.item.setTextAlignment(Qt.AlignCenter)  # 居中显示
            self.right_widget.addWidget(self.lis_win[i])

    def _setdata_(self):
        pass

    def changeData(self):
        pass
