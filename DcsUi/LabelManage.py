# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'LabelManage.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!
from PyQt5 import QtCore, QtGui, QtWidgets

from utils.ClientModels import Procedure, Usecase, UsecaseGroup
import sys


class DragView(QtWidgets.QListWidget):
    def __init__(self, parent=None):
        super(DragView, self).__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)

    def getContent(self):
        pass

class LabelManageUi(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(LabelManageUi, self).__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Form")
        self.resize(754, 479)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 1, 0, 4, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 0, 1, 5)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 5, 0, 1, 5)
        self.labelTab = QtWidgets.QTabWidget(self)
        self.labelTab.setObjectName("labelTab")
        # self.tab = QtWidgets.QWidget()
        # self.tab.setObjectName("tab")
        # self.labelTab.addTab(self.tab, "")
        # self.tab_2 = QtWidgets.QWidget()
        # self.tab_2.setObjectName("tab_2")
        # self.labelTab.addTab(self.tab_2, "")
        self.gridLayout.addWidget(self.labelTab, 4, 1, 1, 3)
        self.UsercaseView = QtWidgets.QListView(self)
        self.UsercaseView.setObjectName("UsercaseView")
        self.gridLayout.addWidget(self.UsercaseView, 3, 2, 1, 1)
        self.procedureView = QtWidgets.QListView(self)
        self.procedureView.setObjectName("procedureView")
        self.gridLayout.addWidget(self.procedureView, 3, 1, 1, 1)
        self.usecasegroupVIew = QtWidgets.QListView(self)
        self.usecasegroupVIew.setObjectName("usecasegroupVIew")
        self.gridLayout.addWidget(self.usecasegroupVIew, 3, 3, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 1, 1, 1, 2)
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 3, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 1, 4, 4, 1)
        self.procedurelabel = QtWidgets.QLabel(self)
        self.procedurelabel.setAlignment(QtCore.Qt.AlignCenter)
        self.procedurelabel.setObjectName("procedurelabel")
        self.gridLayout.addWidget(self.procedurelabel, 2, 1, 1, 1)
        self.usecaseLabel = QtWidgets.QLabel(self)
        self.usecaseLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.usecaseLabel.setObjectName("usecaseLabel")
        self.gridLayout.addWidget(self.usecaseLabel, 2, 2, 1, 1)
        self.usercasegroupLabel = QtWidgets.QLabel(self)
        self.usercasegroupLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.usercasegroupLabel.setObjectName("usercasegroupLabel")
        self.gridLayout.addWidget(self.usercasegroupLabel, 2, 3, 1, 1)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "分类管理"))
        self.pushButton.setText(_translate("Form", "添加"))
        self.procedurelabel.setText(_translate("Form", "规程"))
        self.usecaseLabel.setText(_translate("Form", "用例"))
        self.usercasegroupLabel.setText(_translate("Form", "用例组"))


 
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    form = LabelManageUi()
    form.show()
    app.exec_()