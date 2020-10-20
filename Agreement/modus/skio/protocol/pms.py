import socket
import struct
import typing

from modbus_tk import defines as cst
from modbus_tk.exceptions import ModbusError
from modbus_tk.modbus_tcp import TcpMaster
from pubsub import pub

from Agreement.modus.skio import exception
from Agreement.modus.skio.define import IDev, IVar, T_Val, ValType

_T_OUTPUT_VALUE = typing.Union[typing.Tuple[int], typing.List[int], int]


# 三门协议
class SmPXIDev(IDev, TcpMaster):
    _slave: int = 1

    def __init__(self):
        IDev.__init__(self)
        TcpMaster.__init__(self)

    def setup(self, uri):
        host, port = uri.split(':')
        self._host = host
        self._port = int(port)
        pub.sendMessage('SKIO.SmPXIDev.SETUP', a1=uri)

    def read(self, var: IVar) -> T_Val:
        try:
            f_code = int(str(var.reg)[0])
            address = int(str(var.reg)[1:])
        except TypeError:
            raise exception.SkError(exception.VAR_CFG_ERROR, f'{var} config error')

        if var.chr == ValType.D64:
            length = 4
            data = self._cmd(f_code=f_code, address=address, quantity_of_x=length)
            pub.sendMessage('SKIO.SmPXIDev.READ', a1=struct.unpack('<d', struct.pack('<HHHH', *data))[0])
            return struct.unpack('<d', struct.pack('<HHHH', *data))[0]
        elif var.chr == ValType.U32:
            length = 2
            data = self._cmd(f_code=f_code, address=address, quantity_of_x=length)
            pub.sendMessage('SKIO.SmPXIDev.READ', a1=struct.unpack(f'<Q', struct.pack('<HHHH', *data))[0])
            return struct.unpack(f'<Q', struct.pack(f'<HHHH', *data))[0]
        elif var.chr == ValType.BOOL:
            length = 1
            data = self._cmd(f_code=f_code, address=address, quantity_of_x=length)
            pub.sendMessage('SKIO.SmPXIDev.READ', a1=data[0])
            return data[0]
        elif var.chr == ValType.U64:
            length = 4
            data = self._cmd(f_code=f_code, address=address, quantity_of_x=length)
            pub.sendMessage('SKIO.SmPXIDev.READ', a1=struct.unpack(f'<Q', struct.pack('<HHHH', *data))[0])
            return struct.unpack(f'<Q', struct.pack(f'<HHHH', *data))[0]
        else:
            raise exception.SkError(exception.UNSUPPORTED_TYPE,
                                    f'{self.__class__.__name__} not support {var.chr}')

    def write(self, var: IVar, value: T_Val):
        try:
            if var.chr == ValType.B1:
                value = int(value)
                value = 1 if value > 0 else 0
            elif var.chr in (ValType.F32, ValType.D64):
                value = float(value)
            else:
                value = float(value)
            f_code = int(str(var.reg)[0])
            address = int(str(var.reg)[1:])

            if var.engineering_unit == 'amps':
                value = float(value)
                value = (value - var.rlo) / (var.rhi - var.rlo)
            elif var.engineering_unit == 'volts':
                value = float(value)
                value = (value - var.rlo) / (var.rhi - var.rlo)
            elif var.engineering_unit == 'OHMS':
                OHMSanalysis(value, var)
            elif var.engineering_unit == 'HZ':
                value = float(value)
        except (TypeError, ValueError):
            raise exception.SkError(exception.VAR_CFG_ERROR, f'{var} config error')

        if f_code == cst.COILS:
            value = 1 if int(value) > 0 else 0
            self._cmd(f_code=cst.WRITE_SINGLE_COIL, address=address, output_value=value)
            pub.sendMessage('SKIO.SmPXIDev.WRITE', a1=var.name, a2=value)
            return value
        elif f_code == cst.HOLDING_REGISTERS:
            if var.chr == ValType.D64:
                output_value = struct.unpack('<HHHH', struct.pack('<d', value))
            elif var.chr == ValType.U64:
                output_value = struct.unpack('<HHHH', struct.pack('<Q', value))
            elif var.chr == ValType.U32:
                output_value = struct.unpack('<HH', struct.pack('<L', value))
            else:
                raise exception.SkError(exception.UNSUPPORTED_TYPE,
                                        f'{self.__class__.__name__} not support {var.chr}')
            self._cmd(f_code=cst.WRITE_MULTIPLE_REGISTERS, address=address, output_value=output_value)
            pub.sendMessage('SKIO.SmPXIDev.WRITE', a1=var.name, a2=value)
            return value
        else:
            raise exception.SkError(exception.READ_ONLY, f'{var.name} is ReadOnly')

    def _cmd(self,
             f_code: int,
             address: int,
             quantity_of_x: int = 0,
             output_value: _T_OUTPUT_VALUE = 0,
             expected_length: int = -1
             ) -> _T_OUTPUT_VALUE:
        try:
            return self.execute(
                self._slave,
                f_code,
                address,
                quantity_of_x=quantity_of_x,
                output_value=output_value,
                expected_length=expected_length
            )
        except (socket.timeout, ConnectionRefusedError, ConnectionResetError, OSError) as e:
            raise exception.SkError(exception.NETWORK_ERROR, e)
        except ModbusError as e:
            raise exception.SkError(exception.PROTOCOL_ERROR, e.get_exception_code())


class ModBus(IDev, TcpMaster):
    _slave: int = 1

    def __init__(self):
        IDev.__init__(self)
        TcpMaster.__init__(self)

    def setup(self, uri):
        host, port = uri.split(':')
        self._host = host
        self._port = int(port)
        self.master = TcpMaster(self._host, self._port)
        # pub.sendMessage('SKIO.SmPXIDev.SETUP', 传入值=uri, 传出值='写入成功')

    def read(self, var: IVar) -> T_Val:
        try:
            f_code = int(str(var.reg)[0])
            address = int(str(var.reg)[1:])
        except TypeError:
            raise exception.SkError(exception.VAR_CFG_ERROR, f'{var} config error')

        if var.chr == ValType.D64:
            length = 4
            data = self._cmd(f_code=f_code, address=address, quantity_of_x=length)
            pub.sendMessage('SKIO.SmPXIDev.READ', 传入值=var, 传出值=struct.unpack(f'<d', struct.pack('<HHHH', *data))[0])
            return struct.unpack('<d', struct.pack('<HHHH', *data))[0]
        elif var.chr == ValType.U32:
            length = 2
            data = self._cmd(f_code=f_code, address=address, quantity_of_x=length)
            pub.sendMessage('SKIO.SmPXIDev.READ', 传入值=var, 传出值=struct.unpack(f'<Q', struct.pack('<HHHH', *data))[0])
            return struct.unpack(f'<Q', struct.pack(f'<HHHH', *data))[0]
        elif var.chr == ValType.BOOL:
            length = 1
            data = self._cmd(f_code=f_code, address=address, quantity_of_x=length)
            pub.sendMessage('SKIO.SmPXIDev.READ', 传入值=var, 传出值=data[0])
            return data[0]
        elif var.chr == ValType.U64:
            length = 4
            data = self._cmd(f_code=f_code, address=address, quantity_of_x=length)
            pub.sendMessage('SKIO.SmPXIDev.READ', 传入值=var, 传出值=struct.unpack(f'<Q', struct.pack('<HHHH', *data))[0])
            return struct.unpack(f'<Q', struct.pack(f'<HHHH', *data))[0]
        else:
            raise exception.SkError(exception.UNSUPPORTED_TYPE,
                                    f'{self.__class__.__name__} not support {var.chr}')

    def write(self, var: IVar, value: T_Val):
        try:
            if var.chr == ValType.B1:
                value = int(value)
                value = 1 if value > 0 else 0
            elif var.chr in (ValType.F32, ValType.D64):
                value = float(value)
            else:
                value = float(value)
            f_code = int(str(var.reg)[0])
            address = int(str(var.reg)[1:])

            if var.engineering_unit == 'amps':
                value = float(value)
                value = (value - var.rlo) / (var.rhi - var.rlo)
            elif var.engineering_unit == 'volts':
                value = float(value)
                value = (value - var.rlo) / (var.rhi - var.rlo)
            elif var.engineering_unit == 'OHMS':
                OHMSanalysis(value, var)
            elif var.engineering_unit == 'HZ':
                value = float(value)
        except (TypeError, ValueError):
            raise exception.SkError(exception.VAR_CFG_ERROR, f'{var} config error')

        if f_code == cst.COILS:
            value = 1 if int(value) > 0 else 0
            self._cmd(f_code=cst.WRITE_SINGLE_COIL, address=address, output_value=value)
            pub.sendMessage('SKIO.SmPXIDev.WRITE', 传入值1=var, 传入值2=value, 传出值=value)
            return value
        elif f_code == cst.HOLDING_REGISTERS:
            if var.chr == ValType.D64:
                output_value = struct.unpack('<HHHH', struct.pack('<d', value))
            elif var.chr == ValType.U64:
                output_value = struct.unpack('<HHHH', struct.pack('<Q', value))
            elif var.chr == ValType.U32:
                output_value = struct.unpack('<HH', struct.pack('<L', value))
            else:
                raise exception.SkError(exception.UNSUPPORTED_TYPE,
                                        f'{self.__class__.__name__} not support {var.chr}')
            self._cmd(f_code=cst.WRITE_MULTIPLE_REGISTERS, address=address, output_value=output_value)
            pub.sendMessage('SKIO.SmPXIDev.WRITE', 传入值=var, 传出值=value)
            return value
        else:
            raise exception.SkError(exception.READ_ONLY, f'{var.name} is ReadOnly')

    def _cmd(self,
             f_code: int,
             address: int,
             quantity_of_x: int = 0,
             output_value: _T_OUTPUT_VALUE = 0,
             expected_length: int = -1
             ) -> _T_OUTPUT_VALUE:
        try:
            return self.master.execute(
                self._slave,
                f_code,
                address,
                quantity_of_x=quantity_of_x,
                output_value=output_value,
                expected_length=expected_length
            )
        except (socket.timeout, ConnectionRefusedError, ConnectionResetError, OSError) as e:
            raise exception.SkError(exception.NETWORK_ERROR, e)
        except ModbusError as e:
            raise exception.SkError(exception.PROTOCOL_ERROR, e.get_exception_code())


def OHMSanalysis(value, var):
    value = float(value) * 0.000476
    value = (value - var.elo) / (var.ehi - var.elo)
    return value
