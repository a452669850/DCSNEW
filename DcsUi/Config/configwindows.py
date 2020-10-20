import csv
import re

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

from DcsUi.Config.configure import textEnvironment, networkConfiguration, environmentChecking, timeInterval
from DcsUi.Config.getData import getListData
from DcsUi.Config.importThread import myQThreading
from DcsUi.userManagement.AccountManagement import AccountManagement
from scriptExecute.window.scriptimport import scriptImprort
from utils import core
from utils.WorkModels import *


class textEnviron(textEnvironment):
    def __init__(self):
        textEnvironment.__init__(self)

    def leadingIn(self):
        """查询配置表数据数据"""
        dirPath = QtWidgets.QFileDialog.getOpenFileName(self,
                                                        "选取文件",
                                                        "./"
                                                        )[0]
        if dirPath != '':
            self.threading = myQThreading(path=dirPath)
            self.threading.sinOut.connect(self.textset)
            self.threading.start()

    def timecard(self):
        """导入时间卡"""
        dirPath = QtWidgets.QFileDialog.getOpenFileName(self,
                                                        "选取文件",
                                                        "./"
                                                        )[0]
        if dirPath != '':
            with open(dirPath, 'r') as csvfile:
                bulk = []
                for x in csv.DictReader(csvfile):
                    bulk.append(x)
                TimeCard.delete().execute()
                chunk = []
                for x in bulk:
                    chunk.append(x)
                    if len(chunk) < 50:
                        continue
                    TimeCard.insert_many(chunk).execute()
                    chunk.clear()
                TimeCard.insert_many(chunk).execute()
                chunk.clear()
                bulk.clear()

    def getdicdata(self):
        """获取表格数据"""
        lis = []
        # dev_list = NetworkConfig.filter(NetworkConfig.protocol == 'SMPXI')
        # var_list = PointModel.filter(PointModel.slot.in_([x.slot for x in dev_list])).order_by(PointModel.id)
        var_list = [j for j in PointModel.select()]
        for i in var_list:
            self.list_name.append(i)
            lis.append([i.id, i.sig_name, i.sig_type, i.slot, i.channel])
        return lis

    def textset(self, text):
        """用来刷新表格数据"""
        if text == '导入Excel完成\n':
            self.queryModel.datas = self.getdicdata()
            self.queryModel.layoutChanged.emit()

    def search(self):
        """搜索"""
        lis = []
        text = self.line.text()
        for i in self.list_name:
            if text in i.sig_name:
                lis.append([i.id, i.sig_name, i.sig_type, i.slot, i.channel])
        self.queryModel.datas = lis
        self.queryModel.layoutChanged.emit()


class networkConfig(networkConfiguration):
    def __init__(self):
        networkConfiguration.__init__(self)

    def getdicdata(self):
        """查询配置表数据数据"""
        lis = []
        datas = NetworkConfig.select()
        for x in datas:
            lis.append([x.id, x.slot, x.description, x.uri])
        return lis

    def search(self):
        """搜索"""
        text = self.line.text()
        datas = getListData.search_NetworkConfig(text)
        self.queryModel.datas = datas
        self.queryModel.layoutChanged.emit()


class environmentCheck(environmentChecking):
    def __init__(self):
        environmentChecking.__init__(self)

    def startSelfscan(self):
        """开始自检"""
        if self.threading.isRunning():
            QMessageBox.information(
                self,
                "信息提示",
                "正在自检请勿点击",
                QMessageBox.Yes | QMessageBox.No
            )
            return
        else:
            self.queryModel.datas = []
            self.queryModel.layoutChanged.emit()
            self.threading.start()

    def slotAdd(self, lis):
        """该函数是刷新界面数据没自检完成一条就会在表格后面加一条"""
        self.queryModel.append_data(lis)


class timeInter(timeInterval):
    def __init__(self):
        timeInterval.__init__(self)

    def confirm(self):
        """设置时间的按钮功能函数"""
        fieldData = {}
        qletext = self.qle.text()
        boxtext = self.box.currentText()
        fieldData['time'] = qletext or str((core.MainWindowConfig.RunInterval or 0.5) * 1000)
        fieldData['ensure'] = boxtext or core.MainWindowConfig.ContinueRunFalse
        continue_run_false = True if fieldData['ensure'] == u'是' else False
        if re.match(r'^[0-9]+\.[0-9]+$', fieldData['time']):
            if int(float(fieldData['time'])) > 3000 or int(float(fieldData['time'])) < 300:
                QMessageBox.information(
                    self,
                    "信息提示",
                    "请输入300-3000之间的整数！",
                    QMessageBox.Yes | QMessageBox.No
                )
            else:
                set_time = float(fieldData['time'])
                core.MainWindowConfig.ContinueRunFalse = continue_run_false
                core.MainWindowConfig.RunInterval = set_time
                QMessageBox.information(
                    self,
                    "信息提示",
                    "设置成功，请关闭窗口！",
                    QMessageBox.Yes | QMessageBox.No
                )
        else:
            QMessageBox.information(
                self,
                "信息提示",
                "输入有误，请重新输入！",
                QMessageBox.Yes | QMessageBox.No
            )


class configureWindow(AccountManagement):
    """该类是配置按钮的窗口"""
    def __init__(self):
        super().__init__()
        self.setObjectName('配置')
        self.setWindowTitle('配置')

    def _setdata_(self):
        """这个函数是用来加载选项卡窗口和选项卡文字及图片"""
        win1 = textEnviron()
        win2 = networkConfig()
        win3 = environmentCheck()
        win4 = timeInter()
        win5 = scriptImprort()
        self.lis_name = ['测试环境', '网络配置', '环境自检', '时间间隔', '时间响应']
        self.lis_win = [win1, win2, win3, win4, win5]
        self.lis_img = [
            ':/static/environment_settings_icon0.png',
            ':/static/NetworkSettings.png',
            ':/static/VariableSettings.png',
            ':/static/time_interval.png',
            ':/static/closed_loop_response_time.png'
        ]

    def changeData(self):
        """该函数是为了防止选项卡切换时放生数据混乱"""
        win = self.right_widget.currentWidget()
        if hasattr(win, 'getdicdata'):
            win.queryModel.datas = win.getdicdata()
            win.queryModel.layoutChanged.emit()

    def closeEvent(self, event):
        """该函数是为了在配置按钮退出后关闭配置窗口中运行的线程"""
        win = self.right_widget.widget(2)
        win.threading.interrupt.emit('')
        self.close()
