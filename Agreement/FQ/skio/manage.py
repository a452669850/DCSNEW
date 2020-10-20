import multiprocessing as mp
import re
import typing
from multiprocessing.connection import Connection

import peewee
from pubsub import pub

from Agreement.FQ.skio.define import CmdType, KCommand, KReply, IVar
from Agreement.FQ.skio.exception import SkError
from Agreement.FQ.skio.worker.service import SkWorkerProcess
from Agreement.FQ.skio.worker.state import SlotInfo, find_variable
from utils.WorkModels import init_database, PointModel


class SkIO(object):
    connection: Connection

    def __init__(self):
        _connection, self.connection = mp.Pipe()
        self.worker = SkWorkerProcess(_connection)

    def cmd(self, cmd: KCommand) -> KReply:
        self.worker.query.put(cmd)
        replay = self.connection.recv()
        if replay.type == CmdType.ERROR:
            if isinstance(replay.body, SkError):
                raise SkError(replay.body.errno, replay.body.msg)
            raise SkError(msg=str(replay.body))
        return replay

    def setup(self, path):
        if self.worker and not self.worker.is_alive():
            self.worker.start()
        self.cmd(KCommand(CmdType.SETUP, body=path))
        database = peewee.SqliteDatabase(path.joinpath('etc', 'skio.db'))
        init_database(database)
        pub.sendMessage('SKIO.SETUP', a=path)

    def ping(self) -> typing.List[SlotInfo]:
        pong = self.cmd(KCommand(CmdType.PING))
        return pong.body

    def read(self, name, value=None, remote=True, force=False, **kwargs):
        # su 点不支持同时查询多个点，下面是check 5ESFAC/RPCxxx=xxx(CHx)
        channel_val = None
        if value:
            val_re = re.search('\(\S+(\d+)\)', str(value))
            if val_re:
                kwargs['proc_val'] = value
                # read_txs_time 获取通道
                channel_val = val_re.groups()[0]
            # 用来兼容读多个TX
            elif 'TX' in str(value).upper():
                kwargs['proc_val'] = value

        reply = self.cmd(
            KCommand(CmdType.READ, body={'name': name, 'remote': remote, 'force': force, 'kwargs': kwargs}))

        # need_time = 'need_time' in kwargs
        need_time = kwargs.pop('need_time', False)
        v = self.find(name, value)
        name = v.name
        if need_time:
            ti = self.read_txs_time(name, channel_val)
        else:
            # 时间为 -1 的时候，前端不显示
            ti = -1

        if reply.type == CmdType.SUCCESS:
            return reply.body, ti

    def write(self, name, value, force=False, **kwargs):
        val_re = re.search('(\d+(\.\d+)?)\(', str(value))
        if val_re:
            kwargs['proc_val'] = value
            # 浮点数
            if val_re.groups()[1]:
                value = float(val_re.groups()[0])
            else:
                value = int(val_re.groups()[0])
        reply = self.cmd(KCommand(CmdType.WRITE, body={'name': name, 'value': value, 'force': force, 'kwargs': kwargs}))
        need_time = 'need_time' in kwargs
        ti = 0 if need_time else -1

        if reply.type == CmdType.SUCCESS:
            return reply.body, ti

    def incr(self, name, value):
        old_value = self.read(name)
        value += old_value
        self.write(name, value)

    def is_ready(self):
        return self.worker.is_alive()

    def txsPy(self, path):
        """
        执行 TXS 初始化脚本
        :param path:
        :return:
        """
        reply = self.cmd(KCommand(CmdType.TXSPY, path))
        if reply.type == CmdType.SUCCESS:
            return True
        return False

    def read_txs_time(self, name, channel_val=None) -> float:
        """
        返回时间，不用设置通道
        :param name:
        :return:
        """
        # 如果传进来的是通道名
        print('read_txs_time', name, channel_val)
        if channel_val:
            channel_val = int(channel_val)
            pxi_freg = PointModel.filter(PointModel.sig_name == name).first()
            rpc, in_or_out = pxi_freg.uri.split(':')
            # 获得计时卡
            pxi_time: PointModel = PointModel.filter(PointModel.sig_name == f'{rpc}_{channel_val}_TIME').first()
        else:
            pxi_freg = PointModel.filter(PointModel.sig_name == name).first()
            rpc, in_or_out = pxi_freg.uri.split(':')
            if re.search(r'(\d+)', in_or_out):
                in_or_out_value = re.search(r'(\d+)', in_or_out).groups()[0]
                in_or_out_value = int(in_or_out_value)
            # channel_val = 1
            # 获得计时卡
            pxi_time: PointModel = PointModel.filter(PointModel.sig_name == f'{rpc}_{in_or_out_value}_TIME').first()

        time_reply = self.cmd(
            KCommand(CmdType.READ, body={'name': pxi_time.sig_name, 'remote': True, 'force': False}))

        if time_reply.type == CmdType.SUCCESS:
            return time_reply.body

    def find(self, name: str, value='', **kwargs) -> IVar:
        try:
            kwargs.setdefault('proc_val', f'{value}')
            return find_variable(name, **kwargs)
        except Exception:
            return None

    def clear_all_refer_time(self):
        print('>>> 清空参考信号')
        # 取到所有参考信号
        for i in range(1, 9):
            self.write(f'__SYS.REFER_{i}', 0)

        print('>>> 清空RPC和ESFAC时间')
        for i in range(1, 5):
            for j in range(1, 5):
                self.write(f'RPC{i}_{j}_TIME', '-1')

        # TODO: 需要把ESFAC时间清空
        for i in range(1, 6):
            self.write(f'ESFAC_A_{i}_TIME', '-1')
        for i in range(1, 6):
            self.write(f'ESFAC_B_{i}_TIME', '-1')
        for i in range(1, 6):
            self.write(f'ESFAC_DAS_{i}_TIME', '-1')

    # 在规程执行完清除所有通道
    def clear_all_channel(self):
        print('>>> 清空所有channel')
        for i in range(1, 5):
            for j in range(1, 3):
                self.write(f'RPC{i}_{j}_CHANNEL', 0)

        for i in range(1, 6):
            self.write(f'ESFAC_A_{i}_CHANNEL', 0)
        for i in range(1, 6):
            self.write(f'ESFAC_B_{i}_CHANNEL', 0)
