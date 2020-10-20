from PyQt5.QtWidgets import QMenuBar


class MenuBar(QMenuBar):
    """
    全局菜单栏
    """

    def __init__(self, parent=None):
        QMenuBar.__init__(self, parent)
        self.setNativeMenuBar(False)
        self.addMenu('&File')
        self.addMenu('&Edit')
        self.addMenu('&View')
        self.addMenu('&Navigate')
        self.addMenu('&Code')
        self.addMenu('&Refactor')
        self.addMenu('R&un')
        self.addMenu('&Tools')
        self.addMenu('VC&S')
        self.addMenu('&Window')
        self.addMenu('&Help')
