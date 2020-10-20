from pathlib import Path

from peewee import SqliteDatabase

from scriptExecute.execute.utils import logger
from scriptExecute.toLead.parse import opc
from scriptExecute.toLead.parse.xlsx.meta import StepLine, StepBlock, Script
from utils.WorkModels import init_database, TimeCard


class PmsHook(object):
    TAG_FIX = '[HOOK.PMS]系统指令'

    def hook(self, instance: Script):
        """
        针对三门的项目，做如下变换

        1. 恢复 -> 依次调整到最后执行
        2. 试验结果确认 -> 去除尾部`_TIME`标记
        3. 初始化 -> 置`TTD`,`TSD`,`TRD`,`TWD`,`WD`等于`0`
        """
        self.fix_reset_block(instance)
        self.fix_init_block(instance)
        self.fix_trigger_block(instance)

    TAG_RESET = 3

    def fix_reset_block(self, instance):
        left, right = 0, len(instance.lines)
        while left < right:
            section = instance.lines[left]
            if isinstance(section, StepBlock):
                if self.TAG_RESET == section.stepNo:
                    logger.debug(f'[HOOK.PMS]检测到`{section.Comments}`逻辑块, 将调整到行尾执行')
                    instance.lines.pop(left)
                    instance.lines.append(section)
                    right -= 1
                    continue
            left += 1

    TAG_INIT = 1

    def fix_init_block(self, instance):
        for section in instance.lines:
            if isinstance(section, StepBlock) and section.stepNo == self.TAG_INIT:
                logger.debug(f'[HOOK.PMS]检测到`{section.Comments}`逻辑块, 将添加`TTD=0`,`TSD=0`,`TRD=0`,`TWD=0`,`WD=0`指令')
                fix1 = StepLine(lineNo=section.lineNo, stepNo=section.stepNo, opStr='计数器复位', Comments=self.TAG_FIX,
                                Input_Capture_Times=section.Input_Capture_Times)
                fix1.ops.append(opc.WRT(lineNo=section.lineNo, stepNo=section.stepNo, name='TTD', value=0))
                fix1.ops.append(opc.WRT(lineNo=section.lineNo, stepNo=section.stepNo, name='TSD', value=0))
                fix1.ops.append(opc.WRT(lineNo=section.lineNo, stepNo=section.stepNo, name='TWD', value=0))
                fix1.ops.append(opc.WRT(lineNo=section.lineNo, stepNo=section.stepNo, name='WD', value=0))
                section.lines.insert(0, fix1)

                # 初始化完成后设置 `TTD`
                fix2 = StepLine(lineNo=section.lineNo, stepNo=section.stepNo, Comments=self.TAG_FIX,
                                Input_Capture_Times=section.Input_Capture_Times)
                # 测试类型：有些测试的开始start信号由外部给予，通过此寄存器来区分。1为内部触发（此时需要和第6项配合）。2为外部触发。
                fix2.ops.append(opc.WRT(lineNo=section.lineNo, stepNo=fix2.stepNo, name='TTD',
                                        value=_test_type_from_number(instance.name)))
                # 当每次上位机写完所有需要写入的寄存器时，将此寄存器值加1，slave根据此寄存器辨别数据的新旧，检测到新数据就刷新硬件输出。
                # 当master重启时，将此寄存器复位为0，slave检测到0进行初始化，不刷新硬件输出。
                # 当发生溢出是复位到0.
                fix2.ops.append(opc.WRT(lineNo=section.lineNo, stepNo=fix2.stepNo, name='WD', value=1, incr=True))
                section.lines.append(fix2)
                continue

    TAG_TRIGGER = 2

    def fix_trigger_block(self, instance):
        for section in instance.lines:
            if isinstance(section, StepBlock) and self.TAG_TRIGGER == section.stepNo:
                logger.debug(f'[HOOK.PMS]检测到`{section.Comments}`逻辑块, 将添加`TSD=1`,`TWD++`,`WD++`指令')
                fix1 = StepLine(lineNo=section.lineNo, stepNo=section.stepNo, Comments=self.TAG_FIX,
                                Input_Capture_Times=section.Input_Capture_Times)
                # 测试输出发送完成累加器TWD：当发送测试和start信号完成，master将此寄存器加1。
                # slave根据此寄存器判断新值，并启动计时程序。需要注意的是，WD写入寄存器也应该加1.可以理解为WD是master发送所有数据的计数，TWD是测试部分的计数。
                # slave通过WD判断master是否写入了所有新数据，并刷新硬件。通过TWD判断master写入的新数据是不是包含了测试数据，是否需要启动计时卡计时。
                fix1.ops.append(opc.WRT(lineNo=section.lineNo, stepNo=fix1.stepNo, name='TSD', value=1))
                fix1.ops.append(opc.WRT(lineNo=section.lineNo, stepNo=fix1.stepNo, name='TWD', value=1, incr=True))
                fix1.ops.append(opc.WRT(lineNo=section.lineNo, stepNo=fix1.stepNo, name='WD', value=1, incr=True))
                section.lines.append(fix1)
                row = instance.lines.index(section)
        self.fix_check_time_block(instance, row)

    def fix_check_time_block(self, instance, row):
        # stepNo = 0 Input_Capture_Times= 0 表示检查时间
        section = StepBlock(lineNo=1, stepNo=0, Input_Capture_Times=0, Comments='检查时间')
        logger.debug(f'[HOOK.PMS]检测到`{section.Comments}`逻辑块, 将去除信号的`_TIME`后缀')
        for line in section.lines:
            if isinstance(line, StepLine):
                for op in line.ops:
                    if isinstance(op, opc.CHK):
                        if op.name.endswith('_TIME'):
                            op.name = op.name[:-5]
                            op.keep = 2
        fix1 = StepLine(lineNo=section.lineNo, stepNo=section.stepNo, opStr='等待计时卡数据清零', Comments=self.TAG_FIX,
                        Input_Capture_Times=section.Input_Capture_Times)
        fix1.ops.append(opc.CHK(lineNo=section.lineNo, stepNo=section.stepNo, name='T1', value=0, operator='=', keep=2))
        fix1.ops.append(opc.CHK(lineNo=section.lineNo, stepNo=section.stepNo, name='T2', value=0, operator='=', keep=2))
        fix1.ops.append(opc.CHK(lineNo=section.lineNo, stepNo=section.stepNo, name='T3', value=0, operator='=', keep=2))
        fix1.ops.append(opc.WRT(lineNo=section.lineNo, stepNo=section.stepNo, name='TRD', value=1, incr=True))
        find_script_timer(section, instance.name)
        section.lines.insert(0, fix1)
        instance.lines.insert(row + 1, section)


def find_script_timer(section, name):
    '''查找脚本所需要检查的计时卡'''
    datas = TimeCard.select().where(TimeCard.pid == name)
    for i in datas:
        fix1 = StepLine(
            lineNo=section.lineNo,
            stepNo=section.stepNo,
            opStr=f'检查{i.sig_name}动作时间',
            Input_Capture_Times=section.Input_Capture_Times,
            Comments=section.Comments
        )
        fix1.ops.append(
            opc.CHK(lineNo=section.lineNo, stepNo=section.stepNo, name=i.sig_name, value=i.tm_out, operator='<=',
                    keep=2))
        section.lines.append(fix1)


def _find_timer_from_sig_name(number, name):
    """通过脚本名/信号名查找计时卡信息"""
    pass


def _test_type_from_number(number):
    """测试类型"""
    if number.startswith('XITR'):
        return 2
    elif number.startswith('XOTR'):
        return 3
    else:
        return 1
