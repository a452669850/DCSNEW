from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QGridLayout, QHBoxLayout, QSplitter, \
    QVBoxLayout

from communication import iomapping


class updataVarWindow(QDialog):
    my_sinOut = pyqtSignal(str)

    def __init__(self, lis):
        QDialog.__init__(self)
        self.var_list = lis
        self.name_label = QLabel('Sig_name')
        self.val_type_label = QLabel('Sig_type')
        self.slot_label = QLabel('Slot')
        self.channel_label = QLabel('Channel')

        self.name_edit = QLineEdit(self)
        self.name_edit.setText(self.var_list[1])
        self.val_type_edit = QLineEdit(self)
        self.val_type_edit.setText(self.var_list[2])
        self.slot_edit = QLineEdit(self)
        self.slot_edit.setText(self.var_list[3])
        self.channel_edit = QLineEdit(self)
        self.channel_edit.setText(self.var_list[4])

        self.commit_btn = QPushButton('确定')
        self.close_btn = QPushButton('取消')

        self.commit_btn.clicked.connect(self.commit)
        self.close_btn.clicked.connect(self.close)

        glayout = QGridLayout()
        glayout.addWidget(self.name_label, 0, 0)
        glayout.addWidget(self.name_edit, 0, 1)

        glayout.addWidget(self.val_type_label, 1, 0)
        glayout.addWidget(self.val_type_edit, 1, 1)
        glayout.addWidget(self.slot_label, 2, 0)
        glayout.addWidget(self.slot_edit, 2, 1)
        glayout.addWidget(self.channel_label, 3, 0)
        glayout.addWidget(self.channel_edit, 3, 1)

        hlayout = QHBoxLayout()
        hlayout.addWidget(QSplitter())
        hlayout.addWidget(self.commit_btn)
        hlayout.addWidget(self.close_btn)

        layout = QVBoxLayout()
        layout.addLayout(glayout)
        layout.addLayout(hlayout)

        self.setLayout(layout)

    def commit(self):
        pass


class updataWindow(updataVarWindow):

    def __init__(self, var_id):
        updataVarWindow.__init__(self, var_id)

    def commit(self):
        name_text = self.name_edit.text()
        type_text = self.val_type_edit.text()
        slot_text = self.slot_edit.text()
        channel_text = self.channel_edit.text()
        iomapping.updata_varmodel([
            (name_text, self.name_label.text()),
            (type_text, self.val_type_label.text()),
            (slot_text, self.slot_label.text()),
            (channel_text, self.channel_label.text())
        ], self.var_list[0])
        iomapping.setup_Current()
        self.close()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.my_sinOut.emit('')
