from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QSize, QFile
from PyQt5.QtGui import QIcon, QColor
from PyQt5 import QtGui
from DcsUi.GetQss import CommonHelper
import os


class NewDockWidget(QDockWidget):
    def __init__(self, title, parent=None):
        QDockWidget.__init__(self, parent = parent)
        parent.toolBar = QToolBar()
        self.DockTitleBar = DockTitleBar # 自定义标题栏
        self.setTitleBarWidget(self.DockTitleBar(parent, title))
        self.setObjectName(title)
        self.setWindowTitle(title)
        # self.setStyleSheet('''border: 1.5px ridge #484848;
        # background:#444444;''')

    def changeTitle(self, title):
        # 更改Dock标题
        self.titleBarWidget().label.setText(title)


class DockTitleBar(QFrame):
    ''' 自定义标题栏类 '''
    def __init__(self, parent, title):
        super(DockTitleBar, self).__init__(parent)
        self.window = parent

        qssStyle = CommonHelper.getQss()
        self.setStyleSheet(qssStyle)
        
        self.setFrameStyle(QFrame.Raised | QFrame.StyledPanel)

        # 标题栏布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0.1,0.1,0.1,0.1)

        # 设置标题栏标题
        self.label = QLabel(title)
        # self.label.setStyleSheet('''
        # border: 0px;
        # border-radius: 0px;
        # padding: 0px;''')
        # 设置标题栏按钮
        iconSize = QApplication.style().standardIcon(
            QStyle.SP_TitleBarNormalButton).actualSize(
                QSize(20, 20))
        buttonSize = iconSize + QSize(5, 5)

        # 最小化dock按钮
        self.minButton = QToolButton(self)
        self.minButton.setAutoRaise(True)
        self.minButton.setMaximumSize(buttonSize)
        self.minButton.setIcon(QApplication.style().standardIcon(
            QStyle.SP_TitleBarMinButton))
        self.minButton.clicked.connect(self.minClicked)

        #最大化dock按钮
        self.maxButton = QToolButton(self)
        self.maxButton.setAutoRaise(True)
        self.maxButton.setMaximumSize(buttonSize)
        self.maxButton.setIcon(QApplication.style().standardIcon(
            QStyle.SP_TitleBarMaxButton))
        self.maxButton.clicked.connect(self.maxClicked)
        self.whetherPress = 0

        # dock还原事件
        self.restoreAction = QAction(title, parent)
        self.restoreAction.triggered.connect(self.ViewDock)

        # 布局设置
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.minButton)
        layout.addWidget(self.maxButton)

    def minClicked(self):
        # 最小化事件
        self.parent().setVisible(False)
        self.window.addToolBar(Qt.BottomToolBarArea,self.window.toolBar) # 工具栏添加还原按钮
        self.window.toolBar.addAction(self.restoreAction) # 工具栏添加还原事件

    def maxClicked(self):
        # 最大化事件
        if self.whetherPress == 0: # 判断是否最大化
            if self.parent() == self.window.dockTop:
                self.window.dockBottom.setVisible(False)
                self.window.dockLeft.setVisible(False)
            elif self.parent() == self.window.dockBottom:
                self.window.dockTop.setVisible(False)
                self.window.dockLeft.setVisible(False)
            else:
                self.window.dockTop.setVisible(False)
                self.window.dockBottom.setVisible(False)
            self.parent().showMaximized()
            self.whetherPress = 1 # 设置为已经最大化
            self.maxButton.setIcon(QApplication.style().standardIcon(
            QStyle.SP_TitleBarNormalButton))
        else:
            if self.parent() == self.window.dockTop:
                self.window.dockBottom.setVisible(True)
                self.window.dockLeft.setVisible(True)
            elif self.parent() == self.window.dockBottom:
                self.window.dockTop.setVisible(True)
                self.window.dockLeft.setVisible(True)
            else:
                self.window.dockTop.setVisible(True)
                self.window.dockBottom.setVisible(True)

            self.whetherPress = 0 
            self.parent().setFloating(False)
            self.maxButton.setIcon(QApplication.style().standardIcon(
            QStyle.SP_TitleBarMaxButton))

    def ViewDock(self):
        # 还原dock
        self.parent().setVisible(True)
        self.window.toolBar.removeAction(self.restoreAction)

