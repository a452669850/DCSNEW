import multiprocessing as mp
from multiprocessing.connection import Connection

from Agreement.SM.skio.exception import SkError
from Agreement.SM.skio.define import CmdType, KCommand, KReply
from Agreement.SM.skio.worker.state import SkWorkerState


class SkWorkerProcess(mp.Process):
    connection: Connection

    def __init__(self, connection):
        mp.Process.__init__(self)
        self.name = 'SkWorker'
        self.daemon = True
        self.connection = connection
        self.query = mp.Queue()

    def run(self) -> None:
        state = SkWorkerState()
        while True:
            cmd: KCommand = self.query.get()
            try:
                if cmd.type == CmdType.SETUP:
                    path = cmd.body
                    state.setup(path)
                    reply = KReply(CmdType.SUCCESS)
                    self.connection.send(reply)
                elif cmd.type == CmdType.PING:
                    reply = KReply(CmdType.PING, body=state.slots)
                    self.connection.send(reply)
                elif cmd.type == CmdType.READ:
                    name = cmd.body.pop('name')
                    remote = cmd.body.get('remote', True)
                    force = cmd.body.get('force', False)
                    if force:
                        value = state.force_flag.get(name)
                    else:
                        value = state.read(name, remote=remote)
                    reply = KReply(CmdType.SUCCESS, body=value)
                    self.connection.send(reply)
                elif cmd.type == CmdType.WRITE:
                    force = cmd.body.get('force', False)
                    name = cmd.body.pop('name')
                    value = cmd.body.pop('value')
                    if force and value == '':
                        if name in state.force_flag:
                            state.force_flag.pop(name)
                    else:
                        value = state.write(name, value, remote=True)
                    if force:
                        state.force_flag[name] = value
                    reply = KReply(CmdType.SUCCESS, body=value)
                    self.connection.send(reply)
            except SkError as e:
                reply = KReply(CmdType.ERROR, body=e)
                self.connection.send(reply)
