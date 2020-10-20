import mmap
import os
import struct
import threading
import typing
from dataclasses import dataclass
from pathlib import Path

from Agreement.SM.skio.define import ValType, IVar, T_Val
from utils.WorkModels import NetworkConfig, PointModel


@dataclass
class BlockInfo(object):
    index: int
    offset: int
    bit: int
    var_type: ValType
    length: int


class MemCache(object):
    index: typing.Dict[int, BlockInfo]
    path: typing.Optional[Path]
    mmap: typing.Optional[mmap.mmap]
    # 设计容量 20w 个 D64 点，
    # 16m, 20w * D64 = 200k*8 = 1.6m
    MAX_SIZE = 1024 * 1024 * 16

    def __init__(self):
        self.path = None
        self.mmap = None
        self.index = {}
        self.lock = threading.RLock()

    def setup(self, path: Path) -> None:
        with self.lock:
            self.path = path
            self.__create_mmap()
            self.__create_index()

    def __create_mmap(self):
        fd = os.open(
            self.path.joinpath('var', 'memory.dat').as_posix(),
            flags=os.O_CREAT | os.O_RDWR
        )
        os.write(fd, b'\0' * self.MAX_SIZE)
        self.mmap = mmap.mmap(
            fileno=fd,
            length=self.MAX_SIZE,
            access=mmap.ACCESS_WRITE | mmap.ACCESS_READ
        )

    def __create_index(self):
        dev_list = NetworkConfig.select().order_by(NetworkConfig.id)
        self.index.clear()
        block = [0, 0, 0]
        for dev in dev_list:
            var_list = PointModel.filter(PointModel.slot == dev.slot)
            for var in var_list:
                self.__register(block, var)
            block[0] += 1
            block[1] = 0
            block[2] = 0

        self.__dump_index()
        self.__load_index()

    def __register(self, block, var):
        idx, off, bit = block
        vt = var.val_type
        if '*' in vt:
            vt, length = vt.split('*')
            vt, length = ValType[vt], int(length)
        else:
            vt, length = ValType[vt], 1

        self.index[var.id] = BlockInfo(idx, off, bit, vt, length)

        if vt == ValType.B1:
            bit += length
            _off, bit = divmod(bit, 8)
            off += _off
            _idx, off = divmod(off, 1000)
            idx += _idx
        elif vt in (ValType.U8, ValType.I8):
            bit = 0
            off += 1 * length
            _idx, off = divmod(off, 1000)
            idx += _idx
        elif vt in (ValType.U16, ValType.I16):
            bit = 0
            off += 2 * length
            _idx, off = divmod(off, 1000)
            idx += _idx
        elif vt in (ValType.U32, ValType.I32, ValType.F32):
            bit = 0
            off += 4 * length
            _idx, off = divmod(off, 1000)
            idx += _idx
        elif vt in (ValType.U64, ValType.I64, ValType.D64):
            bit = 0
            off += 8 * length
            _idx, off = divmod(off, 1000)
            idx += _idx

        block[:] = [idx, off, bit]

    __idx_fmt = struct.Struct('<HHHHHH')

    def __dump_index(self):
        with self.path.joinpath('etc', 'index.dat').open('wb') as fp:
            for pk, bi in self.index.items():
                fp.write(self.__idx_fmt.pack(pk, bi.index, bi.offset, bi.bit, bi.var_type.value, bi.length))

    def __load_index(self):
        self.index.clear()
        path = self.path.joinpath('etc', 'index.dat')
        with path.open('rb') as fp:
            for pk, idx, off, bit, vt, length in self.__idx_fmt.iter_unpack(fp.read()):
                self.index[pk] = BlockInfo(idx, off, bit, ValType(vt), length)

    __block_size = 1024

    def read(self, var: IVar) -> T_Val:
        print(self.index)
        block_info = self.index[var.id]
        off = block_info.index * self.__block_size + block_info.offset
        if block_info.var_type == ValType.U8:
            return struct.unpack_from('<B', self.mmap, off)[0]
        elif block_info.var_type == ValType.I8:
            return struct.unpack_from('<b', self.mmap, off)[0]
        elif block_info.var_type == ValType.U16:
            return struct.unpack_from('<H', self.mmap, off)[0]
        elif block_info.var_type == ValType.I16:
            return struct.unpack_from('<h', self.mmap, off)[0]
        elif block_info.var_type == ValType.U32:
            return struct.unpack_from('<I', self.mmap, off)[0]
        elif block_info.var_type == ValType.I32:
            return struct.unpack_from('<i', self.mmap, off)[0]
        elif block_info.var_type == ValType.U64:
            return struct.unpack_from('<Q', self.mmap, off)[0]
        elif block_info.var_type == ValType.I64:
            return struct.unpack_from('<q', self.mmap, off)[0]
        elif block_info.var_type == ValType.F32:
            return struct.unpack_from('<f', self.mmap, off)[0]
        elif block_info.var_type == ValType.D64:
            return struct.unpack_from('<d', self.mmap, off)[0]
        elif block_info.var_type == ValType.B1:
            byte = struct.unpack_from('<B', self.mmap, off)[0]
            op = 1 << block_info.bit
            return 1 if byte & op == op else 0
        else:
            raise TypeError(block_info)

    def write(self, var: IVar, val: T_Val) -> T_Val:
        bi = self.index[var.id]
        off = bi.index * self.__block_size + bi.offset
        with self.lock:
            if bi.var_type == ValType.U8:
                struct.pack_into('<B', self.mmap, off, val)
            elif bi.var_type == ValType.I8:
                struct.pack_into('<b', self.mmap, off, val)
            elif bi.var_type == ValType.U16:
                struct.pack_into('<H', self.mmap, off, val)
            elif bi.var_type == ValType.I16:
                struct.pack_into('<h', self.mmap, off, val)
            elif bi.var_type == ValType.U32:
                struct.pack_into('<I', self.mmap, off, val)
            elif bi.var_type == ValType.I32:
                struct.pack_into('<i', self.mmap, off, val)
            elif bi.var_type == ValType.U64:
                struct.pack_into('<Q', self.mmap, off, val)
            elif bi.var_type == ValType.I64:
                struct.pack_into('<q', self.mmap, off, val)
            elif bi.var_type == ValType.F32:
                struct.pack_into('<f', self.mmap, off, val)
            elif bi.var_type == ValType.D64:
                struct.pack_into('<d', self.mmap, off, val)
            elif bi.var_type == ValType.B1:
                byte = struct.unpack_from('<B', self.mmap, off)[0]
                op = 1 << bi.bit
                if val > 0:
                    byte = byte | op
                else:
                    byte = byte & ~op
                struct.pack_into('<B', self.mmap, off, byte)
            else:
                raise TypeError(bi)
        return val

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.mmap.close()
