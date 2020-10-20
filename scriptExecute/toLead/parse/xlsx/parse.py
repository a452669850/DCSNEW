import re
from pathlib import Path

# from robot.running.arguments.argumentparser import typing
import typing

from scriptExecute.execute.utils import logger
from scriptExecute.toLead.parse import opc
from scriptExecute.toLead.parse.xlsx.hook import PmsHook
from scriptExecute.toLead.parse.xlsx.meta import StepBlock, Script, StepLine


def scan(order, path: Path) -> typing.Optional[Script]:
    name = re.search('([^<>/\\\|:""\*\?]+\.\w+$)', str(path)).group().split('.')[0]
    with path.open('r') as fp:
        instance = Script(name, order)
        BodyReader().read(fp, instance)

        PmsHook().hook(instance)
        return instance


class BaseReader(object):
    def __init__(self):
        self.errors = []

    def read(self, input_, instance: Script):
        return NotImplemented

    def error(self, message):
        logger.error(message)
        self.errors.append(message)


class BodyReader(BaseReader):

    def read(self, input_, instance: Script):
        self._read_lines(input_, instance)
        _make_ast(instance)

    def _read_lines(self, input_, instance: Script):
        steps = input_.readline().strip()
        steps = steps.split('\t')
        assert steps[0] == 'Steps'
        steps = [int(x) for x in steps[1:]]
        comments = input_.readline().strip()
        comments = comments.split('\t')
        assert comments[0] == 'Comments'
        comments = [x for x in comments]
        icts = input_.readline().strip()
        icts = icts.split('\t')
        assert icts[0] == 'Input Capture Times'
        input_capture_times = [int(x[1:]) for x in icts[1:]]
        signals = []
        ops = []
        for step_id in range(len(steps)):
            ops.append([])
        for line in input_:
            line = line.strip()
            if not line: continue
            if line.startswith('//'): continue
            line = line.split('\t')
            sig_name = line[0]
            signals.append(sig_name)
            values = line[1:]
            for step_id in range(len(steps)):
                try:
                    ops[step_id].append(values[step_id])
                except IndexError:
                    ops[step_id].append('')
        a = set()
        for i in range(len(steps)):
            for j in range(len(signals) + 1):
                if i not in a:
                    block = StepBlock(
                        lineNo=j + 1,
                        stepNo=steps[i],
                        Input_Capture_Times=input_capture_times[i],
                        Comments=comments[i]
                    )
                    instance.lines.append(block)
                    a.add(i)
                    continue
                line = StepLine(
                    lineNo=j + 1,
                    stepNo=steps[i],
                    Input_Capture_Times=input_capture_times[i],
                    Comments=comments[i],
                    opStr=signals[j - 1] + '=' + ops[i][j - 1]
                )

                _parse_step_line(line)
                block.lines.append(line)


def _parse_step_line(line: StepLine):
    lis = line.opStr.split('=')
    op = opc.WRT(lineNo=line.lineNo, stepNo=line.stepNo, name=lis[0], value=float(lis[1]))
    line.ops.append(op)


def _make_ast(instance: Script):
    """生成树形结构
    - UseCase
        - StepBlock
            - StepLine
                - OpWrite
                - OpCheck
    """
    idx = 0
    lines = []
    while idx < len(instance.lines):
        block = instance.lines[idx]
        idx += 1

        if isinstance(block, StepBlock):
            lines.append(block)
            while idx < len(instance.lines):
                line = instance.lines[idx]
                idx += 1

                if isinstance(line, StepBlock):
                    idx -= 1
                    break
                else:
                    block.lines.append(line)
        else:
            lines.append(block)

    instance.lines = lines
