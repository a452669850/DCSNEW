import sys
from pathlib import Path

sys.path.append('D:\\dcstms')

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiArea, QHBoxLayout

from communication import skio, iomapping
from communication.view.IntermediateVariable import intermediateVarWindow
from communication.view.databaseManagement import databaseManageWindow
from communication.view.deviceVariables import deviceVarWindow
from communication.view.myTree import TreeDockWidget
from communication.view.systemParameter import sysParameterWindow

path = Path(__file__).absolute().parent.parent.joinpath('static')


class comWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Dcs自动化测试软件-[工程管理器]')
        skio.setup(path.joinpath('demo'))
        iomapping.setup_Current()
        self.createMenue()
        self.initUI()

    def initUI(self):
        layout = QHBoxLayout()
        self.items = TreeDockWidget(self)
        self.items.tree_Signal.connect(self.windowAction)
        self.items.setFloating(False)
        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.items)
        self.setLayout(layout)

    def createMenue(self):
        self.menubar = self.menuBar()
        self.viewMenu1 = self.menubar.addMenu('&工程')
        self.viewMenu2 = self.menubar.addMenu('&查看')
        self.viewMenu3 = self.menubar.addMenu('&工具')
        self.viewMenu4 = self.menubar.addMenu('&操作')
        self.viewMenu5 = self.menubar.addMenu('&帮助')

        self.viewMenu1.addAction('新建工程')
        self.viewMenu1.addAction('打开')
        self.viewMenu1.addAction('保存')
        self.viewMenu1.addAction('退出')

        self.viewMenu2.addAction('工具栏')
        self.viewMenu2.addAction('状态栏')
        self.viewMenu2.addAction('工作区')
        self.viewMenu2.addAction('显示区')
        self.viewMenu2.addAction('编辑')

        self.viewMenu3.addAction('模拟')
        self.viewMenu3.addAction('运行')
        self.viewMenu3.addAction('下载工程')
        self.viewMenu3.addAction('上传工程')
        self.viewMenu3.addAction('标准modbus点表')
        self.viewMenu3.addAction('模板导入')

        self.viewMenu4.addAction('增加')
        self.viewMenu4.addAction('追加')
        self.viewMenu4.addAction('行拷')
        self.viewMenu4.addAction('列拷')
        self.viewMenu4.addAction('修改')
        self.viewMenu4.addAction('删除')
        self.viewMenu4.addAction('导出')
        self.viewMenu4.addAction('导入')

        self.viewMenu5.addAction('帮助')
        self.viewMenu5.addAction('关于')

        self.viewMenu1.triggered.connect(self.menueAction1)
        self.viewMenu2.triggered.connect(self.menueAction2)
        self.viewMenu3.triggered.connect(self.menueAction3)
        self.viewMenu4.triggered.connect(self.menueAction4)
        self.viewMenu5.triggered.connect(self.menueAction5)

    def windowAction(self, text):
        if len(self.mdi.subWindowList()) < 1:
            if text == 'sysParameter':
                sub = sysParameterWindow()
                self.mdi.addSubWindow(sub)
                sub.showMaximized()
            if text == 'comEqu':
                sub = deviceVarWindow()
                self.mdi.addSubWindow(sub)
                sub.showMaximized()
            if text == 'deviceVar':
                sub = intermediateVarWindow()
                sub.threadings.start()
                self.mdi.addSubWindow(sub)
                sub.showMaximized()
            if text == 'intermediateVar':
                sub = intermediateVarWindow()
                sub.threadings.start()
                self.mdi.addSubWindow(sub)
                sub.showMaximized()
            if text == 'databaseManage':
                sub = databaseManageWindow()
                self.mdi.addSubWindow(sub)
                sub.showMaximized()
        if len(self.mdi.subWindowList()) == 1:
            self.mdi.subWindowList()[0].close()
            if text == 'sysParameter':
                sub = sysParameterWindow()
                self.mdi.addSubWindow(sub)
                sub.showMaximized()
            if text == 'comEqu':
                sub = deviceVarWindow()
                self.mdi.addSubWindow(sub)
                sub.showMaximized()
            if text == 'deviceVar':
                sub = intermediateVarWindow()
                sub.threadings.start()
                self.mdi.addSubWindow(sub)
                sub.showMaximized()
            if text == 'intermediateVar':
                sub = intermediateVarWindow()
                sub.threadings.start()
                self.mdi.addSubWindow(sub)
                sub.showMaximized()
            if text == 'databaseManage':
                sub = databaseManageWindow()
                self.mdi.addSubWindow(sub)
                sub.showMaximized()

        # winDict = {
        #     'sysParameter': sysParameterWindow(),
        #     'comEqu': deviceVarWindow(),
        #     'deviceVar': intermediateVarWindow(),
        #     'intermediateVar': intermediateVarWindow(),
        #     'databaseManage': databaseManageWindow()
        # }
        # if len(self.mdi.subWindowList()) < 1:
        #     sub = winDict[text]
        #     if hasattr(sub, 'threadings'):
        #         print(1)
        #     self.mdi.addSubWindow(sub)
        #     sub.showMaximized()
        # if len(self.mdi.subWindowList()) == 1:
        #     self.mdi.subWindowList()[0].close()
        #     sub = winDict[text]
        #     self.mdi.addSubWindow(sub)
        #     sub.showMaximized()

    def menueAction1(self):
        print(1)

    def menueAction2(self):
        print(2)

    def menueAction3(self):
        print(3)

    def menueAction4(self):
        print(4)

    def menueAction5(self):
        print(5)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = comWindow()
    ex.show()
    sys.exit(app.exec_())
