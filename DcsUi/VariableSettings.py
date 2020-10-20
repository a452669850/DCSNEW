from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

from DcsUi.TableFilter import VarDockWidget
from DcsUi.VarTreeView import VarTreeDockWidget
from DcsUi.variablecoercion.ToolBarClass import Deploy
# from DcsUi.variablecoercion.displaycolumnWindow import MyWindow
from DcsUi.variablecoercion.ToolBarClassWindow import DeployWindow
from DcsUi.variablecoercion.editTable import configure
from DcsUi.variablecoercion.model import variableGroupModel
from DcsUi.variablecoercion.preservationNewGroup import preservation
from mainwindow import MainWindow
from utils import core


class VariableSettingsUi(MainWindow):
    '''变量强制界面继承自主窗口'''
    def __init__(self):
        super(VariableSettingsUi, self).__init__()
        self.group = None
        self.initUI()
        self.newInitUI()

    def show(self):
        super(MainWindow, self).show()
        self.dockLeft.setMaximumWidth(300)

    def closeEvent(self, event):
        # 窗口关闭事件 覆盖主窗口中的关闭事件
        event.accept()

    def newInitUI(self):
        self.dockTop.deleteLater() # 销毁主窗口中的规程显示dock
        self.dockLeft.deleteLater()# 销毁主窗口中的树结构显示dock

        self.dockTop = VarDockWidget("变量", self) # 重新创建变量Dock
        self.addDockWidget(Qt.TopDockWidgetArea, self.dockTop)
        self.setCentralWidget(self.dockTop)

        self.dockLeft = VarTreeDockWidget('变量强制窗口', self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockLeft)

        self.splitDockWidget(self.dockLeft, self.dockBottom, Qt.Horizontal)
        self.splitDockWidget(self.dockLeft, self.dockTop, Qt.Horizontal)
        self.splitDockWidget(self.dockTop, self.dockBottom, Qt.Vertical)
        self.setDockNestingEnabled(True)
        self.dockBottom.hide()
        self.dockLeft.setMaximumWidth(250)

    # def varforceSetcolClicked(self):
    # self.varforceSetcolClickedUi = MyWindow()
    # self.varforceSetcolClickedUi.show()

    def varforceFindClicked(self):
        # 查找变量按钮点击事件
        self.varforceFindClickedUi = Deploy(group_name=self.group)
        self.varforceFindClickedUi.add_Group_Signal.connect(self.action1)
        self.varforceFindClickedUi.updata_Group_Signal.connect(self.action2)
        self.varforceFindClickedUi.show()

    def varforceEdiTupleClicked(self):
        # 变量组修改按钮点击事件
        if self.group == None:
            QMessageBox.information(
                self,
                "信息提示",
                "请选择变量组",
                QMessageBox.Yes | QMessageBox.No
            )
            return
        if not self.dockTop.varTab.currentWidget():
            QMessageBox.information(
                self,
                "信息提示",
                "请选择变量组",
                QMessageBox.Yes | QMessageBox.No
            )
            return
        self.varforceEdiTupleClickedUi = configure(group_name=self.group)
        self.varforceEdiTupleClickedUi.my_Signal.connect(self.action2)
        self.varforceEdiTupleClickedUi.show()

    def varforceNewGroupClicked(self):
        # 变量组创建新组按钮
        if self.group == None:
            QMessageBox.information(
                self,
                "信息提示",
                "请选择变量组",
                QMessageBox.Yes | QMessageBox.No
            )
            return
        if not self.dockTop.varTab.currentWidget():
            QMessageBox.information(
                self,
                "信息提示",
                "请选择变量组",
                QMessageBox.Yes | QMessageBox.No
            )
            return
        self.varforceNewGroupClickedUi = preservation(group_name=self.group)
        self.varforceNewGroupClickedUi.my_Signal.connect(self.action1)
        self.varforceNewGroupClickedUi.show()

    def varforceAllForceGroupClicked(self):
        # 查看变量所有组按钮
        self.varforceAllForceGroupClickedUi = DeployWindow(group_name=self.group, win_type=False)
        self.varforceAllForceGroupClickedUi.show()

    def action1(self):
        # 左侧树结构刷新函数
        self.dockLeft.refreshTree()

    def action2(self):
        # 刷新变量显示界面函数
        self.dockTop.varTab.currentWidget().queryModel.header = core.MainWindowConfig.header
        self.dockTop.varTab.currentWidget().queryModel.datas = variableGroupModel.selectGroupData(name=self.group)
        self.dockTop.varTab.currentWidget().queryModel.layoutChanged.emit()
