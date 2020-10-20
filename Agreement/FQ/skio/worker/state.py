import enum
import logging
import re
import threading
import typing
from collections import namedtuple
from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
from logging.handlers import RotatingFileHandler
from pathlib import Path

from peewee import SqliteDatabase

from Agreement.FQ.skio import exception
from Agreement.FQ.skio.define import LOGGER, ProtocolType, T_Val, IVar, SigType, ValType, \
    IDev
from Agreement.FQ.skio.exception import SkError
from utils.WorkModels import init_database, PointModel, NetworkConfig
from Agreement.FQ.skio.protocol.pms import SmPXIDev, SmHSLDev
from Agreement.FQ.skio.worker.memory import MemCache
from Agreement.FQ.skio.worker.sample import SampleThread

from Agreement.FQ.skio.protocol.txs.dev import TXS_PXI_Dev, TXS_Dev, TxsPy


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

        if not self.sample.is_alive():
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

            # return self.mem.read(var)
            return 0
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
            kwargs.setdefault('proc_val', value)
            var = self.find(name, **kwargs)
            LOGGER.info(
                f'write kwargs={name}, {value}, {remote}, {kwargs}; {var}')
            if not var:
                return

            if var.trans_value is not None:
                value = var.trans_value
            print('>>iv.trans_value', value)

            if remote:
                for si in self.slots:
                    if si.slot == var.slot:
                        value = si.write(var, value)
                        self.mem.write(var, value)
                        return value

            # return self.mem.write(var, value)
            return 0
        except exception.SkError as e:
            LOGGER.exception(e)
            raise e

    def txsPy(self, path):
        path = self.path.joinpath('var', path)
        print('>>>path ',path)
        if not path.exists():
            raise exception.SkError(msg=f'脚本不存在: {path}')

        txs = TxsPy.compile(path.read_text('utf-8'))
        txs.execute(self)
        return True


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
    elif protocol == ProtocolType.TXS:
        si.dev = TXS_Dev()
    elif protocol == ProtocolType.TXS_PXI_Dev:
        si.dev = TXS_PXI_Dev()
    si.dev.setup(si.uri)
    return si


_alias = {
    'START_PXI1': 'TSD',
    'START_PXI2': 'TSD',
    'START_PXI3': 'TSD',
    'START_PXI4': 'TSD',
    'START_PXI5': 'TSD',
    'START_PXI6': 'TSD',

    '52 UV A1': 'PMS-JD-RTSA01-UV',
    '52 Shunt A1': 'PMS-JD-RTSA02-UV',
    '52 UV A2': 'PMS-JD-RTSA01-ST',
    '52 Shunt A2': 'PMS-JD-RTSA02-ST',

    '52 UV B1': 'PMS-JD-RTSB01-UV',
    '52 Shunt B1': 'PMS-JD-RTSB02-UV',
    '52 UV B2': 'PMS-JD-RTSB01-ST',
    '52 Shunt B2': 'PMS-JD-RTSB02-ST',

    '52 UV C1': 'PMS-JD-RTSC01-UV',
    '52 Shunt C1': 'PMS-JD-RTSC02-UV',
    '52 UV C2': 'PMS-JD-RTSC01-ST',
    '52 Shunt C2': 'PMS-JD-RTSC02-ST',

    '52 UV D1': 'PMS-JD-RTSD01-UV',
    '52 Shunt D1': 'PMS-JD-RTSD02-UV',
    '52 UV D2': 'PMS-JD-RTSD01-ST',
    '52 Shunt D2': 'PMS-JD-RTSD02-ST',
}


# @lru_cache(maxsize=1024)
def find_variable(name: str, **kwargs) -> IVar:
    """
    查找变量信息
    :param name:
    :param kwargs:
    :return:
    """
    # 福清项目SYS不特殊处理
    # if name.startswith('__SYS.'):
    #     LOGGER.info(f'SYS VAR {name}')
    #     tag = name.split('.')
    #     # 触发边沿
    #     if tag[1] == 'EDG':
    #         ch = tag[2]
    #         if not ch:
    #             return
    #         ch = int(ch.lstrip('T')) - 1
    #         iv = find_variable('EDG')
    #         niv = deepcopy(iv)
    #         niv.name = f'{iv.name}.{ch}'
    #         niv.length = 1
    #         fc, addr, size = iv.uri.split(':')
    #         niv.uri = f'{fc}:{int(addr)+ch}:{1}'
    #         return niv

    # 新的执行需求
    dd = AnalysisDev(name, **kwargs)
    res = dd.parse_val()

    if res:
        return res

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


class BaseAnalysis:
    def __init__(self, name, proc_data):
        self.name = name
        self.proc_data = proc_data

    def analysis(self):
        raise NotImplementedError


class ChAnalysis(BaseAnalysis):
    NUM_PATTERN = re.compile(r"([0-9\.]+)")
    STR_PATTERN = re.compile(r"([a-zA-Z\%]+)")

    def __init__(self, name, proc_data):
        super().__init__(name, proc_data)

    def analysis(self):
        # 带ma的
        if 'ma' in self.proc_data.lower():
            res = self.NUM_PATTERN.search(self.proc_data)
            if res:
                val = res.groups()[0]

                # 他们是A为单位
                return float(val) / 1000
            return None
        else:
            sdt = self.STR_PATTERN.search(self.proc_data)
            # 带任何字符和%的
            if sdt:
                num_sdt = self.NUM_PATTERN.search(self.proc_data)
                if num_sdt:
                    num = float(num_sdt.groups()[0])
                    return self.transform_ma(num)
                else:
                    raise SkError('22', '无法找到num值')
            # 纯数字的
            else:
                return self.transform_ma(self.proc_data)

    def read_db(self):
        res = PointModel.filter(PointModel.sig_name == self.name)

        if len(res) == 0:
            raise ValueError('未找到signame数据')
        elif len(res) > 1:
            raise ValueError('找到多条signame数据')
        else:
            data = res.first()
            return data

    def transform_ma(self, x3):
        sig_data = self.read_db()
        y3 = ChAnalysis.transform(sig_data, x3)

        return y3

    @staticmethod
    def linear_two_unknown(x1, y1, x2, y2, x3):
        """
        y = ax+b
        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :param x3:
        :return:
        """
        if (not all((x2, y1, y2))) or (x1 is None):
            return x3

        a = float((y1 - y2) / (x1 - x2))
        b = float(y1 - (a * x1))
        x3 = float(x3)

        y3 = a * x3 + b
        # 他们单位 A 我们输入的是ma
        return y3 / 1000

    @staticmethod
    def times_two_unknown(x1, y1, x2, y2, x3):
        """
        y = ax^2 + b
        :param x1:
        :param y1:
        :param x2:
        :param y2:
        :param x3:
        :return:
        """
        if (not all((x2, y1, y2))) or (x1 is None):
            return x3

        a = float((y1 - y2) / ((x1 * x1) - (x2 * x2)))
        b = float(y1 - (a * x1 * x1))
        x3 = float(x3)

        y3 = a * x3 * x3 + b
        # 他们单位 A 我们输入的是ma
        return y3 / 1000

    @staticmethod
    def transform(varObj, x3: str) -> float:
        if varObj.initial == 1:
            y3 = ChAnalysis.times_two_unknown(
                varObj.rlo, varObj.elo,
                varObj.rhi, varObj.ehi,
                x3
            )
        else:
            y3 = ChAnalysis.linear_two_unknown(
                varObj.rlo, varObj.elo,
                varObj.rhi, varObj.ehi,
                x3
            )

        return y3


class TxAnalysis(BaseAnalysis):
    TX_DATA = namedtuple('TX_DATA', (
        'signame_first',
        'signame_second',
        'signame_third',
    ))

    def __init__(self, name, proc_data):
        super().__init__(name, proc_data)

    def read_tx_data(self):
        res = self.name.split('.')
        if len(res) == 3:
            tx_data = self.TX_DATA(
                signame_first=res[0],
                signame_second=res[1],
                signame_third=res[2]
            )
        elif len(res) == 1:
            tx_data = self.TX_DATA(
                signame_first=res[0],
                signame_second=None,
                signame_third=None
            )
        else:
            second_data = res[1]
            if second_data.lower() in ('m1', 'm2'):
                tx_data = self.TX_DATA(
                    signame_first=res[0],
                    signame_second=None,
                    signame_third=second_data
                )
            else:
                tx_data = self.TX_DATA(
                    signame_first=res[0],
                    signame_second=second_data,
                    signame_third=None
                )

        return tx_data

    def analysis(self):
        self.tx_data = self.read_tx_data()
        data = self.parse_data(self.tx_data)
        return data

    def parse_data(self, tx_data):
        """
        #todo 对tx_data进行query搜索，根据第一个，第二个和第三个值做对应的搜索
        :param tx_data:
        :return:
        """

        tx_keyword = tx_data.signame_first
        if tx_data.signame_second:
            tx_keyword += '.' + tx_data.signame_second

        res = None
        if tx_data.signame_third:
            if tx_data.signame_third == 'M1':
                res = PointModel.filter((PointModel.sig_name.contains(tx_keyword)) & (VarModel.channel == 'M1'))
            elif tx_data.signame_third == 'M2':
                res = PointModel.filter(PointModel.sig_name.contains(tx_keyword))
        else:
            res = PointModel.filter(PointModel.sig_name.contains(tx_keyword))

        return res

    def data_to_ivar(self):
        res = self.parse_data(self.read_tx_data())
        self.ivar_list = []
        for dt in res:

            # 数据类型，长度
            if '*' in dt.val_type:
                val_type, length = dt.val_type.split('*')
                val_type = ValType[val_type.upper()]
                length = int(length)
            else:
                val_type, length = dt.val_type, 1
                val_type = ValType[val_type.upper()]

            # 信号类型
            sig_type = SigType[dt.sig_type.upper()]

            iv = IVar(
                id=dt.id,
                name=dt.sig_name,
                sig_type=sig_type,
                val_type=val_type,
                length=1,
                uri=dt.uri,
                slot=dt.slot,
                channel=dt.channel
            )

            if dt.eu is not None:
                iv.eu = dt.eu
            if dt.rlo is not None:
                iv.rlo = float(dt.rlo)
            if dt.rhi is not None:
                iv.rhi = float(dt.rhi)
            if dt.elo is not None:
                iv.elo = float(dt.elo)
            if dt.ehi is not None:
                iv.ehi = float(dt.ehi)

            self.ivar_list.append(iv)

        return self.ivar_list


class AnalysisDev:
    """
    ad1 = AnalysisDev('XRPB201SM1.M2', proc_val='1(TX)', trigger=1)
    ad1.parse_val()
    """
    VAL_PATTERN = re.compile(r"([a-zA-Z0-9\-\.\%\/]+)\(([a-zA-Z0-9\-]+)\)")
    TX_PATTENR = re.compile(r"([0-9\.\-]+)")

    def __init__(self, name, **kwargs):
        self.name = name
        self.proc_val = kwargs.get('proc_val')
        self.trigger = kwargs.get('trigger')
        self.need_time = kwargs.get('need_time')

        # txs_port 调用port接口
        self.txs_port = kwargs.get('txs_port')
        # print(self.txs_port)

    MAGIC_NUMBER = 5

    def parse_val(self) -> (IVar, float):
        if not self.proc_val:
            return None
        res = self.VAL_PATTERN.search(self.proc_val)
        if not res:
            return
        proc_data, proc_type = res.groups()

        if 'ch' in proc_type.lower():
            # print('++++ channel', self.name)
            if self.name[0].upper() == 'X':
                self.name = f'{self.MAGIC_NUMBER}{self.name[1:]}'
            ana = ChAnalysis(self.name, proc_data)
            res = ana.read_db()
            self.value = ana.analysis()

            ch = proc_type[2:]
        elif 'tx' in proc_type.lower():
            ana = TxAnalysis(self.name, proc_data)
            # res = ana.analysis()
            res = ana.data_to_ivar()

            # tx的value读取整数
            gps = self.TX_PATTENR.search(self.proc_val)
            if not gps:
                raise SkError(22, '无法匹配到数值')
            else:
                self.value = float(gps.groups()[0])
        else:
            self.value = None
            return

        if isinstance(res, PointModel):
            iv = IVar(
                id=res.id,
                name=res.sig_name,
                sig_type=res.sig_type,
                val_type=res.val_type,
                length=1,
                uri=res.uri,
                slot=res.slot
            )

            if res.eu is not None:
                iv.eu = res.eu
            if res.rlo is not None:
                iv.rlo = float(res.rlo)
            if res.rhi is not None:
                iv.rhi = float(res.rhi)
            if res.elo is not None:
                iv.elo = float(res.elo)
            if res.ehi is not None:
                iv.ehi = float(res.ehi)

            iv.trigger = self.trigger
            iv.channel = ch

            if self.txs_port:
                iv.txs_port = self.txs_port
        else:
            print(res)
            iv = IVar(
                id=res[0].id,
                name=self.name,
                sig_type=SigType.TXS,
                length=1,
                slot=res[0].slot,
                val_type=ValType.D64
            )
            iv.trigger = self.trigger
            iv.group = res
            print(iv.group)

        iv.trans_value = self.value

        if self.need_time:
            iv.need_time = self.need_time

        if self.txs_port:
            iv.txs_port = self.txs_port

        return iv
