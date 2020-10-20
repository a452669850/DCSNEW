from PyQt5.QtWidgets import QAction, QMainWindow, QMdiArea

from DcsUi.variablecoercion.mandatoryList import mandatoryListWindow
from DcsUi.variablecoercion.saveGroupNew import groupNew
from DcsUi.variablecoercion.smallWindow import *


class Deploy(QMainWindow):
    action = []
    list_name = []
    add_Group_Signal = QtCore.pyqtSignal(str)
    updata_Group_Signal = QtCore.pyqtSignal(str)

    def __init__(self, group_name=None, win_type=True):
        super().__init__()
        self.win_type = win_type
        self.group_name = group_name
        self.sec = 0
        self.setWindowTitle('变量搜索')
        self.resize(1100, 750)
        self.ImgPath = 'static\\images\\toolbar_icon\\'
        # 实例化Qmidarea区域
        self.mdi = QMdiArea()
        # 设置为中间控件
        self.setCentralWidget(self.mdi)
        # 配置menu
        self.menubar = None
        self.initUI()

    def initUI(self):
        self.toolbarBuild()
        if self.win_type:
            self.newBuild()
        else:
            self.allmandatory()

    # 设置工具栏按钮
    def toolbarBuild(self):
        newBuild = QAction(QIcon(self.ImgPath + 'varforce_new_group_search.png'), '新建', self)
        dispose = QAction(QIcon(self.ImgPath + 'varforce_new_group.png'), '保存新组', self)
        addGroup = QAction(QIcon(self.ImgPath + 'varforce_update_group.png'), '添加到组', self)
        interval = QAction(QIcon(self.ImgPath + 'varforce_all_force_group.png'), '所有强制点', self)
        newBuild.triggered.connect(self.newBuild)
        dispose.triggered.connect(self.dispose)
        addGroup.triggered.connect(self.addGroup)
        interval.triggered.connect(self.allmandatory)
        toolbar = self.addToolBar('工具栏')  # 创建一个工具栏实例
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        toolbar.addAction(newBuild)
        toolbar.addAction(dispose)
        toolbar.addAction(addGroup)
        toolbar.addAction(interval)

    def newBuild(self):
        # 实例化多文档界面对象
        if len(self.mdi.subWindowList()) == 0:
            self.menubar = self.menuBar()
            self.viewMenu = self.menubar.addMenu('&Window')
            self.viewMenu.addAction('Cascade')
            self.viewMenu.addAction('Tiled')
            self.viewMenu.addSeparator()
            self.action1 = self.viewMenu.addAction('Next', self.mdi.activateNextSubWindow)
            self.action2 = self.viewMenu.addAction('Previcus', self.mdi.activatePreviousSubWindow)
            if len(self.mdi.subWindowList()) <= 1:
                self.action1.setEnabled(False)
                self.action2.setEnabled(False)
        self.sub = mySearchWindow(self.group_name)
        # 获取count
        self.count = self.sub.getResult()
        # 设置新建子窗口的标题和图标
        self.sub.setWindowTitle('tmp')
        # 将子窗口添加到Mdi区域
        self.mdi.addSubWindow(self.sub)
        self.sub.my_Signal.connect(self.smallWindowClose)
        # 子窗口显示
        self.sub.show()
        if self.count > 0 and self.menubar == None:
            self.menubar = self.menuBar()
            self.viewMenu = self.menubar.addMenu('&Window')
            self.viewMenu.addAction('Cascade')
            self.viewMenu.addAction('Tiled')
            self.viewMenu.addSeparator()
            self.action1 = self.viewMenu.addAction('Next', self.mdi.activateNextSubWindow)
            self.action2 = self.viewMenu.addAction('Previcus', self.mdi.activatePreviousSubWindow)
            if len(self.mdi.subWindowList()) <= 1:
                self.action1.setEnabled(False)
                self.action2.setEnabled(False)
            self.viewMenu.addSeparator()
            self.viewMenu.addAction('%d tmp' % (self.count))
        else:
            if len(self.mdi.subWindowList()) > 1:
                self.action1.setEnabled(True)
                self.action2.setEnabled(True)
            action = self.viewMenu.addAction('%d tmp' % (self.count))
            self.action.append(action)
        self.list_name.append('%d tmp' % (self.count))
        self.viewMenu.triggered[QAction].connect(self.windowAction)

    def dispose(self):
        """保存新组功能函数"""
        self.newGroup = groupNew()
        self.newGroup.show()
        self.newGroup.add_Signal.connect(self.addActive)

    def addGroup(self):
        pass

    def windowAction(self, q):
        """Qmenu的触发函数"""
        if q.text() == 'Cascade':
            self.mdi.cascadeSubWindows()

        if q.text() == 'Tiled':
            self.mdi.tileSubWindows()

        for i in range(len(self.list_name)):
            if q.text() == self.list_name[i]:
                self.mdi.subWindowList()[i].setFocus()

    def allmandatory(self):
        # 实例化多文档界面对象
        if len(self.mdi.subWindowList()) == 0:
            self.menubar = self.menuBar()
            self.viewMenu = self.menubar.addMenu('&Window')
            self.viewMenu.addAction('Cascade')
            self.viewMenu.addAction('Tiled')
            self.viewMenu.addSeparator()
            self.viewMenu.addAction('Arrange Icons')
            self.action1 = self.viewMenu.addAction('Next', self.mdi.activateNextSubWindow)
            self.action2 = self.viewMenu.addAction('Previcus', self.mdi.activatePreviousSubWindow)
            if len(self.mdi.subWindowList()) <= 1:
                self.action1.setEnabled(False)
                self.action2.setEnabled(False)
        self.subwin = mandatoryListWindow(self.group_name)
        # 获取count
        self.count = self.subwin.getResult()
        # 设置新建子窗口的标题
        self.subwin.setWindowTitle('tmp')
        # 将子窗口添加到Mdi区域
        self.mdi.addSubWindow(self.subwin)
        self.subwin.my_Signal.connect(self.mandatoryWindowClose)
        # 子窗口显示
        self.subwin.show()
        if self.count > 0 and self.menubar == None:
            self.menubar = self.menuBar()
            self.viewMenu = self.menubar.addMenu('&Window')
            self.viewMenu.addAction('Cascade')
            self.viewMenu.addAction('Tiled')
            self.viewMenu.addSeparator()
            self.action1 = self.viewMenu.addAction('Next', self.mdi.activateNextSubWindow)
            self.action2 = self.viewMenu.addAction('Previcus', self.mdi.activatePreviousSubWindow)
            if len(self.mdi.subWindowList()) <= 1:
                self.action1.setEnabled(False)
                self.action2.setEnabled(False)
            self.viewMenu.addSeparator()
            self.viewMenu.addAction('%d tmp' % (self.count))
        else:
            if len(self.mdi.subWindowList()) > 1:
                self.action1.setEnabled(True)
                self.action2.setEnabled(True)
            action = self.viewMenu.addAction('%d tmp' % (self.count))
            self.action.append(action)
        self.list_name.append('%d tmp' % (self.count))
        self.viewMenu.triggered[QAction].connect(self.windowAction)

    def smallWindowClose(self):
        """管理子窗口的函数"""
        self.count = self.sub.deleteResult()
        self.viewMenu.removeAction(self.action[-1])
        self.action.pop(-1)
        if len(self.mdi.subWindowList()) - 1 <= 1:
            self.action1.setEnabled(False)
            self.action2.setEnabled(False)
        if len(self.mdi.subWindowList()) - 1 == 0:
            self.menubar.clear()

    def mandatoryWindowClose(self):
        """管理强制子窗口的函数"""
        self.count = self.subwin.deleteResult()
        self.viewMenu.removeAction(self.action[-1])
        self.action.pop(-1)
        if len(self.mdi.subWindowList()) - 1 <= 1:
            self.action1.setEnabled(False)
            self.action2.setEnabled(False)
        if len(self.mdi.subWindowList()) - 1 == 0:
            self.menubar.clear()

    def addActive(self, text):
        pass
