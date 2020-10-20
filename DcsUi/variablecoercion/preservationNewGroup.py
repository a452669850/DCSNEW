import sys

from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QSplitter, QApplication, \
    QMessageBox

from DcsUi.variablecoercion.model import variableGroupModel
from utils.WorkModels import PointModel


class preservationWindow(QWidget):
    my_Signal = QtCore.pyqtSignal(str)

    def __init__(self, group_name):
        super().__init__()

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

        self.group_name = group_name

        self.setWindowTitle('变量组名')

        self.resize(400, 150)

        self.label = QLabel('请在下面文本框中输入变量组名：')

        self.line = QLineEdit()

        self.ok_btn = QPushButton('OK')
        self.ok_btn.clicked.connect(self.okeyEvent)

        self.cancel_btn = QPushButton('Cancel')
        self.cancel_btn.clicked.connect(self.close)

        layout = QVBoxLayout(self)

        hight = QHBoxLayout(self)
        hight.addWidget(QSplitter())
        hight.addWidget(self.ok_btn)
        hight.addWidget(self.cancel_btn)

        layout.addWidget(self.label)
        layout.addWidget(self.line)
        layout.addLayout(hight)
        self.setLayout(layout)

    def okeyEvent(self):
        pass


class preservation(preservationWindow):
    def __init__(self, group_name):
        preservationWindow.__init__(self, group_name)

    def okeyEvent(self):
        """OK按钮功能函数"""
        text = self.line.text()
        self.my_Signal.emit(text)
        if self.group_name != None:
            points = variableGroupModel.getGroupData(self.group_name)
            if variableGroupModel.createGroup(text, points):
                self.my_Signal.emit('')
                self.close()
            else:
                QMessageBox.information(
                    self,
                    "信息提示",
                    "组名重复",
                    QMessageBox.Yes | QMessageBox.No
                )
        else:
            points = PointModel.all_points()
            if variableGroupModel.createGroup(text, points):
                self.my_Signal.emit('')
                self.close()
            else:
                QMessageBox.information(
                    self,
                    "信息提示",
                    "组名重复",
                    QMessageBox.Yes | QMessageBox.No
                )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = preservationWindow()
    ex.show()
    sys.exit(app.exec_())
