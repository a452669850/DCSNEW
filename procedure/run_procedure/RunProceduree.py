#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import QThread, QWaitCondition, QMutex, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QProgressBar, QMessageBox
from PyQt5.QtGui import QStandardItem
from utils.ClientModels import RunResult, Usecase, UsecaseGroup, Phrase
from utils.WorkModels import PointModel, NetworkConfig
from utils.core import MainWindowConfig
from DcsUi.ExcelDockWidget import clearAllItem
from time import strftime
from pubsub import pub
import uuid
import re
import json


class ProcedureThread(QThread):
    # 规程运行线程
    colorChange = pyqtSignal(int,int)
    logChange = pyqtSignal(int)
    quitThread = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(ProcedureThread, self).__init__(*args, **kwargs)
        self.pharses = Phrase.get_all() # 获取所有短语库
        self.phrase = {}
        for phrase in self.pharses: # 将短语库存入字典之中
            phraseList = [phrase.id, phrase.name, phrase.operation]
            self.phrase[phrase.name] = phrase.operation       

        self.parent = kwargs['parent']

        # self.run_debug = True  # 初始的单步运行状态
        self.run_procedure_number = ""  # 当前运行的规程编号
        self.run_procedure_name = ""  # 当前运行的规程名称
        self.run_usecase_group_name = ""  # 当前运行的用例组名字
        self.run_usecase_number = ""  # 当前运行的用例编号
        self.run_operation_section = 0  # 当前规程运行的用例中具体段落的索引
        self.run_text = {}  # 运行中返回来的文本
        self.run_big_sort_index = 0  # 运行的单步操作的index，比如四个检查只一个单步操作
        self.run_sort = 0  # 运行的单行操作的sort，每个检查都有自己sort
        self.run_result = True  # 运行结果True 或者False
        self.run_uuid = uuid.uuid1()  # 运行时UID
        self.run_type_dict = {'procedure' : 1,
                        'usecase': 3,
                        'usecasegroup': 2}
        self.start_delay_dict = {}
        self.current_loop_list = []
        self.run_usecase_index = 0
        self.run_type_map = 0
        self.certification = {}
        
        self.is_stop = 0
        self._isPause = False
        self._isWork = False
        self.cond = QWaitCondition()
        self.mutex = QMutex()
        self.logChange.connect(self.parent.dockBottom.updateLog)

    def pause(self):
        # 线程暂停
        self._isPause = True

    def resume(self):
        # 线程恢复
        self._isPause = False
        self.cond.wakeAll()

    def run(self):
        # 多线程执行
        self._isWork = True
        self.procedureExcel = self.parent.dockTop.ExcelTab.currentWidget()
        clearAllItem(self.procedureExcel)
        self.colorChange.connect(self.procedureExcel.changeRowColor)
        if self.run_type == 'procedure':
            self.run_procedure_number = self.procedureExcel.model.item(0,3).text()
            self.run_procedure_name = self.procedureExcel.model.item(0,1).text()
            self.run_usecase_number = self.procedureExcel.model.item(1,3).text()
            self.judgeIndex = [5, 6]
        if self.run_type == 'usecase':
            self.run_usecase_number = self.procedureExcel.model.item(0,3).text()
            self.judgeIndex = [6, 6]
        if self.run_type == 'usecasegroup':
            self.run_usecase_group_name = self.procedureExcel.groupName
            self.judgeIndex = [6, 6]
        while self._isWork:
            self.mutex.lock() # 线程锁
            if self._isPause:
                self.cond.wait(self.mutex)
            if self.parent.procedureRunIndex > self.procedureExcel.colsLen:
                self._isWork = None
                self.run_result = True
                self.save_run_result()
                self.msleep(MainWindowConfig.RunInterval)
                self.mutex.unlock()
                self.parent.procedureRunIndex = 0
                # reply = QMessageBox.question(self.parent, '提示', '执行完毕！', QMessageBox.Yes)
                self.exec_() # 关闭线程
            res = self.performAction(self.procedureExcel.getRowContent(self.parent.procedureRunIndex)) # 获取运行结果
            self.colorChange.emit(self.parent.procedureRunIndex, res) # 主界面中表格颜色进行变化
            self.logChange.emit(self.parent.procedureRunIndex) # 主界面中日志窗口更新
            self.parent.procedureRunIndex += 1
            self.msleep(1000)
            self.mutex.unlock()
        # self.colorChange.emit(-self.parent.procedureRunIndex + 1)
        self.parent.procedureRunIndex = 0

    def save_run_result(self):
        # 保存记录
        self.run_type_map = self.run_type_dict[self.run_type]
        runresult = RunResult()
        runresult.run_uuid = self.run_uuid
        runresult.procedure_number = self.run_procedure_number
        runresult.procedure_name = self.run_procedure_name
        runresult.usecase_group_name = self.run_usecase_group_name
        runresult.usecase_number = self.run_usecase_number
        runresult.operation_section = self.run_operation_section
        runresult.run_big_sort = self.run_big_sort_index
        runresult.section_sort = self.run_sort
        runresult.run_text = self.run_text
        runresult.run_result = self.run_result
        runresult.run_time = strftime("%Y-%m-%d %H:%M:%S")
        runresult.run_type = self.run_type_map
        runresult.run_usecase_index = self.run_usecase_index
        # 如果usecase_number 、operation_section、section_sort都相同，则是循环的操作，
        # 只需要更新即可，不能用保存
        exist_runresult = RunResult.select().where(RunResult.usecase_number == runresult.usecase_number,
                                                   RunResult.usecase_group_name == runresult.usecase_group_name,
                                                   # RunResult.run_uuid == runresult.run_uuid,
                                                   RunResult.operation_section == runresult.operation_section,
                                                   RunResult.section_sort == runresult.section_sort)
        if exist_runresult.first() == None:
            runresult.is_stop = self.is_stop
            runresult.run_text = json.dumps(self.run_text) 
            runresult.run_result = self.run_result
            runresult.run_time = strftime("%Y-%m-%d %H:%M:%S")
            runresult.certification = json.dumps(self.certification)
            runresult.save()
        if exist_runresult.first() != None:
            update_result = exist_runresult.first()
            update_result.run_text = json.dumps(self.run_text)
            update_result.run_result = self.run_result
            update_result.run_time = strftime("%Y-%m-%d %H:%M:%S")
            update_result.is_stop = self.is_stop
            update_result.certification = json.dumps(self.certification)
            RunResult.update_obj(update_result)

    def performAction(self, action):
        # 步骤执行函数
        if action is None or action == ' ':
            return
        if self.run_type == 'procedure':
            exResIndex = 3
            REsIndex = 4
            timeIndex = 7
        else:
            exResIndex = 4
            REsIndex = 3
            timeIndex = 2
        for key, value in self.phrase.items():
            if key in action:
                if value == 'SET' or not re.compile(u'[\u4e00-\u9fa5]').search(action) and '=' in action: # 如果当前步骤为设置
                    print(key)
                    if key in action: 
                        writeList = action.split('\n')[1:]
                    else:
                        writeList = action.split('\n')
                    for write in writeList:
                        write = write.split('=')
                        try:
                            self.procedureExcel.model.setItem(self.parent.procedureRunIndex, timeIndex, QStandardItem(strftime("%Y-%m-%d %H:%M:%S")))
                            result = MainWindowConfig.IOMapping.skio.write(write[0], float(re.findall('\d+',write[1])[0])) # 获取步骤执行结果
                            pub.subscribe(snoop, pub.ALL_TOPICS)
                            # print(MainWindowConfig.IOMapping.skio.write(write[0], float(re.findall('\d+',write[1])[0])))
                            if result:
                                self.procedureExcel.model.setItem(self.parent.procedureRunIndex, self.judgeIndex[0], QStandardItem('是'))
                                self.procedureExcel.model.setItem(self.parent.procedureRunIndex, REsIndex, QStandardItem(write[0] + '=' + str(result[0])))
                                self.run_text[action] = ['是', strftime("%Y-%m-%d %H:%M:%S"), '成功']
                                self.parent.log.infoLog(f'执行到{self.parent.procedureRunIndex}行,{action}成功')
                                # self.certification[action] = f'解析{action},通过短语库字段检索,判定该步骤为{value},解析到需要操作的变量为{write[0]},{self.search(write[0], value, result[0])}'
                                self.certification[action] = [value,write[0],self.search(write[0]), result[0]]
                                return 1
                            else:
                                self.procedureExcel.model.setItem(self.parent.procedureRunIndex, self.judgeIndex[1], QStandardItem('否'))
                                self.run_text[action] = ['否', strftime("%Y-%m-%d %H:%M:%S")]
                                self.parent.log.infoLog(f'执行到{self.parent.procedureRunIndex}行,{action}失败')
                                return 0
                        except Exception as e:
                            error = self.judgeError(e, write[0])
                            self.procedureExcel.model.setItem(self.parent.procedureRunIndex, self.judgeIndex[1], QStandardItem('否'))
                            self.run_text[action] = ['否', strftime("%Y-%m-%d %H:%M:%S"),error]
                            self.procedureExcel.model.setItem(self.parent.procedureRunIndex, REsIndex, QStandardItem(str(error)))
                            self.parent.log.warningLog(f'执行到{self.parent.procedureRunIndex}行,{action}失败,错误原因{e}')
                            # self.certification[action] = f'解析{action},通过短语库字段检索,判定该步骤为{value},解析到需要操作的变量为{write[0]},设置失败,错误原因{str(error)}'
                            self.certification[action] = [value,write[0],str(error)]
                            return 0
                elif value in 'CHECK':# 如果当前步骤为检查
                    read = re.sub('[\u4e00-\u9fa5]', '', action)
                    try:
                        self.procedureExcel.model.setItem(self.parent.procedureRunIndex, timeIndex, QStandardItem(strftime("%Y-%m-%d %H:%M:%S")))
                        result = str(MainWindowConfig.IOMapping.skio.read(read))
                        pub.subscribe(snoop, pub.ALL_TOPICS)
                        print(result)
                    except Exception as e:
                        error = self.judgeError(e, read)
                        self.procedureExcel.model.setItem(self.parent.procedureRunIndex, self.judgeIndex[1], QStandardItem('否'))
                        self.run_text[action] = ['否', strftime("%Y-%m-%d %H:%M:%S"), error]
                        self.procedureExcel.model.setItem(self.parent.procedureRunIndex, REsIndex, QStandardItem(str(error)))
                        self.parent.log.warningLog(f'执行到{self.parent.procedureRunIndex}行,{action}失败,错误原因{e}')
                        # self.certification[action] = f'解析{action},通过短语库字段检索,判定该步骤为{value},解析到需要操作的变量为{read},读取失败,错误原因为{str(error)}'
                        self.certification[action] = [value,read,str(error)]
                        result = None
                        return 0
                    expectedResult = self.procedureExcel.model.item(self.parent.procedureRunIndex, exResIndex).text().split('=')[-1]
                    self.procedureExcel.model.setItem(self.parent.procedureRunIndex, REsIndex, QStandardItem(read + '=' + result))
                    Operator = self.getOperator(re.compile('[<,<=,>,>=,=,≤,≥,==]').search(action))
                    if eval(f'{str(float(expectedResult))}{Operator}{str(float(result))}'):
                        self.procedureExcel.model.setItem(self.parent.procedureRunIndex, self.judgeIndex[0], QStandardItem('是'))
                        self.run_text[action] = ['是', strftime("%Y-%m-%d %H:%M:%S"), read + Operator + result]
                        self.parent.log.infoLog(f'执行到{self.parent.procedureRunIndex}行,{action}成功')
                        # self.certification[action] = f'解析{action},通过短语库字段检索,判定该步骤为{value},解析到需要操作的变量为{read},{self.search(read, value, result)},与预期结果{read}={expectedResult}相同'
                        self.certification[action] = [value,read,self.search(read),result,True]
                        return 1
                    else:
                        self.procedureExcel.model.setItem(self.parent.procedureRunIndex, self.judgeIndex[1], QStandardItem('否'))
                        self.run_text[action] = ['否', strftime("%Y-%m-%d %H:%M:%S"), read + Operator + result]
                        self.parent.log.infoLog(f'执行到{self.parent.procedureRunIndex}行,{action}成功')
                        # self.certification[action] = f'解析{action},通过短语库字段检索,判定该步骤为{value},解析到需要操作的变量为{read},{self.search(read)},与预期结果{read}={expectedResult}不符'
                        self.certification[action] = [value,read,self.search(read),result,False]
                        return 0


    def judgeError(self, e, value):
        # 判断异常的类型
        if str(e) == value:
            error = '未在变量表找到该变量'
        elif str(e) == '1':
            error = '功能码异常'
        elif str(e) == '2':
            error = '地址异常'
        elif str(e) == '[WinError 10061] 由于目标计算机积极拒绝，无法连接。':
            error = '未连接'
        else:
            error = str(e)
        return error

    def search(self, name):
        # 通道号
        channel = PointModel.get(PointModel.sig_name == name).channel
        # 通信接口
        slot = PointModel.get(PointModel.sig_name == name).slot
        # 协议
        protocol = NetworkConfig.get(NetworkConfig.slot == slot).protocol
        return [channel,protocol]

    def getOperator(self, Operator):
        # 将步骤中符号转换为语言中符号
        if Operator == '=':
            return '=='
        elif Operator == '≤':
            return '<='
        elif Operator == '≥':
            return '>='
        else:
            return Operator

def snoop(topicObj=pub.AUTO_TOPIC, **mesgData):
    print('topic "%s": %s' % (topicObj.getName(), mesgData))
         

