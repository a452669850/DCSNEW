from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSplitter, QVBoxLayout


class sysParameterWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.btn_user = QPushButton('用户权限')
        layout = QVBoxLayout()
        h = QHBoxLayout()
        h.addWidget(self.btn_user)
        h.addWidget(QSplitter())
        layout.addLayout(h)
        layout.addWidget(QSplitter())
        layout.addWidget(QSplitter())
        self.setLayout(layout)
