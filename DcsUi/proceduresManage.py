from PyQt5 import QtCore

from DcsUi.AccountManagement import AccountManagement


class proceduresWindow(AccountManagement):
    proced_Signal = QtCore.pyqtSignal(str)

    def __init__(self, lis_name, lis_win, lis_img, str):
        AccountManagement.__init__(self, lis_name, lis_win, lis_img, str)

    def changeData(self):
        win = self.right_widget.currentWidget()
        win.queryModel.datas = win.getTableValue()
        win.queryModel.layoutChanged.emit()
        win.my_Signal.connect(self.treeViewUpdate)

    def treeViewUpdate(self):
        self.proced_Signal.emit('')
