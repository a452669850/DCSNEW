# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'login.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from utils.AcountModels import User
from mainwindow import MainWindow
from tools.JsonConfig import writeJson, rewriteJson
from utils.ClientModels import database_proxy
from utils.InitDb import connectDb
from peewee import *
import os
import sys
import json

class LoginUI(QtWidgets.QDialog):
    def __init__(self):
        super(LoginUI, self).__init__()
        self.setupUi(self)
        self.projectName = None
        self.projectPath = None

    def setupUi(self, Login):
        self.setObjectName("Login")
        self.resize(462, 119)
        self.verticalLayout = QtWidgets.QVBoxLayout(Login)
        self.verticalLayout.setContentsMargins(-1, -1, -1, 5)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setHorizontalSpacing(7)
        self.gridLayout.setVerticalSpacing(10)
        self.gridLayout.setObjectName("gridLayout")
        self.passwordLabel = QtWidgets.QLabel(self)
        self.passwordLabel.setObjectName("passwordLabel")
        self.gridLayout.addWidget(self.passwordLabel, 1, 0, 1, 1)

        self.passwordLineEdit = QtWidgets.QLineEdit(self)
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.gridLayout.addWidget(self.passwordLineEdit, 1, 1, 1, 1)

        self.userLabel = QtWidgets.QLabel(self)
        self.userLabel.setObjectName("userLabel")
        self.gridLayout.addWidget(self.userLabel, 0, 0, 1, 1)

        self.userLineEdit = QtWidgets.QLineEdit(self)
        self.userLineEdit.setObjectName("userLineEdit")
        self.gridLayout.addWidget(self.userLineEdit, 0, 1, 1, 1)

        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout.setSpacing(7)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.loginButton = QtWidgets.QPushButton(self)
        self.loginButton.setMaximumSize(QtCore.QSize(10777215, 30))
        self.loginButton.setObjectName("loginButton")
        self.loginButton.clicked.connect(self.login)
        self.horizontalLayout.addWidget(self.loginButton)

        self.guestLoginButton = QtWidgets.QPushButton(self)
        self.guestLoginButton.setMaximumSize(QtCore.QSize(10777215, 30))
        self.guestLoginButton.setObjectName("guestLoginButton")
        self.horizontalLayout.addWidget(self.guestLoginButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Login", "Dialog"))
        self.passwordLabel.setText(_translate("Login", " 密码："))
        self.userLabel.setText(_translate("Login", "用户名："))
        self.loginButton.setText(_translate("Login", "登录"))
        self.guestLoginButton.setText(_translate("Login", "游客"))

    def login(self):
        connectDb(self.projectPath)
        if not User.get_user_by_username('admin'):
            User.create_user('admin', 'admin')
        self.user = self.userLineEdit.text()
        self.password = self.passwordLineEdit.text()
        if User.password_valid(self.password) and User.username_valid(self.user):
            user = User.get_or_none(User.username == self.user)
            if user.verify_password(self.password):
                rewriteJson(self.user)
                self.showMainwindow()
        else:
            reply = QtWidgets.QMessageBox.question(self, '提示', '账户或密码错误！', QtWidgets.QMessageBox.Yes)

    def showMainwindow(self):
        self.MainWindow = MainWindow()
        self.MainWindow.projectName = self.projectName
        self.MainWindow.projectPath = self.projectPath
        self.MainWindow.initUI()
        self.MainWindow.show()
        self.close()
        writeJson(self.projectPath)

