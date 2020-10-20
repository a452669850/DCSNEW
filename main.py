import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget

from xps.menubar import MenuBar
from xps.navbar import TreeDockWidget


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self, parent=None, flags=Qt.Window)
        self.initUI()

    def initUI(self):
        self.setMenuBar(MenuBar(self))
        self.setDockNestingEnabled(True)
        self.addDockWidget(Qt.LeftDockWidgetArea, TreeDockWidget(self))
        self.setCentralWidget(QTabWidget(self))
        self.resize(1200, 800)


if __name__ == '__main__':
    application = QApplication(sys.argv)
    application.setApplicationName('dcsTMS')
    application.setApplicationDisplayName('dcsTMS')
    application.setOrganizationName('shuker')
    application.setOrganizationDomain('shuker.io')
    window = MainWindow()
    window.show()
    sys.exit(application.exec_())
