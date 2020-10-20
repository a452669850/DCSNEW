from PyQt5.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import QDockWidget, QTextBrowser
from DcsUi.DockCLass import NewDockWidget

class LogDockWidget(NewDockWidget):
    def __init__(self, title, parent=None):
        NewDockWidget.__init__(self, title, parent=parent)
        self.parent = parent
        self.logBrowser = QTextBrowser()
        self.logBrowser.setFont(QFont("Timers", 20));
        self.setWidget(self.logBrowser)

    def updateLog(self, rowIndex):
        # 更新记录文本框
        logCon = self.parent.dockTop.ExcelTab.currentWidget().getRowContent(rowIndex) # 获取当前执行步骤信息
        if logCon:
            self.logBrowser.append(logCon + '已经完成\r\n')
        else:
            pass
        if self.parent.dockTop.ExcelTab.currentWidget().colsLen == rowIndex:
            self.logBrowser.append('已经全部完成\r\n')
        self.cursor = self.logBrowser.textCursor() # 获取文本框游标
        self.logBrowser.moveCursor(self.cursor.End)
        
