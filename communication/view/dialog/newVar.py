from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QDialog, QGroupBox, QLabel, QComboBox, QLineEdit, QVBoxLayout, QSplitter, \
    QGridLayout, QPushButton, QHBoxLayout

from communication.view.thread.addThread import addVarThread


class newVarWindow(QDialog):
    my_sin = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('追加变量')
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

        self.init()

    def init(self):
        self.groupBox = QGroupBox('批量增加变量')
        self.var_type = QLabel('功能码')
        self.var_number = QLabel('连续个数')
        self.register = QLabel('寄存器间隔')
        self.var_name = QLabel('变量名')
        self.describe = QLabel('描述')
        self.eu = QLabel('单位')
        self.sig_type = QLabel('变量类型')
        self.data_type = QLabel('数值类型')
        self.slot = QLabel('通信接口')
        self.channel = QLabel('通道')

        lis = ['1', '2', '3', '4']
        self.type_combobox = QComboBox(self, minimumWidth=100)
        for i in lis:
            self.type_combobox.addItem(i)

        self.var_number_line = QLineEdit(self)
        self.var_number_line.setText('1')
        self.register_line = QLineEdit(self)
        self.register_line.setText('1')
        self.var_name_line = QLineEdit(self)
        self.var_name_line.setText('var')
        self.describe_line = QLineEdit(self)
        self.describe_line.setText('描述')
        self.eu_line = QLineEdit(self)
        self.eu_line.setText('mA')
        self.sig_type_line = QLineEdit(self)
        self.sig_type_line.setText('sAO')
        self.slot_line = QLineEdit(self)
        self.slot_line.setText('PXI1SLOT1')
        self.channel_line = QLineEdit(self)
        self.channel_line.setText('PXI-6704/CH1')
        self.data_type_line = QLineEdit(self)
        self.data_type_line.setText('D64')
        layout = QGridLayout()

        layout.addWidget(self.var_type, 0, 0)
        layout.addWidget(self.type_combobox, 0, 1)
        layout.addWidget(self.register, 0, 2)
        layout.addWidget(self.register_line, 0, 3)

        layout.addWidget(self.var_number, 1, 0)
        layout.addWidget(self.var_number_line, 1, 1)
        layout.addWidget(self.var_name, 1, 2)
        layout.addWidget(self.var_name_line, 1, 3)
        # layout.addWidget(self.data_type, 1, 2)
        # layout.addWidget(self.data_type_line, 1, 3)
        # layout.addWidget(self.register, 1, 2)
        # layout.addWidget(self.register_line, 1, 3)

        layout.addWidget(self.data_type, 2, 0)
        layout.addWidget(self.data_type_line, 2, 1)
        layout.addWidget(self.sig_type, 2, 2)
        layout.addWidget(self.sig_type_line, 2, 3)

        layout.addWidget(self.describe, 3, 0)
        layout.addWidget(self.describe_line, 3, 1)
        layout.addWidget(self.slot, 3, 2)
        layout.addWidget(self.slot_line, 3, 3)

        layout.addWidget(self.eu, 4, 0)
        layout.addWidget(self.eu_line, 4, 1)
        layout.addWidget(self.channel, 4, 2)
        layout.addWidget(self.channel_line, 4, 3)

        self.groupBox.setLayout(layout)

        self.btn_connect = QPushButton('确定')
        self.btn_connect.clicked.connect(self.commit)
        self.btn_cancel = QPushButton('取消')
        self.btn_cancel.clicked.connect(self.close)

        mainLayout = QVBoxLayout()
        hmainlayout = QHBoxLayout()
        hmainlayout.addWidget(QSplitter())
        hmainlayout.addWidget(self.btn_connect)
        hmainlayout.addWidget(self.btn_cancel)
        mainLayout.addWidget(self.groupBox)
        mainLayout.addLayout(hmainlayout)

        self.setLayout(mainLayout)

    def commit(self):
        name_text = self.var_name_line.text()
        number = self.var_number_line.text()
        describe = self.describe_line.text()
        interval = self.register_line.text()
        unit = self.eu_line.text()
        sig_type = self.sig_type_line.text()
        slot = self.slot_line.text()
        channel = self.channel_line.text()
        combobox_text = self.type_combobox.currentText()
        data_type = self.data_type_line.text()
        self.threading = addVarThread(
            name=name_text, number=number, describe=describe,
            interval=interval, unit=unit, sig_type=sig_type,
            slot=slot, channel=channel, reg=combobox_text,
            chr=data_type
        )
        self.threading.start()
        self.threading.sinOut.connect(self.receive_sin)

    def receive_sin(self, lis):
        self.my_sin.emit(lis)
