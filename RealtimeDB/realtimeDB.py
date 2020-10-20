import multiprocessing
import sys
from pathlib import Path

from RealtimeDB.view.dialog.saveWindow import saveWindow

sys.path.append('D:\\dcs')

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiArea, QHBoxLayout

from RealtimeDB import skio
from RealtimeDB.view.utils.mytree import TreeDockWidget
from RealtimeDB.view.window.IOvariable import IOvariableWindow

path = Path(__file__).absolute().parent.parent.joinpath('static')


class realtimewindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('实时数据库')
        skio.setup(path.joinpath('demo'))
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
        self.viewMenu1 = self.menubar.addMenu('&连接')
        self.viewMenu2 = self.menubar.addMenu('&设置')
        self.viewMenu3 = self.menubar.addMenu('&帮助')

        self.viewMenu1.addAction('连接')
        self.viewMenu1.addAction('打印')
        self.viewMenu1.addAction('关闭')

        self.viewMenu2.addAction('强制数据')
        self.viewMenu2.addAction('取消强制')

        self.viewMenu3.addAction('帮助')
        self.viewMenu3.addAction('关于')

        self.viewMenu1.triggered.connect(self.menueAction1)
        self.viewMenu2.triggered.connect(self.menueAction2)
        self.viewMenu3.triggered.connect(self.menueAction3)

    def windowAction(self, text):
        self.text = text
        self.win = saveWindow()
        self.win.show()
        self.win.my_sin.connect(self.windowshow)

    def windowshow(self):
        if len(self.mdi.subWindowList()) < 1:
            if self.text == 'IOvariable':
                sub = IOvariableWindow()
                sub.threadings.start()
                self.mdi.addSubWindow(sub)
                sub.showMaximized()
            if self.text == 'Intermediatevariable':
                sub = IOvariableWindow()
                sub.threadings.start()
                self.mdi.addSubWindow(sub)
                sub.showMaximized()
            if self.text == 'Systemvariables':
                sub = IOvariableWindow()
                sub.threadings.start()
                self.mdi.addSubWindow(sub)
                sub.showMaximized()

    def menueAction1(self):
        print(1)

    def menueAction2(self):
        print(2)

    def menueAction3(self):
        print(3)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = realtimewindow()
    ex.show()
    sys.exit(app.exec_())
