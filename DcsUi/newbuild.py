# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newbuild.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
from utils.InitDb import initDatabase, createConfig
from utils.InitDb import connectDb, judgeProjectPath
from DcsUi.Login import LoginUI
import os

class Ui_NewBuild(QtWidgets.QDialog):
    def __init__(self, parent = None):
        super(Ui_NewBuild, self).__init__()
        # 主窗口是否已经运行
        self.mainIsWorking = None
        self.parent = parent
        self.setupUi()

        

    def setupUi(self):
        self.setObjectName("新建工程")
        self.resize(540, 221)
        self.toolButton = QtWidgets.QToolButton(self)
        self.toolButton.setGeometry(QtCore.QRect(490, 110, 47, 31))
        self.toolButton.setObjectName("toolButton")
        self.toolButton.clicked.connect(self.chooseDir)

        self.pushButton_2 = QtWidgets.QPushButton(self)
        self.pushButton_2.setGeometry(QtCore.QRect(20, 160, 93, 41))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.close)

        self.pushButton_3 = QtWidgets.QPushButton(self)
        self.pushButton_3.setGeometry(QtCore.QRect(430, 160, 93, 41))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(self.createProject)

        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setGeometry(QtCore.QRect(130, 40, 351, 31))
        self.lineEdit.setText('我的工程')
        self.lineEdit.setObjectName("lineEdit")

        self.lineEdit_2 = QtWidgets.QLineEdit(self)
        self.lineEdit_2.setGeometry(QtCore.QRect(130, 110, 351, 31))
        self.lineEdit_2.setObjectName("lineEdit_2")

        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(1, 39, 101, 31))
        self.label.setObjectName("label")

        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setGeometry(QtCore.QRect(1, 109, 121, 31))
        self.label_2.setObjectName("label_2")

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("NewBuild", "创建工程"))
        self.toolButton.setText(_translate("NewBuild", "..."))
        self.pushButton_2.setText(_translate("NewBuild", "关闭"))
        self.pushButton_3.setText(_translate("NewBuild", "保存"))
        self.label.setText(_translate("NewBuild", "请输入工程名:"))
        self.label_2.setText(_translate("NewBuild", "请选择工程路径:"))

    def chooseDir(self):
        # 选择文件夹函数
        self.dirPath = QtWidgets.QFileDialog.getExistingDirectory(self,'选择文件夹','./')
        self.lineEdit_2.setText(self.dirPath)

    def createProject(self):
        self.projectPath = self.lineEdit_2.text()
        self.projectName = self.lineEdit.text()
        if self.projectPath and self.projectName:
            if not os.listdir(self.projectPath):  
                self.dbPath = os.path.join(self.projectPath, '.resources', 'dcs.db')
                createConfig(self.projectPath, self.projectName)
                initDatabase(self.dbPath)
                if not self.mainIsWorking:
                    self.loginUi = LoginUI()
                    self.loginUi.projectPath = self.projectPath
                    self.loginUi.projectName = self.projectName
                    self.loginUi.show()
                    self.close()
                else:
                    connectDb(self.projectPath)
                    self.parent.projectName = self.projectName
                    self.parent.dockTop.setWidget(QWidget())
                    self.parent.dockLeft.refreshTree()
                    self.parent.dockBottom.logBrowser.clear()
                    self.close()
            else:
                reply = QtWidgets.QMessageBox.question(self, '提示', '请选择空文件夹！', QMessageBox.Yes)
        else:
            reply = QtWidgets.QMessageBox.question(self, '提示', '工程名或路径不可为空！', QMessageBox.Yes)
    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)  # 创建一个QApplication，也就是你要开发的软件app
    MainWindow = QtWidgets.QMainWindow()    # 创建一个QMainWindow，用来装载你需要的各种组件、控件
    ui = Ui_NewBuild()                    # ui是Ui_MainWindow()类的实例化对象
    ui.setupUi(MainWindow)                  # 执行类中的setupUi方法，方法的参数是第二步中创建的QMainWindow
    MainWindow.show()                       # 执行QMainWindow的show()方法，显示这个QMainWindow
    sys.exit(app.exec_())