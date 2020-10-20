# -*- coding: UTF-8 -*-
"""
    规程运行，包括单步运行，暂停，恢复，退出等操作
"""

# 运行规程,先确定要运行的规程，或者用例组，或者用例的id，再定位到表里面的具体操作
from procedure.manage_procedure.models import (
    Procedure, Usecase, UsecaseGroup,
    RunResult, InitProcedure, StatisticalReport,
    LoopRunResult
)
import json, sys
import threading
import uuid
import wx
from utils import core
from ui_dcs import ui_utils
from operation import init_operation, write_operation, read_operation
from time import strftime
from test.log_info import DCSLog, DCSLogType


class RunConfig(threading.Thread):
    def __init__(self, run_type, value, run_action='run'):
        """
        :param run_type:
                可以传入usecase_number 或者 procedure_number 或者 usecase_group_name，都是单独传入，不能同时传入
        :param value:
                number
        :param run_action:
                'run'：顺序执行            'debug'： 单步执行
        """
        self.sleep_time = 0.5
        self.is_loop_run = False
        self.run_interval = self.sleep_time + 2
        threading.Thread.__init__(self)
        self.__flag = threading.Event()  # 用于暂停线程的标识
        self.__flag.set()  # 设置为True
        self.__running = threading.Event()  # 用于停止线程的标识
        self.__running.set()  # 将running设置为True

        self.run_action = run_action
        self.runPauseStatusToggle = 'run'

        self.run_debug = True  # 初始的单步运行状态
        self.run_procedure_number = ""  # 当前运行的规程编号
        self.run_procedure_name = ""  # 当前运行的规程名称
        self.run_usecase_group_name = ""  # 当前运行的用例组名字
        self.run_usecase_number = ""  # 当前运行的用例编号
        self.run_operation_section = 0  # 当前规程运行的用例中具体段落的索引
        self.run_text = ""  # 运行中返回来的文本
        self.run_big_sort_index = 0  # 运行的单步操作的index，比如四个检查只一个单步操作
        self.run_sort = 0  # 运行的单行操作的sort，每个检查都有自己sort
        self.run_result = True  # 运行结果True 或者False
        self.run_uuid = uuid.uuid1()  # 运行时UID
        self.run_is_complete = False
        self.run_type = ""
        self.start_delay_dict = {}
        self.current_loop_list = []
        self.run_type_map = 1
        self.run_usecase_index = 0
        self.continue_run = False
        from dcs_io.iocontroller import IOController
        self.io_controller = IOController()
        self.io_controller.io_mapping.load_point_table(ui_utils.GetStaticPath("modbus_slave_simulator.xlsm"))
        if run_type == "procedure_number":
            self.procedure = Procedure.get(Procedure.number == value)
            self.run_procedure_number = value
            self.run_procedure_name = self.procedure.name
            self.run_usecase_number = json.loads(self.procedure.usecase)[0]
            self.run_usecase_obj = Usecase.get(Usecase.number == self.run_usecase_number)
            self.run_type = "procedure"
            self.run_type_map = 1
        elif run_type == "usecase_group_name":
            self.usecasegroup = UsecaseGroup.get(UsecaseGroup.id == value)
            self.run_usecase_group_name = self.usecasegroup.name
            self.run_usecase_number = json.loads(self.usecasegroup.usecase)[0]
            self.run_usecase_obj = Usecase.get(Usecase.number == self.run_usecase_number)
            self.run_type = "usecasegroup"
            self.run_type_map = 2
        elif run_type == "usecase_number":
            self.usecase = Usecase.get(Usecase.number == value)
            self.run_usecase_number = value
            self.run_type = "usecase"
            self.run_type_map = 3
        else:
            print "运行类型错误"
            sys.exit(0)

    # 终止列表重新运行配置
    @classmethod
    def rerun_config(cls, result_id):
        result = RunResult.get(RunResult.id == result_id)
        if result.procedure_number != "":
            runconfig = cls("procedure_number", result.procedure_number, run_action='run')
        elif result.usecase_group_name != "":
            usecase_group_id = UsecaseGroup.get(UsecaseGroup.name == result.usecase_group_name).id
            runconfig = cls("usecase_group_name", usecase_group_id, run_action='run')
        else:
            runconfig = None
        runconfig.run_uuid = result.run_uuid
        runconfig.run_usecase_number = result.usecase_number
        runconfig.run_operation_section = result.operation_section
        runconfig.run_usecase_index = result.run_usecase_index
        runconfig.run_sort = result.section_sort
        runconfig.run_usecase_obj = Usecase.get(Usecase.number == runconfig.run_usecase_number)
        runconfig.run_big_sort_index = result.run_big_sort

        runconfig.continue_run = True
        runconfig.start()
        runconfig.pause()
        runconfig.run_debug = False
        return runconfig

    # 根据sort获取big_sort
    def get_big_sort(self, run_usecase_obj, operation_section, section_sort):
        operation = json.loads(run_usecase_obj.operation)
        section = operation[operation_section]
        big_section_sort = 0
        for m in range(1, len(section)):

            for i in range(1, len(section[m])):
                if int(section[m][i]["sort"]) == section_sort:
                    return big_section_sort
            big_section_sort = big_section_sort + 1

    # 顺序运行的入口
    def run(self):
        if not InitProcedure.select().limit(1):
            log = DCSLog(u'请导入初始化规程', DCSLogType.ERROR)
            core.Client.Project.AddLog(log)
            core.Client.setCurrentRun(None)
            core.Client.RunDirty = True
            return False
        while self.__running.isSet():
            self.__flag.wait()  # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            if self.run_type == "procedure":
                self.run_procedure()
            elif self.run_type == "usecasegroup":
                self.run_usecase_group()
            elif self.run_type == "usecase":
                self.run_usecase()
            else:
                print "运行类型错误"
                sys.exit(0)

    def pause(self):
        self.__flag.clear()  # 设置为False, 让线程阻塞
        self.runPauseStatusToggle = 'pause'

    def resume(self):
        self.__flag.set()  # 设置为True, 让线程停止阻塞
        self.runPauseStatusToggle = 'run'

    def current_stop(self):
        self.__flag.set()  # 将线程从暂停状态恢复, 如果已经暂停的话
        self.__running.clear()  # 设置为False
        from test.log_info import DCSLog, DCSLogType
        name = u'%s-%s' % (self.run_procedure_number or self.run_usecase_number, self.run_usecase_group_name)
        log = DCSLog(u'%s运行结束' % name, DCSLogType.DEFAULT)
        core.Client.Project.AddLog(log)
        del self
        core.Client.setCurrentRun(None)
        core.Client.RunDirty = True

    def stop(self):
        self.__flag.set()  # 将线程从暂停状态恢复, 如果已经暂停的话
        self.__running.clear()  # 设置为False
        self.join(1)
        from test.log_info import DCSLog, DCSLogType
        name = u'%s-%s' % (self.run_procedure_number or self.run_usecase_number, self.run_usecase_group_name)
        log = DCSLog(u'%s运行结束' % name, DCSLogType.DEFAULT)
        core.Client.Project.AddLog(log)
        del self
        core.Client.setCurrentRun(None)
        core.Client.RunDirty = True

    # 单步运行程序，第一次调用判断run_debug的值进而决定是否起线程
    def debug(self):
        if self.run_debug == True:
            self.start()
            self.pause()
            self.run_debug = False
        else:
            self.resume()
            self.pause()

    # 运行规程,顺序运行
    def run_procedure(self):
        if self.run_usecase_number == json.loads(
                self.procedure.usecase)[0] and self.run_operation_section == 0 and self.run_big_sort_index == 0:
            print "开始运行规程", self.procedure.name
            core.Client.CurrentProcedureEditor.SetOperationsNumberValue(self.run_usecase_number, '', '')
        self.run_usecase_operation(json.loads(self.run_usecase_obj.operation))

    # 运行用例组,顺序运行
    def run_usecase_group(self):
        if self.run_usecase_number == json.loads(
                self.usecasegroup.usecase)[0] and self.run_operation_section == 0 and self.run_big_sort_index == 0:
            print "开始运行用例组", self.usecasegroup.name
            core.Client.CurrentProcedureEditor.SetOperationsNumberValue(self.run_usecase_number, '', True)
        self.run_usecase_operation(json.loads(self.run_usecase_obj.operation))

    # 运行用例,顺序运行
    def run_usecase(self):
        print "运行的用例是", self.usecase.name
        operation = json.loads(self.usecase.operation)
        self.run_usecase_operation(operation)

    # 运行用例大步操作集，顺序运行
    def run_usecase_operation(self, operation):
        if self.run_big_sort_index == 0:
            tmp_number = u'%s-%s-%s' % (self.run_usecase_number, self.run_operation_section, 0)
            core.Client.CurrentProcedureEditor.SetOperationsNumberValue(tmp_number, '', True)
        section = operation[self.run_operation_section]
        self.run_usecase_section(section)

    # 运行操作集中的一个section
    def run_usecase_section(self, section):
        section_big_sort = section[self.run_big_sort_index]
        if self.run_big_sort_index > 0:
            self.run_usecase_sort(section_big_sort)
        else:
            self.run_big_sort_index += 1

    # 运行单条指令
    def run_usecase_sort(self, section_big_sort):
        run_operation_result = self.run_operation(section_big_sort)
        if (not core.Client.ContinueRunFalse) and (not self.is_loop_run):
            while not run_operation_result :
                retCode = wx.MessageBox(u'是否运行下一条操作',u'操作不通过,确认继续运行吗？',  wx.YES_NO | wx.ICON_QUESTION)
                if retCode == wx.YES:
                    break
                run_operation_result = self.run_operation(section_big_sort)

        # 如果运行的单步索引等于当前section的长度-1，则将run_big_sort_index设为0，位下一个section做准备
        # 并且在此时，需要将section的索引+1,如果section索引的值等于当前operation的长度-1，则将run_operation_section设为0
        self.run_big_sort_index += 1
        tmp_operation = json.loads(self.run_usecase_obj.operation)
        if self.run_big_sort_index == len(tmp_operation[self.run_operation_section]):
            self.run_big_sort_index = 0
            self.run_operation_section += 1
            if self.run_operation_section == len(tmp_operation):
                self.run_operation_section = 0
                self.stop_run()

    def run_operation(self, section_big_sort):
        operate_map = {
            "INIT": init_operation,
            "WRITE": write_operation,
            "READ": read_operation,
        }
        return operate_map.get(section_big_sort[0])(self, section_big_sort)

    # 是否暂停当前运行的规程或者用例
    def stop_run(self):
        if self.run_type == "usecase":
            RunResult.update(is_stop=False).where(RunResult.run_uuid == self.run_uuid).execute()

            if not self.is_loop_run:
                # 更新统计报表
                self.save_statistical_report(self.run_usecase_number)
                # 停止线程
                self.current_stop()
            else:
                self.loop_init_config()
        if self.run_type == "procedure":
            # 判断是否还有下一个用例，如果没有就结束线程
            # tmp_usecase_index = json.loads(self.procedure.usecase).index(self.run_usecase_number)
            if self.run_usecase_index < len(json.loads(self.procedure.usecase)) - 1:
                self.run_usecase_number = json.loads(self.procedure.usecase)[self.run_usecase_index + 1]
                self.run_usecase_index += 1
                self.run_usecase_obj = Usecase.get(Usecase.number == self.run_usecase_number)
            else:
                RunResult.update(is_stop=False).where(RunResult.run_uuid == self.run_uuid).execute()

                if not self.is_loop_run:
                    # 更新统计报表
                    self.save_statistical_report(self.run_usecase_number)
                    # 停止线程
                    self.current_stop()
                else:
                    self.loop_init_config()
        if self.run_type == "usecasegroup":
            # 判断是否还有下一个用例，如果没有就结束线程
            # tmp_usecase_index = json.loads(self.usecasegroup.usecase).index(self.run_usecase_number)
            if self.run_usecase_index < len(json.loads(self.usecasegroup.usecase)) - 1:
                self.run_usecase_number = json.loads(self.usecasegroup.usecase)[self.run_usecase_index + 1]
                self.run_usecase_index += 1
                self.run_usecase_obj = Usecase.get(Usecase.number == self.run_usecase_number)
            else:
                RunResult.update(is_stop=False).where(RunResult.run_uuid == self.run_uuid).execute()
                if not self.is_loop_run:
                    # 更新统计报表
                    self.save_statistical_report(self.run_usecase_group_name)
                    # 停止线程
                    self.current_stop()
                else:
                    self.loop_init_config()

    def save_statistical_report(self, name_or_number):
        runResult = RunResult.select().where(RunResult.run_uuid == self.run_uuid)
        pass_Result = RunResult.select().where(
            (RunResult.run_uuid == self.run_uuid) & (RunResult.run_result == True))
        statisticalReport = StatisticalReport()
        statisticalReport.result_uuid = self.run_uuid
        statisticalReport.report_type = self.run_type_map
        statisticalReport.name_or_number = name_or_number
        statisticalReport.start_time = runResult[0].run_time
        statisticalReport.end_time = runResult[-1].run_time
        a = float(len(pass_Result))
        b = float(len(runResult))
        statisticalReport.pass_rate = "%.2f%%" % (a / b * 100)
        statisticalReport.operator = core.Client.User.username
        statisticalReport.save()

    # 存储运行结果
    def save_run_result(self):
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
        exist_runresult = RunResult.select().where(RunResult.run_uuid == runresult.run_uuid,
                                                   RunResult.usecase_number == runresult.usecase_number,
                                                   RunResult.operation_section == runresult.operation_section,
                                                   RunResult.section_sort == runresult.section_sort)
        if exist_runresult.first() == None:
            runresult.is_stop = True
            runresult.save()
        if exist_runresult.first() != None:
            update_result = exist_runresult.first()
            update_result.run_text = self.run_text
            update_result.run_result = self.run_result
            update_result.run_time = strftime("%Y-%m-%d %H:%M:%S")
            runresult.is_stop = True
            RunResult.update_obj(update_result)

    def save_loop_result(self):
        loopRunResult = LoopRunResult()
        loopRunResult.run_uuid = self.run_uuid
        loopRunResult.procedure_number = self.run_procedure_number
        loopRunResult.procedure_name = self.run_procedure_name
        loopRunResult.usecase_group_name = self.run_usecase_group_name
        loopRunResult.usecase_number = self.run_usecase_number
        loopRunResult.operation_section = self.run_operation_section
        loopRunResult.run_big_sort = self.run_big_sort_index
        loopRunResult.section_sort = self.run_sort
        loopRunResult.run_text = self.run_text
        loopRunResult.run_result = self.run_result
        loopRunResult.run_time = strftime("%Y-%m-%d %H:%M:%S")
        loopRunResult.run_type = self.run_type_map
        loopRunResult.run_usecase_index = self.run_usecase_index
        # 如果usecase_number 、operation_section、section_sort都相同，则是循环的操作，
        # 只需要更新即可，不能用保存
        exist_runresult = LoopRunResult.select().where(LoopRunResult.run_uuid == loopRunResult.run_uuid,
                                                       LoopRunResult.usecase_number == loopRunResult.usecase_number,
                                                       LoopRunResult.operation_section == loopRunResult.operation_section,
                                                       LoopRunResult.section_sort == loopRunResult.section_sort)
        if exist_runresult.first() == None:
            loopRunResult.is_stop = True
            loopRunResult.save()
        if exist_runresult.first() != None:
            update_result = exist_runresult.first()
            update_result.run_text = self.run_text
            update_result.run_result = self.run_result
            update_result.run_time = strftime("%Y-%m-%d %H:%M:%S")
            loopRunResult.is_stop = True
            LoopRunResult.update_obj(update_result)

    # 重新设置循环运行的参数
    def loop_init_config(self):
        self.run_uuid = uuid.uuid1()
        if self.run_type_map == 1:
            self.run_usecase_number = json.loads(self.procedure.usecase)[0]
        elif self.run_type_map == 2:
            self.run_usecase_number = json.loads(self.usecasegroup.usecase)[0]

        self.run_usecase_obj = Usecase.get(Usecase.number == self.run_usecase_number)
        self.run_operation_section = 0  # 当前规程运行的用例中具体段落的索引
        self.run_big_sort_index = 0  # 运行的单步操作的index，比如四个检查只一个单步操作
        self.run_sort = 0  # 运行的单行操作的sort，每个检查都有自己sort
        self.run_usecase_index = 0

        # TODO 重置运行界面的参数
        if core.Client.CurrentProcedureEditor:
            core.Client.CurrentProcedureEditor.resetAll()

# if __name__ == "__main__":
#     from utils import core
#     core.Client.setDb('C:\\Users\\zhan\\Desktop\\dcs_pro\\p1\\.resources\\dcs.db')
#     # core.Client.CurrentProcedureEditor.SetOperationsNumberValue(number, real_result, result_check)
#     run = RunConfig("procedure_number", "TP3RPN01")
#     run.start()
#     # run.start_run() #顺序运行规程
#     # run.step_run_procedure(1,1,1)
#     # run.save_run_result()
