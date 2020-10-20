import multiprocessing as mp
import typing
from multiprocessing.connection import Connection

import peewee
from pubsub import pub

from Agreement.modus.skio.define import CmdType, KCommand, KReply, LOGGER
from Agreement.modus.skio.exception import SkError
from Agreement.modus.skio.worker.service import SkWorkerProcess
from Agreement.modus.skio.worker.state import SlotInfo
from utils.WorkModels import init_database


class SkIO(object):
    connection: Connection

    def __init__(self):
        _connection, self.connection = mp.Pipe()
        self.worker = SkWorkerProcess(_connection)

    def start(self):
        LOGGER.info('START sample loop')

    def stop(self):
        LOGGER.info('STOP sample loop')

    def cmd(self, cmd: KCommand) -> KReply:
        self.worker.query.put(cmd)
        replay = self.connection.recv()
        if replay.type == CmdType.ERROR:
            if isinstance(replay.body, SkError):
                raise SkError(replay.body.errno, replay.body.msg)
            raise SkError(msg=str(replay.body))
        pub.sendMessage('SKIO.CMD', 传入值=cmd, 传出值=replay)
        return replay

    def setup(self, path):
        if self.worker and not self.worker.is_alive():
            self.worker.start()
        self.cmd(KCommand(CmdType.SETUP, body=path))
        database = peewee.SqliteDatabase(path.joinpath('etc', 'skio.db'))
        init_database(database)
        pub.sendMessage('SKIO.SETUP', 传入值=path)

    def ping(self) -> typing.List[SlotInfo]:
        pong = self.cmd(KCommand(CmdType.PING))
        pub.sendMessage('SKIO.PING', 传出值=pong)
        return pong.body

    def read(self, name, remote=True, force=False):
        reply = self.cmd(KCommand(CmdType.READ, body={'name': name, 'remote': remote, 'force': force}))
        if reply.type == CmdType.SUCCESS:
            pub.sendMessage('SKIO.READ', 传入值1=name, 传入值2=remote, 传入值3=force, 传出值=reply.body)
            return reply.body

    def write(self, name, value, force=False):
        reply = self.cmd(KCommand(CmdType.WRITE, body={'name': name, 'value': value, 'force': force}))
        if reply.type == CmdType.SUCCESS:
            pub.sendMessage('SKIO.WRITE', 传入值1=name, 传入值2=value, 传入值3=force, 传出值=reply.body)
            return reply.body

    def incr(self, name, value):
        old_value = self.read(name)
        value += old_value
        self.write(name, value)

    def is_ready(self):
        return self.worker.is_alive()

    def close(self):
        self.worker.terminate()
