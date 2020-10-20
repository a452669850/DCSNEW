import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QFrame, QVBoxLayout, QHBoxLayout, QSplitter, \
    QApplication


class groupNew(QWidget):
    add_Signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.setWindowTitle('变量组名')
        self.resize(400, 150)

        self.label = QLabel('请在下面文本框中输入变量组名:')

        self.line_edit = QLineEdit(self)

        self.btn_OK = QPushButton('OK')
        self.btn_OK.clicked.connect(self.okeyCommit)
        self.btn_Cancel = QPushButton('Cancel')
        self.btn_Cancel.clicked.connect(self.close)

        self.line = QFrame(self)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setObjectName("line")

        layout = QVBoxLayout(self)

        h = QHBoxLayout(self)
        h.addWidget(QSplitter())
        h.addWidget(self.btn_OK)
        h.addWidget(self.btn_Cancel)

        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.line)
        layout.addLayout(h)
        self.setLayout(layout)

    def okeyCommit(self):
        """OK按钮功能函数"""
        text = self.line_edit.text()
        self.add_Signal.emit(text)
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = groupNew()
    ex.show()
    sys.exit(app.exec_())
