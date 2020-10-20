from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QSplitter


class exportWindow(QDialog):
    my_Signal = QtCore.pyqtSignal(str)

    def __init__(self, data, ctype):
        super().__init__()
        self.data = data
        self.type = ctype

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

        self.init()

    def init(self):
        self.setWindowTitle('导出测试报告')

        self.label = QLabel('请选择报告路径：')

        self.qle = QLineEdit()

        self.btn = QPushButton('...')
        self.btn.clicked.connect(self.commitPath)

        self.close_btn = QPushButton('关闭')
        self.close_btn.clicked.connect(self.close)

        self.commit_btn = QPushButton('保存')
        self.commit_btn.clicked.connect(self.commitFile)

        layout = QVBoxLayout()
        h1 = QHBoxLayout()
        h2 = QHBoxLayout()
        h1.addWidget(self.label)
        h1.addWidget(self.qle)
        h1.addWidget(self.btn)
        h2.addWidget(self.close_btn)
        h2.addWidget(QSplitter())
        h2.addWidget(self.commit_btn)
        layout.addLayout(h1)
        layout.addLayout(h2)

        self.setLayout(layout)

    def commitFile(self):
        pass

    def commitPath(self):
        pass
