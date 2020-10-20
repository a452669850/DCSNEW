# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout,QListView,QMessageBox, QAbstractItemView
from PyQt5.QtCore import QStringListModel
from DcsUi.login import LoginUI
from DcsUi.newbuild import Ui_NewBuild
from tools.JsonConfig import getProjectList
import os


class SelectProjectUI(QtWidgets.QDialog):
    def __init__(self):
        super(SelectProjectUI, self).__init__()
        self.setupUi() 

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(290, 269)
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

        self.objectLabel = QtWidgets.QLabel(self)
        self.objectLabel.setObjectName("objectLabel")
        self.verticalLayout.addWidget(self.objectLabel)

        self.tableView = QtWidgets.QListView(self)
        self.tableView.setObjectName("tableView")
        self.model = QStringListModel()
        self.projectList = getProjectList()
        #设置模型列表视图，加载数据列表
        self.model.setStringList(self.projectList)
        #设置列表视图的模型
        self.tableView.setModel(self.model)
        self.tableView.doubleClicked.connect(self.listClicked)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalLayout.addWidget(self.tableView)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetMaximumSize)
        self.horizontalLayout.setContentsMargins(5, 0, 5, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.createObjectButton = QtWidgets.QPushButton(self)
        self.createObjectButton.setObjectName("createObjectButton")
        self.createObjectButton.clicked.connect(self.createProject)
        self.horizontalLayout.addWidget(self.createObjectButton)

        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.horizontalLayout.addItem(spacerItem)

        self.openObjectButton = QtWidgets.QPushButton(self)
        self.openObjectButton.setObjectName("openObjectButton")
        self.openObjectButton.clicked.connect(self.openProject)
        self.horizontalLayout.addWidget(self.openObjectButton)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)


    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "加载工程"))
        self.objectLabel.setText(_translate("Dialog", "            最近打开的工程"))
        self.createObjectButton.setText(_translate("Dialog", "新建工程"))
        self.openObjectButton.setText(_translate("Dialog", "打开工程"))

    def openProject(self):
        self.LoginUI = LoginUI()
        self.projectPath = QtWidgets.QFileDialog.getExistingDirectory(self,'选择文件夹','./')
        if judgeProjectPath(self.projectPath):
            self.LoginUI.projectPath = self.projectPath
            # self.LoginUI.projectName = self.projectName
            self.LoginUI.show()
            self.close()
        else:
            reply = QtWidgets.QMessageBox.question(self, '提示', '请选择正确的路径！', QtWidgets.QMessageBox.Yes)

    def createProject(self):
        self.newBuildUi = Ui_NewBuild()
        self.newBuildUi.show()
        self.close()

    def listClicked(self,qModelIndex):
        self.projectPath = self.projectList[qModelIndex.row()]
        self.LoginUI = LoginUI()
        if judgeProjectPath(self.projectPath):
            self.LoginUI.projectPath = self.projectPath
            # self.LoginUI.projectName = self.projectName
            self.LoginUI.show()
            self.close()
        else:
            reply = QtWidgets.QMessageBox.question(self, '提示', '路径已失效！', QtWidgets.QMessageBox.Yes)

def judgeProjectPath(path):
        if path:
            if os.path.exists(path):
                if {'.resources','.userdata','规程文档'} < set(os.listdir(path)):
                    return True
                else:
                    False
        else:
            return False