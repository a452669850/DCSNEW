import enum
import logging
import typing
from dataclasses import dataclass
# from skio.worker.state import SlotInfo
from typing import Any


class ProtocolType(enum.Enum):
    # beijing & 301
    RCV = 5
    # SMNPC
    SMPXI = 10
    SMHSL = 11
    modbus = 12
    # TXS
    TXS = 12
    TXS_PXI_Dev = 13


class SigType(enum.Enum):
    ALIAS = 1

    STO = 10
    SAI, SAO = 11, 12
    SDI, SDO = 13, 14
    DPO = 15
    SCTR = 16

    HSL_BEAT = 17
    HSLO = 18
    NIS_F, NIS_A = 19, 20

    AI, AO, AIO = 1, 2, 3
    DI, DO, DIO = 4, 5, 6

    SHSL = 7

    TXS, FREG = 21, 22
    FAI, FAO, FDI, FDO = 23, 24, 25, 26
    FAV, FPT100 = 27, 28


class ValType(enum.Enum):
    B1 = 0
    U8, U16, U32, U64 = 1, 2, 3, 4
    I8, I16, I32, I64 = 5, 6, 7, 8
    F32, D64 = 9, 10
    BOOL = 11
    s32 = 12


@dataclass
class BlockInfo(object):
    idx: int
    off: int
    bit: int
    vt: ValType
    length: int


@dataclass
class FVar(object):
    id: int
    name: str
    sig_type: SigType
    val_type: ValType
    length: int = 1
    uri: str = ''
    slot: str = ''
    si: typing.Optional['SlotInfo'] = None
    eu: str = None
    rlo: float = None
    rhi: float = None
    elo: float = None
    ehi: float = None

    channel: int = 1
    trigger: bool = False
    group: list = None
    trans_value: typing.Union[str, int, bool, float] = None

    # 是否使用福清port回读，当硬件置值过来的时候使用
    txs_port: bool = False


@dataclass
class IVar(object):
    id: int
    name: str
    sig_type: SigType
    chr: ValType
    reg: int
    length: int = 1
    slot: str = ''
    si: typing.Optional['SlotInfo'] = None
    engineering_unit: str = None
    rlo: float = None
    rhi: float = None
    elo: float = None
    ehi: float = None


T_Val = typing.Union[float, int, bool]
LOGGER = logging.getLogger('SkIO')


class IDev(object):
    def setup(self, uri):
        raise NotImplementedError

    def read(self, var: IVar) -> T_Val:
        raise NotImplementedError

    def write(self, var: IVar, value: T_Val) -> T_Val:
        raise NotImplementedError


class CmdType(enum.Enum):
    SETUP = 0
    PING, PONG = 1, 2
    READ, WRITE = 3, 4
    FQREAD, FQWRITE = 6, 7

    # 执行 txs 脚本
    TXSPY = 5

    SUCCESS, ERROR = 10, 11


@dataclass
class KCommand(object):
    type: CmdType
    body: Any = None


@dataclass
class KReply(object):
    type: CmdType
    body: Any = None
