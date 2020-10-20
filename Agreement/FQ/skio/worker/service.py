import ftplib
import multiprocessing as mp
from multiprocessing.connection import Connection

from Agreement.FQ.skio.exception import SkError
from Agreement.FQ.skio.define import CmdType, KCommand, KReply
from Agreement.FQ.skio.worker.state import SkWorkerState


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
                    kwargs = cmd.body.pop('kwargs', {})
                    if force:
                        value = state.force_flag.get(name)
                    else:
                        value = state.read(name, remote=remote, **kwargs)
                    reply = KReply(CmdType.SUCCESS, body=value)
                    self.connection.send(reply)
                elif cmd.type == CmdType.WRITE:
                    force = cmd.body.get('force', False)
                    name = cmd.body.pop('name')
                    value = cmd.body.pop('value')
                    kwargs = cmd.body.pop('kwargs')
                    if force and value == '':
                        if name in state.force_flag:
                            state.force_flag.pop(name)
                    else:
                        value = state.write(name, value, remote=True,**kwargs)
                    if force:
                        state.force_flag[name] = value
                    reply = KReply(CmdType.SUCCESS, body=value)
                    self.connection.send(reply)
                elif cmd.type == CmdType.TXSPY:
                    state.txsPy(cmd.body)
                    self.connection.send(KReply(CmdType.SUCCESS, body=True))
            except SkError as e:
                reply = KReply(CmdType.ERROR, body=e)
                self.connection.send(reply)


def download_ftp(host, remote, local):
    """
    下载指定文件
    :param host:
    :param remote:
    :param local:
    :return:
    """
    ftp = ftplib.FTP(host)
    with open(local, 'wb') as fp:
        ftp.retrbinary(remote, callback=fp.write)
