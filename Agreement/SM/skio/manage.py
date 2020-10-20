import multiprocessing as mp
import typing
from multiprocessing.connection import Connection

import peewee
from pubsub import pub

from Agreement.SM.skio.define import CmdType, KCommand, KReply, LOGGER
from Agreement.SM.skio.exception import SkError
from utils.WorkModels import init_database
from Agreement.SM.skio.worker.service import SkWorkerProcess
from Agreement.SM.skio.worker.state import SlotInfo


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
            raise SkError(replay.body)
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

    def read(self, name, remote=True, force=False):
        reply = self.cmd(KCommand(CmdType.READ, body={'name': name, 'remote': remote, 'force': force}))
        if reply.type == CmdType.SUCCESS:
            return reply.body

    def write(self, name, value, force=False):
        reply = self.cmd(KCommand(CmdType.WRITE, body={'name': name, 'value': value, 'force': force}))
        if reply.type == CmdType.SUCCESS:
            return reply.body

    def incr(self, name, value):
        old_value = self.read(name)
        value += old_value
        self.write(name, value)

    def is_ready(self):
        return self.worker.is_alive()
