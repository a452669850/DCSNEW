import socket
import struct
import typing

from modbus_tk import defines as cst
from modbus_tk.exceptions import ModbusError
from modbus_tk.modbus_tcp import TcpMaster

from Agreement.FQ.skio.define import IVar, T_Val, ValType, SigType
from Agreement.FQ.skio.exception import SkError
from Agreement.FQ.skio.worker.state import SlotInfo
from utils.WorkModels import PointModel


class PxiMaster(TcpMaster):
    _slave: int = 1
    info: SlotInfo
    speed: str = 'high'

    def __init__(self, info: SlotInfo) -> None:
        TcpMaster.__init__(self)
        self.info = info
        self.setup(info.uri)

    def setup(self, uri: str) -> SlotInfo:
        host, port = uri.split(':')
        self._host, self._port = host, int(port)
        return self.info

    def read(self, var: IVar) -> T_Val:
        uri = var.uri
        f_code, address, length = map(int, uri.split(':'))
        data = self._cmd(f_code=f_code, address=address, quantity_of_x=length)
        if var.val_type == ValType.D64:
            val = struct.unpack('<d', struct.pack('<HHHH', *data))[0]
            return val
        elif var.val_type == ValType.B1:
            val = data[0]
            return val
        elif var.val_type == ValType.U64:
            val = struct.unpack(f'<Q', struct.pack(f'<HHHH', *data))[0]
            return val
        else:
            raise TypeError(f'unsupported val_type {var.val_type}')

    def write(self, var: IVar, val: T_Val) -> T_Val:
        uri = var.uri
        f_code, address, length = map(int, uri.split(':'))
        if f_code == cst.COILS:
            val = 1 if val > 0 else 0
            output_value = val
            self._cmd(f_code=cst.WRITE_SINGLE_COIL, address=address, output_value=output_value)
            return val
        elif f_code == cst.HOLDING_REGISTERS:
            if var.val_type == ValType.D64:
                output_value = struct.unpack('<HHHH', struct.pack('<d', val))
            elif var.val_type == ValType.U64:
                output_value = struct.unpack('<HHHH', struct.pack('<Q', val))
            else:
                raise TypeError(f'unsupported val_type {var.val_type}')
            self._cmd(f_code=cst.WRITE_MULTIPLE_REGISTERS, address=address, output_value=output_value)
            return val
        else:
            raise SkError(f'readOnly var {var.name}')

    def _cmd(self,
             f_code: int,
             address: int,
             quantity_of_x: int = 0,
             output_value: typing.Union[typing.Tuple[int], typing.List[int], int] = 0,
             expected_length: int = -1) -> typing.Union[typing.List[int], int]:
        try:
            ret = self.execute(self._slave,
                               f_code,
                               address,
                               quantity_of_x=quantity_of_x,
                               output_value=output_value,
                               expected_length=expected_length)
            self.info.status = 1
            return ret
        except (socket.timeout, ConnectionRefusedError, ConnectionResetError) as e:
            self.info.status = -1
            raise SkError(e)
        except ModbusError as e:
            print(f_code, address, e)
            self.info.status = -2
            raise SkError(e)

    def fetch(self, worker: 'SkWorker'):
        for var in PointModel.filter(PointModel.slot == self.info.slot):
            ivar = worker.find(var.sig_name)
            val = self.read(ivar)
            if val is None:
                raise Exception(ivar)
            worker.mem.write(ivar, val)


class PxiHSL(PxiMaster):
    data = []

    def setup(self, uri: str) -> SlotInfo:
        si = super(PxiHSL, self).setup(uri)

        self.data.clear()
        for var in PointModel.filter(
                PointModel.slot == self.info.slot,
                PointModel.sig_type == SigType.HSL_BEAT.name):
            vt, length = var.val_type.split('*')
            vt, length = ValType[vt], int(length)
            beat = int(var.initial)

            data = [0] * length
            data[0] = beat
            self.data.append((var, data))

        return si

    def read(self, var: IVar) -> T_Val:
        raise SkError('no support read remote')

    def write(self, var: IVar, val: T_Val) -> T_Val:
        if var.sig_type == SigType.HSL_BEAT:
            raise SkError(f'readOnly var {var.name}')

        port, index, bit = var.uri.split(':')
        port, index, bit = int(port), int(index), int(bit)
        val = self.set(port, index, bit, flag=val)

        b_var, data = self.data[port // 2]
        _, address, _ = b_var.uri.split(':')
        address = int(address)

        output_value = struct.unpack(
            f'<{len(data) * 2}H',
            struct.pack(f'<{len(data)}I', *data)
        )
        self._cmd(f_code=cst.WRITE_MULTIPLE_REGISTERS, address=address, output_value=output_value)
        return val

    def fetch(self, worker: 'SkWorker'):
        for var, data in self.data:
            ivar = worker.find(var.sig_name)
            worker.mem.write(ivar, data[0])

    def set(self, port, index, bit, flag):
        try:
            flag = int(flag)
            flag = 1 if flag > 0 else 0
        except ValueError:
            flag = 0
        if 0 <= bit < 16:
            bit = bit + 16
        else:
            bit = bit - 16

        offset = 1 + index
        _, data = self.data[port // 2]
        byte = data[offset]
        op = 1
        assert 0 <= bit < 32
        op <<= bit
        if flag == 1:
            byte = byte | op
        if flag == 0:
            byte = byte & ~op
        data[offset] = byte
        return flag
