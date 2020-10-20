import re

import pickle
import sys
from pathlib import Path

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QSplitter, QApplication

from scriptExecute.toLead.parse.xlsx import scan
from utils.ClientModels import Script


class importWindow(QWidget):
    my_sin = pyqtSignal(str)

    def __init__(self):
        QWidget.__init__(self)
        self.label = QLabel('请输入序列号')
        self.line1 = QLineEdit(self)
        self.line2 = QLineEdit(self)
        self.btn_select = QPushButton('请选择文件或文件夹')
        self.btn_select.clicked.connect(self.select)
        self.btn_import = QPushButton('导入')
        self.btn_import.clicked.connect(self.script_import)
        h_layout1 = QHBoxLayout()
        h_layout2 = QHBoxLayout()
        v_layout = QVBoxLayout()
        h_layout1.addWidget(self.label)
        h_layout1.addWidget(self.line1)
        h_layout1.addWidget(self.line2)
        h_layout1.addWidget(self.btn_select)
        h_layout2.addWidget(QSplitter())
        h_layout2.addWidget(self.btn_import)
        v_layout.addLayout(h_layout1)
        v_layout.addLayout(h_layout2)
        self.setLayout(v_layout)

    def select(self):
        dirPath = QtWidgets.QFileDialog.getOpenFileName(self,
                                                        "选取文件",
                                                        "./"
                                                        )[0]
        if dirPath != '':
            self.line2.setText(dirPath)

    def script_import(self):
        text1 = self.line1.text()
        text2 = self.line2.text()
        dir = Path(text2)
        data = scan(text1, dir)
        data = pickle.dumps(data, protocol=0)
        name = re.search('([^<>/\\\|:""\*\?]+\.\w+$)', text2).group().split('.')[0]
        lis = [{'name': name, 'serial': text1, 'operation': data, 'path': text2}]
        Script.insert_many(lis).execute()
        self.close()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.my_sin.emit('退出')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = importWindow()
    demo.show()
    sys.exit(app.exec_())
