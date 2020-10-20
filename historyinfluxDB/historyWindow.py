import sys

sys.path.append('D:\\dcs')

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiArea, QHBoxLayout

from historyinfluxDB.view.util.tree import TreeDockWidget, treelist
from historyinfluxDB.view.util.smallwindow import smallwindow


class historyWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('历史数据库')
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
        self.viewMenu1 = self.menubar.addMenu('F文件')
        self.viewMenu2 = self.menubar.addMenu('O操作')
        self.viewMenu3 = self.menubar.addMenu('H帮助')

        self.viewMenu1.addAction('连接')
        self.viewMenu1.addAction('打印')
        self.viewMenu1.addAction('关闭')

        self.viewMenu2.addAction('导出')

        self.viewMenu3.addAction('帮助')
        self.viewMenu3.addAction('关于')

        self.viewMenu1.triggered.connect(self.menueAction1)
        self.viewMenu2.triggered.connect(self.menueAction2)
        self.viewMenu3.triggered.connect(self.menueAction3)

    def menueAction1(self):
        print(1)

    def menueAction2(self):
        print(2)

    def menueAction3(self):
        print(3)

    def windowAction(self, text):
        """子窗口管理函数"""
        if len(self.mdi.subWindowList()) < 1:
            for i in treelist:
                if text == i['name']:
                    sub = smallwindow(text, self)
                    self.mdi.addSubWindow(sub)
                    sub.showMaximized()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = historyWindow()
    ex.show()
    sys.exit(app.exec_())
