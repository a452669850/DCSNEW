import time

from peewee import SqliteDatabase

from RealtimeDB.model import init_database
from RealtimeDB.sharedMemory import MemCache
from RealtimeDB.worker.state import find_variable
from historyinfluxDB.historyDB import add_to_history


class IOMapping:
    name = None
    mem = MemCache()

    def __init__(self, path):
        self.database = SqliteDatabase(path.joinpath('etc', 'SkIO.db'))
        init_database(self.database)
        self.mem.setup(path)

    @classmethod
    def read(cls, name):
        var = find_variable(name)
        return var

    @classmethod
    def set_Current(cls, name, text):
        from RealtimeDB import skio
        value = skio.read(name, remote=False)
        if value == None:
            if name == '':
                return
            cls.mem.write(cls.read(name), 0)
            add_to_history(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), name, 0, time.time(),
                            text)
        else:
            if name == '':
                return
            cls.mem.write(cls.read(name), value)
            add_to_history(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())), name, value, time.time(),
                            text)