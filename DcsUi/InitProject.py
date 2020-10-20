# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'initproject.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import sys
sys.path.append('../')
from static.Png import *
from DcsUi.CDrawer import CDrawer
from tools.JsonConfig import getProjectList, getProjectName
from utils.InitDb import judgeProjectPath
from utils.AcountModels import User
from mainwindow import MainWindow
from tools.JsonConfig import writeJson, rewriteJson, getProjectPath, getLastUser
from utils.ClientModels import database_proxy
from utils.InitDb import connectDb,judgeProjectPath, initDatabase, createConfig
from peewee import *
import os
import sys
import json


class DrawerWidget(QtWidgets.QWidget):
    '''初始窗口中的右侧弹窗，根据不同的类型显示不同样式的窗口（登陆时的弹窗和新建工程时的弹窗）'''
    def __init__(self, winType = None, projectPath = None, parent = None, *args, **kwargs):
        super(DrawerWidget, self).__init__(*args, **kwargs)
        # parent为上个打开的父窗口
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet('DrawerWidget{background:white;}')
        self.projectPath = projectPath # 工程路径
        self.winType = winType # 右侧弹窗类型：Create为创建工程时弹出的窗口 login为登陆时弹出的窗口
        self.parent = parent
        if self.winType == 'Create':
            self.gridLayout = QtWidgets.QGridLayout(self)
            self.gridLayout.setContentsMargins(0, 0, 0, 0)
            self.gridLayout.setObjectName("gridLayout")
            self.lineEdit_2 = QtWidgets.QLineEdit(self)
            self.lineEdit_2.setObjectName("lineEdit_2")
            self.gridLayout.addWidget(self.lineEdit_2, 2, 1, 1, 1)
            spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            self.gridLayout.addItem(spacerItem, 0, 1, 1, 1)
            spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            self.gridLayout.addItem(spacerItem1, 4, 1, 1, 1)
            self.pushButton_2 = QtWidgets.QPushButton(self)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Maximum, QtWidgets.QSizePolicy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
            self.pushButton_2.setSizePolicy(sizePolicy)
            self.pushButton_2.setStyleSheet("background-color:transparent")
            self.pushButton_2.setText("")
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/static/createProject.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.pushButton_2.setIcon(icon)
            self.pushButton_2.setObjectName("pushButton_2")
            self.gridLayout.addWidget(self.pushButton_2, 1, 2, 1, 1)
            self.label_2 = QtWidgets.QLabel(self)
            self.label_2.setObjectName("label_2")
            self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
            self.lineEdit = QtWidgets.QLineEdit(self)
            self.lineEdit.setObjectName("lineEdit")
            self.gridLayout.addWidget(self.lineEdit, 1, 1, 1, 1)
            self.label = QtWidgets.QLabel(self)
            self.label.setObjectName("label")
            self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
            self.gridLayout.setColumnStretch(0, 1)
            self.gridLayout.setColumnStretch(1, 2)
            self.pushButton = QtWidgets.QPushButton()
            self.pushButton.setGeometry(QtCore.QRect(50, 100, 93, 28))
            self.pushButton.setObjectName("pushButton")
            self.pushButton.setStyleSheet("background-color:transparent")
            con = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/static/1209037.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.pushButton.setIcon(icon)
            self.gridLayout.addWidget(self.pushButton, 2, 2, 1, 1)
            self.pushButton_2.clicked.connect(self.chooseDir)
            self.pushButton.clicked.connect(self.createProject)
        else:
            self.gridLayout = QtWidgets.QGridLayout(self)
            self.gridLayout.setContentsMargins(1, 0, 0, 0)
            self.gridLayout.setObjectName("gridLayout")
            self.pwdIcon = QtWidgets.QLabel(self)
            self.pwdIcon.setMaximumSize(QtCore.QSize(31, 31))
            self.pwdIcon.setText("")
            self.pwdIcon.setPixmap(QtGui.QPixmap(":/static/password.png"))
            self.pwdIcon.setScaledContents(True)
            self.pwdIcon.setObjectName("pwdIcon")
            self.gridLayout.addWidget(self.pwdIcon, 3, 1, 1, 1)
            self.userEdit = QtWidgets.QLineEdit()
            self.userEdit.setMinimumSize(QtCore.QSize(181, 31))
            self.userEdit.setObjectName("userEdit")
            self.gridLayout.addWidget(self.userEdit, 2, 2, 1, 1)
            self.userIcon = QtWidgets.QLabel()
            self.userIcon.setMaximumSize(QtCore.QSize(31, 31))
            self.userIcon.setText("2")
            self.userIcon.setPixmap(QtGui.QPixmap(":/static/user.png"))
            self.userIcon.setScaledContents(True)
            self.userIcon.setObjectName("userIcon")
            self.gridLayout.addWidget(self.userIcon, 2, 1, 1, 1)
            spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            self.gridLayout.addItem(spacerItem, 0, 2, 1, 1)
            spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            self.gridLayout.addItem(spacerItem1, 1, 2, 1, 1)
            self.loginButton = QtWidgets.QPushButton()
            self.loginButton.setMinimumSize(QtCore.QSize(0, 31))
            icon = QtGui.QIcon()
            icon.addPixmap(QtGui.QPixmap(":/static/login.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
            self.loginButton.setIcon(icon)
            self.loginButton.setObjectName("loginButton")
            self.loginButton.clicked.connect(self.login)
            self.gridLayout.addWidget(self.loginButton, 5, 1, 1, 2)
            spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            self.gridLayout.addItem(spacerItem2, 6, 2, 1, 1)
            self.pwdEdit = QtWidgets.QLineEdit()
            self.pwdEdit.setMinimumSize(QtCore.QSize(181, 31))
            self.pwdEdit.setObjectName("pwdEdit")
            self.pwdEdit.setEchoMode(QtWidgets.QLineEdit.Password)
            self.gridLayout.addWidget(self.pwdEdit, 3, 2, 1, 1)
            spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            self.gridLayout.addItem(spacerItem3, 4, 2, 1, 1)
            spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            self.gridLayout.addItem(spacerItem4, 7, 2, 1, 1)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)
        

    def retranslateUi(self, Form):
        if self.winType == 'Create':
            _translate = QtCore.QCoreApplication.translate
            self.label_2.setText(_translate("Form", "工程名:"))
            self.label.setText(_translate("Form", "选择文件夹:"))
            self.pushButton.setText(_translate("Form", ""))
        else:
            self.loginButton.setText("登录")

    def login(self):
        # 登陆按钮点击事件
        if self.projectPath:
            dbPath = os.path.join(self.projectPath, '.resources', 'dcs.db') # 获取数据库所在路径
            
            # 链接数据库以获取工程中的用户信息
            db = SqliteDatabase(dbPath)
            database_proxy.initialize(db)
            db.connect()
        if not User.get_user_by_username('admin'):
            # 如果没有默认admin用户则创建一个
            User.create_user('admin', 'admin')
        self.user = self.userEdit.text()
        self.password = self.pwdEdit.text()
        if User.password_valid(self.password) and User.username_valid(self.user):
            user = User.get_or_none(User.username == self.user) # 判断账号密码是否无误
            if user:
                if user.verify_password(self.password):
                    rewriteJson(self.user)
                    self.showMainwindow()
                    self.close()
                else:
                    reply = QtWidgets.QMessageBox.question(self, '提示', '账户或密码错误！', QtWidgets.QMessageBox.Yes)
            else:
                reply = QtWidgets.QMessageBox.question(self, '提示', '用户不存在！', QtWidgets.QMessageBox.Yes)
        else:
            reply = QtWidgets.QMessageBox.question(self, '提示', '账户或密码错误！', QtWidgets.QMessageBox.Yes)

    def showMainwindow(self):
        # 打开主窗口
        self.MainWindow = MainWindow()
        self.MainWindow.projectName = getProjectName(self.projectPath)
        self.MainWindow.projectPath = self.projectPath
        self.MainWindow.user = self.user
        self.MainWindow.initUI()
        self.MainWindow.show()
        self.parent.close()
        writeJson(self.projectPath)

    def chooseDir(self):
        # 选择文件夹事件
        self.dirPath = QtWidgets.QFileDialog.getExistingDirectory(self,'选择文件夹','./')
        self.lineEdit.setText(self.dirPath)
        self.show()

    def createProject(self):
        # 创建工程事件
        self.projectPath = self.lineEdit.text()
        self.projectName = self.lineEdit_2.text()
        self.user = 'admin'
        if self.projectPath and self.projectName:
            if not os.listdir(self.projectPath):  
                self.dbPath = os.path.join(self.projectPath, '.resources', 'dcs.db')
                createConfig(self.projectPath, self.projectName) # 创建配置
                initDatabase(self.dbPath) # 初始化数据库
                self.showMainwindow()
                self.parent.close()
            else:
                reply = QtWidgets.QMessageBox.question(self, '提示', '请选择空文件夹！', QtWidgets.QMessageBox.Yes)
        else:
            reply = QtWidgets.QMessageBox.question(self, '提示', '工程名或路径不可为空！', QtWidgets.QMessageBox.Yes)


class Ui_InitProject(QtWidgets.QDialog):
    '''初始窗口界面'''
    def __init__(self):
        super(Ui_InitProject, self).__init__()
        self.setupUi()

    def setupUi(self):
        self.setWindowFlags(QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowCloseButtonHint)
        self.setWindowIcon(QtGui.QIcon(':/static/default.png'))
        self.setObjectName("InitProject")
        self.resize(872, 644)
        self.horizontalLayoutWidget = QtWidgets.QWidget(self)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(-1, -1, 841, 651))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # 设置list结构 
        self.listView = QtWidgets.QListView(self.horizontalLayoutWidget)
        self.listView.setObjectName("listView")
        self.model = QtCore.QStringListModel()
        self.projectList = [getProjectName(x) + '\r\n' + self.getShortPath(x) for x in getProjectList() if getProjectName(x)]
        self.projectPathList = [x for x in getProjectList() if getProjectName(x)]
        #设置模型列表视图，加载数据列表
        self.model.setStringList(self.projectList)
        #设置列表视图的模型
        self.listView.setModel(self.model)
        self.listView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listView.setFont(QtGui.QFont( "Timers", 10,  QtGui.QFont.Bold))
        self.listView.setStyleSheet('QListView::item{height:40px;}')
        self.listView.doubleClicked.connect(self.listClicked)
        # self.listView.setItemAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignVCenter)

        self.horizontalLayout.addWidget(self.listView)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.logoLabel = QtWidgets.QLabel(self.horizontalLayoutWidget)
        self.logoLabel.setText("")
        self.logoLabel.setTextFormat(QtCore.Qt.AutoText)
        self.logoLabel.setPixmap(QtGui.QPixmap(":/static/icon.png"))
        self.logoLabel.setScaledContents(False)
        self.logoLabel.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.logoLabel.setObjectName("logoLabel")
        self.verticalLayout.addWidget(self.logoLabel)
        self.titleLabel = QtWidgets.QLabel(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("华文细黑")
        font.setPointSize(18)
        font.setBold(False)
        font.setWeight(50)
        self.titleLabel.setFont(font)
        self.titleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.titleLabel.setObjectName("titleLabel")
        self.verticalLayout.addWidget(self.titleLabel)
        self.versionLabel = QtWidgets.QLabel(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Mongolian Baiti")
        font.setPointSize(14)
        font.setBold(False)
        font.setWeight(50)
        self.versionLabel.setFont(font)
        self.versionLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.versionLabel.setObjectName("versionLabel")
        self.verticalLayout.addWidget(self.versionLabel)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)

        self.createButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("新宋体")
        font.setPointSize(12)
        self.createButton.setFont(font)
        self.createButton.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.createButton.setStyleSheet("background-color:transparent")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/static/createProject.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.createButton.setIcon(icon)
        self.createButton.setObjectName("createButton")
        self.verticalLayout.addWidget(self.createButton)
        self.createButton.clicked.connect(self.createProject)

        self.OpenButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        # font = QtGui.QFont()
        # font.setFamily("新宋体")
        # font.setPointSize(12)
        self.OpenButton.setFont(font)
        self.OpenButton.setStyleSheet("background-color:transparent")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/static/openProject.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.OpenButton.setIcon(icon1)
        self.OpenButton.setObjectName("OpenButton")
        self.verticalLayout.addWidget(self.OpenButton)
        self.OpenButton.clicked.connect(self.openProject)

        self.reopenButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.reopenButton.sizePolicy().hasHeightForWidth())
        self.reopenButton.setSizePolicy(sizePolicy)
        self.reopenButton.setFont(font)
        self.reopenButton.setContextMenuPolicy(QtCore.Qt.ActionsContextMenu)
        self.reopenButton.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.reopenButton.setAutoFillBackground(False)
        self.reopenButton.setStyleSheet('background-color:transparent')
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/static/reOpen.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.reopenButton.setIcon(icon2)
        self.reopenButton.setAutoDefault(False)
        self.reopenButton.setObjectName("reopenButton")
        self.verticalLayout.addWidget(self.reopenButton)
        self.reopenButton.clicked.connect(self.reOpen)

        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 1)
        self.verticalLayout.setStretch(3, 1)
        self.verticalLayout.setStretch(4, 3)
        self.verticalLayout.setStretch(5, 3)
        self.verticalLayout.setStretch(7, 1)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.horizontalLayout.setStretch(0, 4)
        self.horizontalLayout.setStretch(2, 5)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("InitProject", "Dcs自动化测试管理软件"))
        self.titleLabel.setText(_translate("InitProject", "DCS自动化测试管理软件"))
        self.versionLabel.setText(_translate("InitProject", "Version 2019.09"))
        self.createButton.setText(_translate("InitProject", "新建工程"))
        self.OpenButton.setText(_translate("InitProject", "打开工程"))
        self.reopenButton.setText(_translate("InitProject", "恢复上次打开的工程"))

    def createProject(self):
        # 点击创建工程时弹出右侧窗口
        if not hasattr(self, 'createDrawer'):
            self.createDrawer = CDrawer(self, widget=DrawerWidget(winType = 'Create', parent = self))
            self.createDrawer.setDirection(CDrawer.RIGHT)
            self.createDrawer.setWindowModality(QtCore.Qt.ApplicationModal)
        self.createDrawer.show()

    def getShortPath(self, path):
        # 获取左侧列表中所用路径的缩写
            # if 'Desktop' in path:
            #     return '/'.join(path.split('/')[path.split('/').index('Desktop'):])
            # else:
            #     return path
            if path:
                return '/'.join(['～'] + path.split('/')[-2:])

    def listClicked(self, qModelIndex):
        # 左侧工程列表点击事件 QModelInDex为列表索引对象
        projectPath = self.projectPathList[qModelIndex.row()]
        if judgeProjectPath(projectPath):
            if not hasattr(self, 'loginDrawer'):
                self.loginDrawer = CDrawer(self, widget=DrawerWidget(winType = 'Login', projectPath = projectPath, parent = self))
                self.loginDrawer.setDirection(CDrawer.RIGHT)
                self.loginDrawer.setWindowModality(QtCore.Qt.ApplicationModal)
            self.loginDrawer.projectPath = projectPath
            self.loginDrawer.show()
        else:
            reply = QtWidgets.QMessageBox.question(self, '提示', '路径已失效！', QtWidgets.QMessageBox.Yes)


    def openProject(self):
        # 打开工程事件
        self.projectPath = QtWidgets.QFileDialog.getExistingDirectory(self,'选择文件夹','./')
        if judgeProjectPath(self.projectPath):
            if not hasattr(self, 'loginDrawer'):
                self.loginDrawer = CDrawer(self, widget=DrawerWidget(winType = 'Login', projectPath = self.projectPath, parent = self))
                self.loginDrawer.setDirection(CDrawer.RIGHT)
            else:
                self.loginDrawer.projectPath = self.projectPath
            self.loginDrawer.show()
            self.loginDrawer.setWindowModality(QtCore.Qt.ApplicationModal) # 设置窗口模态化
        else:
            if self.projectPath:
                reply = QtWidgets.QMessageBox.question(self, '提示', '请选择正确的路径！', QtWidgets.QMessageBox.Yes)

    def reOpen(self):
        # 恢复上次打开窗口
        self.projectPath = getProjectPath()
        if judgeProjectPath(self.projectPath):
            self.mainWindow = MainWindow()
            self.mainWindow.projectPath = self.projectPath
            self.mainWindow.user = getLastUser()
            self.mainWindow.initUI()
            self.mainWindow.show()
            self.close()
        else:
            reply = QtWidgets.QMessageBox.question(self, '提示', '上次打开的工程已失效！', QtWidgets.QMessageBox.Yes)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = Ui_InitProject()
    mainWindow.show()
    sys.exit(app.exec_())