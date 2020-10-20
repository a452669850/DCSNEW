import sys

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QSplitter, QApplication

from RealtimeDB import iomapping
from historyinfluxDB.historyDB import save


class saveWindow(QDialog):
    my_sin = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('存盘')
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

        self.init()

    def init(self):
        self.library_name = QLabel('库名')
        self.line = QLineEdit()
        self.btn_connect = QPushButton('确定')
        self.btn_connect.clicked.connect(self.commit)
        self.btn_cancel = QPushButton('取消')
        self.btn_cancel.clicked.connect(self.close)

        layout = QVBoxLayout(self)
        h1 = QHBoxLayout(self)
        h2 = QHBoxLayout(self)
        h1.addWidget(self.library_name)
        h1.addWidget(self.line)
        h1.addWidget(QSplitter())
        h2.addWidget(self.btn_connect)
        h2.addWidget(QSplitter())
        h2.addWidget(self.btn_cancel)
        layout.addLayout(h1)
        layout.addLayout(h2)
        self.setLayout(layout)

    def commit(self):
        text = self.line.text()
        save(text)
        iomapping.name = text
        self.my_sin.emit('')
        self.close()

