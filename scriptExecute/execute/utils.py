import enum
import logging
import typing
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger('DxRun')
logging.basicConfig(level=logging.DEBUG)


class RunMode(enum.Enum):
    """执行模式"""
    # 自动
    AUTO = 1
    # 单步
    STEP = 2
    # 循环
    LOOP = 3


class RunState(enum.Enum):
    """执行状态"""
    # 空闲
    IDLE = 1
    # 运行
    RUNNING = 2
    # 暂停
    PAUSE = 3


@dataclass
class RunResultRecord(object):
    lineNo: int
    sat: bool
    message: str
    time: float
    value: float

    children: typing.List['RunResultRecord'] = field(default_factory=list)

    def isSat(self):
        if self.children:
            self.sat = all(x.isSat() for x in self.children)
        return self.sat

    def display(self) -> str:
        if self.message: return self.message
        return '\n'.join(x.display() for x in self.children)

    def datetime(self) -> str:
        dt = datetime.fromtimestamp(self.time)
        return dt.isoformat()
