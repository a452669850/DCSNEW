import logging
import random
import time
import typing
from queue import Queue
from threading import Thread, RLock, Event

from pubsub import pub

from scriptExecute.execute.utils import RunMode, RunState, RunResultRecord
from scriptExecute.toLead.parse import opc
from utils import core
from utils.WorkModels import PointModel


class DcsRunTime(Thread):
    __program: typing.Optional['Script']

    def __init__(self):
        Thread.__init__(self)

        self.logger = logging.getLogger('DcsRuntime  ')

        self.__mutex = RLock()
        self.__event = Event()
        self.__queue = Queue()

        self.__program = None
        self.__stack = []

        # 执行模式
        self.__mode = RunMode.AUTO
        # 执行状态
        self.__state = RunState.IDLE
        # 运行标志
        self.__flag = True

    def run(self) -> None:
        """工作循环"""
        while self.__flag:
            self._idle()
            self._running()

    def close(self):
        """关闭线程"""
        self.__flag = False
        self.join(.1)

    def mode(self):
        return self.__mode

    def state(self):
        return self.__state

    def SetMode(self, mode):
        """切换执行模式"""
        self.logger.info(f'[cmd.mode] {self.mode()} -> {mode}')
        with self.__mutex:
            self.__mode = mode

    def Start(self, program):
        """开始执行"""
        self.logger.debug(f'[cmd.start] M={self.mode()}, P=`{program.name}/{program.serial}`')
        self.__queue.put(program)

    def Pause(self):
        """暂停执行"""
        self.__event.clear()

    def Next(self):
        """下一步"""
        self.__event.set()

    def Exit(self):
        """退出"""
        pass

    def _idle(self):
        self.__state = RunState.IDLE
        self.__event.set()
        self.logger.debug(f'[{self.state()}] waiting new program')
        program = self.__queue.get(block=True, timeout=None)
        with self.__mutex:
            # 设置待运行 `Program` 对象
            self.__program = program

    def _running(self):
        self.__state = RunState.RUNNING

        # 保存到临时变量，避免运行中切换了规程
        program = self.__program
        if not program:
            self.logger.error(f'[{self.state()}] no program, exit(-1)')
            return -1

        try:
            self._before_running(program)
            self._doing_running(program)
        finally:
            # 必须执行的工作放在 `finish` 段内
            self._finish_running(program)

    def _before_running(self, program):
        self.logger.info(f'[{self.state()}] before running, M={self.mode()}, P=`{program.name}/{program.serial}`')

    def _doing_running(self, program):
        for op in program:
            # self.logger.debug(f'[{self.state()}] {op}')
            if op.opType == opc.START.opType:
                self._on_start(program, op)
            elif op.opType == opc.BLOCK.opType:
                self._on_block(program, op)
                self.__wait()
            elif op.opType == opc.LINE.opType:
                self._on_line(program, op)
                self.__wait()
            elif op.opType == opc.END.opType:
                self._on_end(program, op)
            elif op.opType == opc.WRT.opType:
                self._on_wrt(program, op)
            elif op.opType == opc.CHK.opType:
                self._on_chk(program, op)

    def _finish_running(self, program):
        self.logger.info(f'[{self.state()}] finished')
        pub.sendMessage('asd', line=None, name=None, value=None, stepNo=None, 返回状态=None, finished=True)

    def _on_start(self, program, op):
        self.logger.info(f'[执行:L{op.lineNo:03d}]规程开始')
        _new_record_from_op(op)
        self.__stack.append(op)  # 入栈，等待END命令出栈

    def _on_block(self, program, op):
        self.logger.info(f'[执行:L{op.lineNo:03d}]逻辑块开始')
        _new_record_from_op(op)
        self.__stack.append(op)

    def _on_line(self, program, op):
        self.logger.info(f'[执行:L{op.lineNo:03d}]逻辑行开始')
        _new_record_from_op(op)
        self.__stack.append(op)

    def _on_end(self, program, op):
        start_op: opc.OpCode = self.__stack.pop(-1)
        if start_op.opType == opc.START.opType:
            self.logger.info(f'[执行:L{op.lineNo:03d}] 规程执行完毕')

            # 循环执行
            if self.mode() == RunMode.LOOP:
                self.logger.info(f'[执行:L{op.lineNo:03d}]循环执行`{program.cNo}`')
                self.Start(program)

        elif start_op.opType == opc.BLOCK.opType:
            self.logger.info(f'[执行:L{start_op.lineNo:03d}]逻辑块执行完毕')
        elif start_op.opType == opc.LINE.opType:
            self.logger.info(f'[执行:L{start_op.lineNo:03d}]行执行完毕')

    def _on_wrt(self, program, op):
        lis = core.MainWindowConfig.IOMapping.skio.write(name=op.name, value=op.value)
        sat = lis[1]
        self.logger.info(f'[执行:L{op.lineNo:03d}]设置`{op.name}={op.value}` 返回状态: `{sat}`')

        # 发送测试结果
        record = _new_record_from_op(op, op.value)
        record.sat = sat
        record.message = f'{op.name}={op.value}'
        line = self.__stack.pop(-1)
        line.record.children.append(record)
        self.__stack.append(line)
        pub.sendMessage('asd', line=op.lineNo, name=op.name, value=op.value, stepNo=op.stepNo, 返回状态=sat)

    def _on_chk(self, program, op):
        name = op.name
        if op.name in ('T1', 'T2', 'T3'):
            name = PointModel.get(PointModel.channel == op.name).sig_name
        try:
            val = core.MainWindowConfig.IOMapping.skio.read(name=name)
            sat = True
        except:
            sat = False
        if op.keep > 0:
            _timeout = True
            t0 = time.time()
            while time.time() - t0 < op.keep:
                time.sleep(.01)
                if sat:
                    _timeout = False
                    self.logger.info(f'[执行:L{op.lineNo:03d}]检查`{op.name}{op.operator}{op.value}` 返回状态: `{sat}`')
                    # 发送测试结果
                    _new_record_from_op(op, val)
                    op.record.sat = sat
                    op.record.message = f'{op.name}{op.operator}{op.value}'
                    line = self.__stack.pop(-1)
                    line.record.children.append(op.record)
                    self.__stack.append(line)
                    pub.sendMessage('asd', line=op.lineNo, name=op.name, value=op.value, stepNo=op.stepNo, 报告=line,
                                    返回状态=sat, 返回值=val)
                    return

            self.logger.info(f'[执行:L{op.lineNo:03d}]检查`{op.name}{op.operator}{op.value}` 返回状态: `{sat}` [超时]')
            # 发送测试结果
            _new_record_from_op(op, val)
            op.record.sat = sat
            op.record.message = f'{op.name}{op.operator}{op.value}[超时]'
            line = self.__stack.pop(-1)
            line.record.children.append(op.record)
            self.__stack.append(line)
            pub.sendMessage('asd', line=op.lineNo, name=op.name, value=op.value, stepNo=op.stepNo, 报告=line, 返回状态=sat,
                            返回值=val)
            return

        sat = random.random() < .8
        self.logger.info(f'[执行:L{op.lineNo:03d}]检查`{op.name}{op.operator}{op.value}` 返回状态: `{sat}`')
        # 发送测试结果
        _new_record_from_op(op, val)
        op.record.sat = sat
        op.record.message = f'{op.name}{op.operator}{op.value}'
        line = self.__stack.pop(-1)
        line.record.children.append(op.record)
        self.__stack.append(line)
        pub.sendMessage('asd', line=op.lineNo, name=op.name, value=op.value, stepNo=op.stepNo, 报告=line, 返回状态=sat,
                        返回值=val)

    def __wait(self):
        if self.mode() == RunMode.STEP:
            self.__event.clear()
            self.__event.wait()
        elif self.mode() == RunMode.AUTO:
            time.sleep(.1)
            self.__event.wait()
        elif self.mode() == RunMode.LOOP:
            time.sleep(.1)
            self.__event.wait()


def _new_record_from_op(op, value=None):
    record = RunResultRecord(lineNo=op.lineNo, sat=True, message='', time=time.time(), value=value)
    op.record = record
    return record
