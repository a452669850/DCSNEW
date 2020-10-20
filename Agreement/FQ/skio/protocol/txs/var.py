import socket
import struct
import typing

from modbus_tk.exceptions import ModbusError
from modbus_tk.modbus_tcp import TcpMaster
from modbus_tk import defines as cst

from Agreement.FQ.skio.define import IVar, T_Val, ValType, SigType
from Agreement.FQ.skio.exception import SkError
from utils.WorkModels import PointModel
from Agreement.FQ.skio.worker.state import SlotInfo


class txsMaster(TcpMaster):
    _slave: int = 1
    info: SlotInfo
    speed: str = 'low'

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
