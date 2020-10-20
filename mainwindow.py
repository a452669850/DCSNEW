# -*- coding:utf-8 -*-
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QApplication, QWidget, QAction, QMenu, \
    QSystemTrayIcon

from DcsUi.Config.configwindows import configureWindow
from DcsUi.ExcelDockWidget import TabDockWidget
from DcsUi.LogDockWidget import LogDockWidget
from DcsUi.LogWindow import LogWindow
from DcsUi.MainToolBarClass import ToolBarSetting
from DcsUi.TreeView import TreeDockWidget
from DcsUi.pharse import PhraseUI
from DcsUi.proceduresManage import proceduresWindow
from DcsUi.stopRulesList.termination import termination
from DcsUi.testRecord.textRecordWindow import textRecordWindow
from DcsUi.useCaseGroupManagement.proceduresManage import proceduresWindow
from DcsUi.userManagement.accountManage import AccountManage
from DcsUi.Classification import ClassificationUi
from RealtimeDB.realtimeDB import realtimewindow
from historyinfluxDB.historyWindow import historyWindow
from procedure.manage_procedure.import_procedure import parse_procedure
from procedure.run_procedure.RunProceduree import ProcedureThread
from tools.JsonConfig import getProjectName, writeJson
from utils.InitDb import connectDb, judgeProjectPath
from utils.core import MainWindowConfig


# from procedure.run_procedure.runconfig import RunConfig
# from communication.communicationWindow import comWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.projectPath = None
        self.projectName = None
        self.procedureRunIndex = 0
        self.procedureRunPath = None

    def initUI(self):
        self.projectName = getProjectName(self.projectPath)
        # 连接数据库
        self.dbPath = connectDb(self.projectPath)

        # 创建工具栏和菜单栏
        self.toolBarSetting = ToolBarSetting(self)
        # 创建一个状态栏
        self.statusBar()

        # 初始化dock控件
        self.dockTop = TabDockWidget("Console", self)
        self.addDockWidget(Qt.TopDockWidgetArea, self.dockTop)
        self.setCentralWidget(self.dockTop)
        # log标签dock
        self.dockBottom = LogDockWidget("Log", self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.dockBottom)
        # tree结构dock
        self.dockLeft = TreeDockWidget("Project Explorer", self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dockLeft)

        # 设置初始dock大小
        self.dockLeft.setMaximumWidth(100)  # 设置最大宽度
        self.dockBottom.setMaximumHeight(250)  # 设置最大高度

        # 设置Dock布局
        self.splitDockWidget(self.dockLeft, self.dockBottom, Qt.Horizontal)
        self.splitDockWidget(self.dockLeft, self.dockTop, Qt.Horizontal)
        self.splitDockWidget(self.dockTop, self.dockBottom, Qt.Vertical)
        self.setDockNestingEnabled(True)  # 开启dock嵌套

        # 初始化窗体
        self.setWindowIcon(QIcon(':/static/default.png'))
        self.setWindowTitle(f"Dcs自动化测试软件[{self.projectName}]")
        self.setWindowState(Qt.WindowMaximized)
        self.addSystemTray()
        QApplication.setStyle('Fusion')

        #  初始化规程线程
        self.ProcedureThread = ProcedureThread(parent=self)

        self.log = LogWindow(self)

    def show(self):
        # 窗口显示函数 调整树结构大小
        super(MainWindow, self).show()
        self.dockLeft.setMaximumWidth(1920)

    def closeEvent(self, event):
        # 窗口关闭事件
        reply = QMessageBox.question(self,
                                     'Quit',
                                     "是否要退出程序？",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                MainWindowConfig.IOMapping.skio.close() # 关闭通讯线程
            except Exception as e:
                print(e)
            writeJson(self.projectPath) # json文件中写入最后一次打开工程
            event.accept()
        else:
            event.ignore()

    def viewDefaultClicked(self):
        # 窗口点击事件
        QApplication.processEvents()

    def projectCreateClicked(self):
        # 创建工程
        from DcsUi.newbuild import Ui_NewBuild
        self.projectCreateUi = Ui_NewBuild(parent=self)
        self.projectCreateUi.mainIsWorking = True
        self.projectCreateUi.show()

    def projectOpenClicked(self):
        # 打开工程
        self.newProjectPath = QFileDialog.getExistingDirectory(self, '选择文件夹', './')
        if judgeProjectPath(self.newProjectPath) and self.newProjectPath != self.projectPath:
            self.projectPath = self.newProjectPath
            connectDb(self.projectPath) # 重新连接数据库
            self.projectName = getProjectName(self.projectPath)
            self.dockTop.setWidget(QWidget()) # 清空excel展示区
            self.dockLeft.refreshTree()
            self.dockBottom.logBrowser.clear() # 清空底部日志
            self.log.infoLog(f'切换工程至:{self.projectName}')

    def projectSaveClicked(self):
        # 保存工程按钮点击事件
        print('pk')

    def proceduresImportClicked(self):
        # 导入规程
        self.procedurePath, filetype = QFileDialog.getOpenFileName(self, '选择文件', '',
                                                                   'Excel files(*.xlsx , *.xls)')  # 设置文件扩展名过滤,注意用双分号间隔
        if self.procedurePath:
            parse_procedure(self.procedurePath)
            self.dockLeft.refreshTree() # 刷新树结构
            self.log.infoLog(f'成功导入{self.procedurePath}')

    # def proceduresExportClicked(self):
    #     print(self)

    def varforceUpdateGroupClicked(self):
        # 用例组管理
        self.varforceUpdateGroupUi = proceduresWindow()
        self.varforceUpdateGroupUi.proced_Signal.connect(self.active_update)
        self.varforceUpdateGroupUi.setWindowModality(Qt.ApplicationModal)
        self.varforceUpdateGroupUi.show()

    # def proceduresDeleteClicked(self):
    #     # 删除规程
    #     print(self)

    def proceduresSettingsClicked(self):
        # 规程配置按钮
        self.proceduresSettingsUi = configureWindow()
        # self.proceduresSettingsUi.setWindowModality(Qt.ApplicationModal)
        self.proceduresSettingsUi.show()

    def procedureAutoRunClicked(self):
        # 规程自动运行
        if not self.procedureRunPath:
            reply = QMessageBox.question(self, '提示', '请先导入规程！', QMessageBox.Yes)
        elif self.ProcedureThread._isWork or self.ProcedureThread._isPause:
            reply = QMessageBox.question(self, '提示', '有正在运行的线程！', QMessageBox.Yes)
        else:
            if self.procedureRunIndex == 0:
                self.dockBottom.logBrowser.clear()
            self.ProcedureThread = ProcedureThread(parent=self)
            self.ProcedureThread.run_type = self.dockTop.ExcelTab.currentWidget().type
            self.ProcedureThread.start()
            self.log.infoLog(f'{self.procedureRunPath}规程开始执行')

    def procedureDebugClicked(self):
        # 规程单步执行
        if not self.procedureRunPath:
            reply = QMessageBox.question(self, '提示', '请先导入规程！', QMessageBox.Yes)
        elif self.procedureRunIndex == self.dockTop.TabelView.colsLen:
            self.dockTop.TabelView.changeRowColor(-self.procedureRunIndex + 1) # 表格中的颜色变更
            self.procedureQuitClicked() # 退出规程
            self.procedureRunIndex = 0
            self.ProcedureThread.save_run_result() # 存储结果
            reply = QMessageBox.question(self, '提示', '已全部执行完毕！', QMessageBox.Yes)
        elif self.ProcedureThread._isWork and not self.ProcedureThread._isPause:
            reply = QMessageBox.question(self, '提示', '有正在自动运行的线程！', QMessageBox.Yes)
        else:
            if self.procedureRunIndex == 0:
                self.dockBottom.logBrowser.clear()
            self.ProcedureThread.judgeIndex = [6, 6]
            if hasattr(self.ProcedureThread, 'procedureExcel'):
                res = self.ProcedureThread.performAction(
                    self.ProcedureThread.procedureExcel.getRowContent(self.procedureRunIndex)) # 获取执行结果
                self.ProcedureThread.procedureExcel.changeRowColor(self.procedureRunIndex, res)
            else:
                res = self.ProcedureThread.performAction(
                    self.dockTop.ExcelTab.currentWidget().getRowContent(self.procedureRunIndex))
                self.dockTop.ExcelTab.currentWidget().changeRowColor(self.procedureRunIndex, res)
                self.ProcedureThread.procedureExcel = self.dockTop.ExcelTab.currentWidget()
            self.dockBottom.updateLog(self.procedureRunIndex)
            self.procedureRunIndex += 1

    def procedurePauseClicked(self):
        # 暂停/继续规程
        if not self.ProcedureThread._isWork:
            reply = QMessageBox.question(self, '提示', '没有正在运行的线程！', QMessageBox.Yes)
        elif self.ProcedureThread._isPause:
            self.ProcedureThread.resume()
            self.log.infoLog(f'{self.procedureRunPath}规程继续执行')
        else:
            self.ProcedureThread.pause()
            self.ProcedureThread.is_stop = 1
            self.ProcedureThread.save_run_result()
            self.ProcedureThread.is_stop = 0
            self.log.infoLog(f'{self.procedureRunPath}规程暂停执行')

    def procedureQuitClicked(self):
        # 退出规程
        if self.ProcedureThread._isPause:
            self.ProcedureThread.resume()
        self.ProcedureThread.save_run_result()
        self.procedureRunIndex = 0
        self.ProcedureThread._isWork = False
        self.log.infoLog(f'退出{self.procedureRunPath}')

    def procedureListPauseClicked(self):
        # 终止规程列表按钮点击事件
        self.procedureListPauseUi = termination(self)
        self.procedureListPauseUi.setWindowModality(Qt.ApplicationModal)
        self.procedureListPauseUi.show()

    # def propertySettingsClicked(self):
    #     print('okk')

    def variableSettingsClicked(self):
        # 变量组管理按钮点击事件
        from DcsUi.VariableSettings import VariableSettingsUi
        self.variableSettingsUi = VariableSettingsUi()
        self.variableSettingsUi.show()

    def logRunResultClicked(self):
        # 打开测试记录按钮点击事件
        self.logRunResultUi = textRecordWindow()
        self.logRunResultUi.setWindowModality(Qt.ApplicationModal)
        self.logRunResultUi.show()

    def logOperateClicked(self):
        # 日志点击事件
        self.log.show()

    def accountManagementClicked(self):
        # 用户管理点击事件
        self.AccountManagementUi = AccountManage()
        self.AccountManagementUi.setWindowModality(Qt.ApplicationModal)
        self.AccountManagementUi.show()

    def active_update(self):
        # 左侧树结构刷新函数
        self.dockLeft.refreshTree()

    def communicationClicked(self):
        # self.communicationUi = comWindow()
        # self.communicationUi.show()
        pass

    def pharseManagementClicked(self):
        # 短语库点击事件
        self.PhraseUI = PhraseUI()
        self.PhraseUI.setWindowModality(Qt.ApplicationModal)
        self.PhraseUI.show()

    def labelManagementClicked(self):
        # 规程分类点击事件
        self.LabelManageUi = ClassificationUi()
        self.LabelManageUi.setWindowModality(Qt.ApplicationModal)
        self.LabelManageUi.show()

    def addSystemTray(self):
        ''' 添加程序最小化到托盘 '''
        if self.__class__.__name__ == 'MainWindow':
            minimizeAction = QAction("最小化至托盘", self, triggered=self.hide)
            maximizeAction = QAction("最大化", self,
                                     triggered=self.showMaximized)
            restoreAction = QAction("还原", self,
                                    triggered=self.showNormal)
            quitAction = QAction("退出", self,
                                 triggered=self.close)
            self.trayIconMenu = QMenu(self)
            self.trayIconMenu.addAction(minimizeAction)
            self.trayIconMenu.addAction(maximizeAction)
            self.trayIconMenu.addAction(restoreAction)
            self.trayIconMenu.addSeparator()
            self.trayIconMenu.addAction(quitAction)
            self.trayIcon = QSystemTrayIcon(self)
            self.trayIcon.setIcon(QIcon(":/static/default.png"))
            self.trayIcon.setContextMenu(self.trayIconMenu)
            self.trayIcon.show()

    def realTrendClicked(self):
        # 实时趋势图点击事件
        self.realtimedb = realtimewindow()
        self.realtimedb.show()

    def historyTrendClicked(self):
        # 历史趋势图点击事件
        self.historydb = historyWindow()
        self.historydb.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.initUI()
    ex.show()
    sys.exit(app.exec_())
