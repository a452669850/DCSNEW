import typing
from dataclasses import dataclass, field

from scriptExecute.toLead.parse import opc


@dataclass
class Script(object):
    name: str
    serial: str
    lines: typing.List['StepLine'] = field(default_factory=list)

    def __iter__(self) -> typing.Iterator[opc.OpCode]:
        yield opc.START()

        for block in self.lines:
            block: StepBlock
            yield opc.BLOCK(lineNo=block.stepNo)
            for line in block.lines:
                line: StepLine
                yield opc.LINE(lineNo=line.stepNo)
                for op in line.ops:
                    yield op
                yield opc.END()
            yield opc.END()
        yield opc.END()


@dataclass
class StepLine(object):
    """逻辑行"""
    lineNo: int
    stepNo: int
    Input_Capture_Times: int
    Comments: str = ''
    opStr: str = ''

    ops: typing.List[typing.Union['opc.WRT', 'opc.CHK']] = field(default_factory=list)


@dataclass
class StepBlock(object):
    """逻辑块"""
    lineNo: int
    stepNo: int
    Input_Capture_Times: int
    Comments: str = ''

    lines: typing.List['StepLine'] = field(default_factory=list)
