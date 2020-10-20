import enum
import typing
from dataclasses import dataclass

from scriptExecute.execute.utils import RunResultRecord


class OpType(enum.Enum):
    START = 0
    END = 1

    BLOCK = 2
    LINE = 3
    WRT = 4
    CHK = 5


class OpCode(object):
    lineNo: int
    opType: OpType

    record: typing.Optional[RunResultRecord] = None


@dataclass
class START(OpCode):
    lineNo: int = 0
    opType: OpType = OpType.START


@dataclass
class END(OpCode):
    lineNo: int = 0
    opType: OpType = OpType.END


@dataclass
class BLOCK(OpCode):
    lineNo: int
    opType: OpType = OpType.BLOCK


@dataclass
class LINE(OpCode):
    lineNo: int
    opType: OpType = OpType.LINE


@dataclass
class WRT(OpCode):
    lineNo: int
    stepNo: int
    name: str
    value: float
    opType: OpType = OpType.WRT
    incr: bool = False


@dataclass
class CHK(OpCode):
    lineNo: int
    stepNo: int
    name: str
    value: float
    operator: str
    opType: OpType = OpType.CHK

    # 如果 `keep` 不为 `0` 表示在该时间内检查多次直到满足条件或超时
    keep: float = 0
