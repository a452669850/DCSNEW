from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QFrame, QHBoxLayout, QVBoxLayout, QSplitter, \
    QMessageBox

from communication import skio


class varCoercion(QWidget):

    def __init__(self, var):
        super().__init__()
        self.var = var

        self.setWindowTitle('变量强制 %s' % self.var.sig_name)

        self.label = QLabel('设置变量 %s' % self.var.sig_name)
        self.label1 = QLabel('类型 %s' % self.var.sig_type)
        self.label2 = QLabel('范围 %s-%s %s' % (self.var.rlo, self.var.rhi, self.var.engineering_unit))

        self.line_edit = QLineEdit(self)

        self.btn_OK = QPushButton('OK')
        self.btn_OK.clicked.connect(self.isokbtn)
        self.btn_Cancel = QPushButton('Cancel')
        self.btn_Cancel.clicked.connect(self.close)

        self.line = QFrame(self)
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)
        self.line.setObjectName("line")

        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hbox3 = QHBoxLayout()
        hbox4 = QHBoxLayout()
        layout = QVBoxLayout()

        hbox1.addWidget(QSplitter())
        hbox1.addWidget(self.btn_OK)
        hbox1.addWidget(self.btn_Cancel)
        hbox2.addWidget(self.label)
        hbox2.addWidget(QSplitter())
        hbox3.addWidget(self.label1)
        hbox3.addWidget(QSplitter())
        hbox4.addWidget(self.label2)
        hbox4.addWidget(QSplitter())

        layout.addLayout(hbox2)
        layout.addLayout(hbox3)
        layout.addLayout(hbox4)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.line)
        layout.addLayout(hbox1)
        self.setLayout(layout)

    def isokbtn(self):
        text = self.line_edit.text()
        try:
            var = float(text)
        except Exception:
            QMessageBox.information(
                self,
                "信息提示",
                "请输入浮点数",
                QMessageBox.Yes | QMessageBox.No
            )
        else:
            skio.write(self.var.sig_name, var)
            self.close()