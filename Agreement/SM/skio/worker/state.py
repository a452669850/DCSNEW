import enum
import logging
import threading
import typing
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
from logging.handlers import RotatingFileHandler
from pathlib import Path

from peewee import SqliteDatabase

from Agreement.SM.skio import exception
from Agreement.SM.skio.define import LOGGER, ProtocolType, T_Val, IVar, SigType, ValType, IDev
from utils.WorkModels import init_database, NetworkConfig, PointModel
from Agreement.SM.skio.protocol.pms import SmPXIDev, SmHSLDev
from Agreement.SM.skio.worker.memory import MemCache
from Agreement.SM.skio.worker.sample import SampleThread


class SkWorkerState(object):
    """
    状态机
    """
    database: typing.Optional[SqliteDatabase]
    path: typing.Optional[Path]
    slots: typing.List['SlotInfo']
    ready: bool

    def __init__(self):
        self.lock = threading.RLock()
        self.ready = False
        self.slots = []
        self.path = None
        self.database = None
        self.mem = MemCache()
        self.sample = SampleThread(self)
        self.force_flag = {}

    def __str__(self):
        return f'{self.__class__.__name__}(ready={self.ready})'

    def setup(self, path: Path) -> 'SkWorkerState':
        """
        setup State from path
        :param path:
        :return:
        """
        # 1. Path
        for x in ('', 'etc', 'log', 'var', 'tmp'):
            p = path.joinpath(x)
            if not p.exists():
                p.mkdir(parents=True)

        self.path = path

        # 2. Logger
        hdlr = RotatingFileHandler(
            filename=path.joinpath('log', 'SkIO.log'),
            maxBytes=1024 * 1024 * 5,
            encoding='utf-8'
        )
        fmt = logging.Formatter(
            '[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d] %(message)s',
            '%y%m%d %H:%M:%S'
        )
        hdlr.setFormatter(fmt)
        hdlr.setLevel(logging.DEBUG)
        LOGGER.setLevel(logging.DEBUG)
        LOGGER.addHandler(hdlr)

        # 3. Database
        self.database = SqliteDatabase(path.joinpath('etc', 'SkIO.db'))
        init_database(self.database)

        # 4. Slot
        self.mem.setup(path)
        self.slots = list(map(register_dev, NetworkConfig.select()))
        # sample thread
        for slot in self.slots:
            self.sample.queue.put(slot)
        self.sample.start()
        self.ready = True
        return self

    def find(self, name: str, **kwargs) -> IVar:
        if not self.database:
            raise exception.SkError(exception.VAR_NOT_FOUND, name)
        return find_variable(name, **kwargs)

    def read(self, name: str, *, remote: bool = True, **kwargs) -> T_Val:
        """
        Read Variable Value
        :param name: SigName
        :param remote: read from remote device if remote else local memory
        :param kwargs:
        :return:
        """
        try:
            var = self.find(name, **kwargs)
            if not var:
                return
            if remote:
                for si in self.slots:
                    if si.slot == var.slot:
                        val = si.read(var)
                        self.mem.write(var, val)
                        return val

            return self.mem.read(var)
        except exception.SkError as e:
            LOGGER.exception(e)
            raise e

    def write(self, name, value, *, remote=True, **kwargs):
        """
        Write Variable Value
        :param name: SigName
        :param value: Value
        :param remote: write to remote device if remote else local memory
        :param kwargs:
        :return:
        """
        try:
            var = self.find(name, **kwargs)
            LOGGER.info(f'write kwargs={name}, {value}, {remote}, {kwargs}; {var}')
            if not var:
                return
            if remote:
                for si in self.slots:
                    if si.slot == var.slot:
                        value = si.write(var, value)
                        self.mem.write(var, value)
                        return value

            return self.mem.write(var, value)
        except exception.SkError as e:
            LOGGER.exception(e)
            raise e


@dataclass
class SlotInfo(object):
    class Status(enum.Enum):
        READY = 0
        OFFLINE = 1
        ERROR = 2

    id: int
    slot: str
    protocol: ProtocolType
    uri: str
    description: str
    status: Status = Status.READY

    dev: typing.Optional[IDev] = None

    def read(self, var: IVar) -> T_Val:
        return self.dev.read(var)

    def write(self, var: IVar, value: T_Val) -> T_Val:
        return self.dev.write(var, value)

    def fetch(self, state: SkWorkerState):
        try:
            if hasattr(self.dev, 'fetch'):
                self.dev.fetch()
                self.status = self.Status.READY
        except exception.SkError as e:
            if e.errno == exception.NETWORK_ERROR:
                self.status = self.Status.OFFLINE
            else:
                self.status = self.Status.ERROR


def register_dev(dev: NetworkConfig) -> 'SlotInfo':
    """
    Creat a `SlotInfo` from `DevModel`
    :param dev:
    :return:
    """
    protocol = ProtocolType[dev.protocol]

    si = SlotInfo(
        id=dev.id,
        slot=dev.slot,
        protocol=protocol,
        uri=dev.uri,
        description=dev.description,
        status=SlotInfo.Status.READY
    )

    if protocol == ProtocolType.SMPXI:
        si.dev = SmPXIDev()
    elif protocol == ProtocolType.SMHSL:
        si.dev = SmHSLDev()
    si.dev.setup(si.uri)
    return si


_alias = {
    'START_PXI1': 'TSD',
    'START_PXI2': 'TSD',
    'START_PXI3': 'TSD',
    'START_PXI4': 'TSD',
    'START_PXI5': 'TSD',
    'START_PXI6': 'TSD',

    # '52 UV A1': 'PMS-JD-RTSA01-UV',
    # '52 Shunt A1': 'PMS-JD-RTSA02-UV',
    # '52 UV A2': 'PMS-JD-RTSA01-ST',
    # '52 Shunt A2': 'PMS-JD-RTSA02-ST',

    '52 UV B1': 'PMS-JD-RTSB01-UV',
    '52 Shunt B1': 'PMS-JD-RTSB01-ST',
    '52 UV B2': 'PMS-JD-RTSB02-UV',
    '52 Shunt B2': 'PMS-JD-RTSB02-ST',

    '52 ST B1': 'PMS-JD-RTSB02-UV',
    '52 ST B2': 'PMS-JD-RTSB02-ST',

    # '52 UV C1': 'PMS-JD-RTSC01-UV',
    # '52 Shunt C1': 'PMS-JD-RTSC02-UV',
    # '52 UV C2': 'PMS-JD-RTSC01-ST',
    # '52 Shunt C2': 'PMS-JD-RTSC02-ST',
    #
    # '52 UV D1': 'PMS-JD-RTSD01-UV',
    # '52 Shunt D1': 'PMS-JD-RTSD02-UV',
    # '52 UV D2': 'PMS-JD-RTSD01-ST',
    # '52 Shunt D2': 'PMS-JD-RTSD02-ST',

    # NIS A 列
    'RXS-JE-NE001A': 'NIS_P0_F',
    'RXS-JE-NE002A': 'NIS_P1_A',
    'RXS-JE-NE002A-P': 'NIS_P1_F',
    'RXS-JE-NE003A': 'NIS_A0',
    'RXS-JE-NE004A': 'NIS_A1',

    # NIS B 列
    'RXS-JE-NE001B': 'NIS_P0_F',
    'RXS-JE-NE002B': 'NIS_P1_A',
    'RXS-JE-NE002B-P': 'NIS_P1_F',
    'RXS-JE-NE003B': 'NIS_A0',
    'RXS-JE-NE004B': 'NIS_A1',
    'RXS-JE-NE001B-A': 'NIS_P0_A'
}


@lru_cache(maxsize=1024)
def find_variable(name: str, **kwargs) -> IVar:
    """
    查找变量信息
    :param name:
    :param kwargs:
    :return:
    """
    if name.startswith('__SYS.'):
        LOGGER.info(f'SYS VAR {name}')
        tag = name.split('.')
        # 触发边沿
        if tag[1] == 'EDG':
            ch = tag[2]
            if not ch:
                return
            ch = int(ch.lstrip('T')) - 1
            iv = find_variable('EDG')
            niv = deepcopy(iv)
            niv.name = f'{iv.name}.{ch}'
            niv.length = 1
            fc, addr, size = iv.uri.split(':')
            niv.uri = f'{fc}:{int(addr)+ch}:{1}'
            return niv

    if name in _alias:
        return find_variable(_alias[name], **kwargs)
    model: PointModel = PointModel.filter(PointModel.sig_name == name).first()
    if not model:
        raise exception.SkError(exception.VAR_NOT_FOUND, name)

    # 数据类型，长度
    if '*' in model.val_type:
        val_type, length = model.val_type.split('*')
        val_type = ValType[val_type.upper()]
        length = int(length)
    else:
        val_type, length = model.val_type, 1
        val_type = ValType[val_type.upper()]

    # 信号类型
    sig_type = SigType[model.sig_type.upper()]

    iv = IVar(
        id=model.id,
        name=model.sig_name,
        sig_type=sig_type,
        val_type=val_type,
        length=length,
        uri=model.uri,
        slot=model.slot
    )

    if model.eu is not None:
        iv.eu = model.eu
    if model.rlo is not None:
        iv.rlo = float(model.rlo)
    if model.rhi is not None:
        iv.rhi = float(model.rhi)
    if model.elo is not None:
        iv.elo = float(model.elo)
    if model.ehi is not None:
        iv.ehi = float(model.ehi)
    return iv
