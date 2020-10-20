import socket
import struct
import typing

from modbus_tk import defines as cst
from modbus_tk.exceptions import ModbusError
from modbus_tk.modbus_tcp import TcpMaster

from Agreement.SM.skio import exception
from Agreement.SM.skio.define import IDev, IVar, T_Val, ValType, SigType
from utils.WorkModels import PointModel

_T_OUTPUT_VALUE = typing.Union[typing.Tuple[int], typing.List[int], int]


class SmPXIDev(IDev, TcpMaster):
    _slave: int = 1

    def __init__(self):
        IDev.__init__(self)
        TcpMaster.__init__(self)

    def setup(self, uri):
        host, port = uri.split(':')
        self._host = host
        self._port = int(port)

    def write(self, var: IVar, value: T_Val) -> T_Val:
        try:
            if var.val_type == ValType.B1:
                value = int(value)
                value = 1 if value > 0 else 0
            elif var.val_type in (ValType.F32, ValType.D64):
                value = float(value)
            else:
                value = int(value)

            # TODO: 应用在三门 PMS 项目
            #  * 电流给百分比,
            #  * 电压给百分比,
            #  * 电阻输出 U=IR=0.000476*R 转换为百分比,
            #  * 频率输出 HZ
            f_code, address, length = map(int, var.uri.split(':'))
            if var.eu == 'amps':
                value = float(value)
                value = (value - var.rlo) / (var.rhi - var.rlo)
            elif var.eu == 'volts':
                value = float(value)
                value = (value - var.rlo) / (var.rhi - var.rlo)
            elif var.eu == 'OHMS':
                value = float(value) * 0.000476  # TODO: A magic number
                value = (value - var.elo) / (var.ehi - var.elo)
            elif var.eu == 'HZ':
                value = float(value)
        except (TypeError, ValueError):
            raise exception.SkError(exception.VAR_CFG_ERROR, f'{var} config error')

        if f_code == cst.COILS:
            value = 1 if int(value) > 0 else 0
            self._cmd(f_code=cst.WRITE_SINGLE_COIL, address=address, output_value=value)
            return value
        elif f_code == cst.HOLDING_REGISTERS:
            if var.val_type == ValType.D64:
                output_value = struct.unpack('<HHHH', struct.pack('<d', value))
            elif var.val_type == ValType.U64:
                output_value = struct.unpack('<HHHH', struct.pack('<Q', value))
            elif var.val_type == ValType.U32:
                output_value = struct.unpack('<HH', struct.pack('<L', value))
            else:
                raise exception.SkError(exception.UNSUPPORTED_TYPE,
                                        f'{self.__class__.__name__} not support {var.val_type}')
            self._cmd(f_code=cst.WRITE_MULTIPLE_REGISTERS, address=address, output_value=output_value)
            return value
        else:
            raise exception.SkError(exception.READ_ONLY, f'{var.name} is ReadOnly')

    def read(self, var: IVar) -> T_Val:
        try:
            f_code, address, length = map(int, var.uri.split(':'))
        except TypeError:
            raise exception.SkError(exception.VAR_CFG_ERROR, f'{var} config error')

        data = self._cmd(f_code=f_code, address=address, quantity_of_x=length)
        if var.val_type == ValType.D64:
            return struct.unpack('<d', struct.pack('<HHHH', *data))[0]
        elif var.val_type == ValType.B1:
            return data[0]
        elif var.val_type == ValType.U64:
            return struct.unpack(f'<Q', struct.pack(f'<HHHH', *data))[0]
        else:
            raise exception.SkError(exception.UNSUPPORTED_TYPE,
                                    f'{self.__class__.__name__} not support {var.val_type}')

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


class SmHSLDev(SmPXIDev):
    data = []

    def setup(self, uri):
        super(SmHSLDev, self).setup(uri)

        self.data.clear()
        for model in PointModel.filter(PointModel.sig_type == SigType.HSL_BEAT.name):
            vt, length = model.val_type.split('*')
            vt, length = ValType[vt], int(length)
            beat = int(model.initial)

            data = [0] * length
            data[0] = beat
            self.data.append((model, data))

    def write(self, var: IVar, value: T_Val) -> T_Val:
        if var.sig_type == SigType.HSL_BEAT:
            for model, data in self.data:
                if model.sig_name == var.name:
                    value = super(SmHSLDev, self).write(var, value)
                    data[0] = value
                    return value
        elif var.sig_type == SigType.HSLO:
            try:
                port, index, bit = var.uri.split(':')
                port, index, bit = int(port), int(index), int(bit)
            except TypeError:
                raise exception.SkError(exception.VAR_CFG_ERROR, f'{var} config error')

            value = self.__set(port, index, bit, flag=value)
            self.__push(port)
            return value
        else:
            raise exception.SkError(exception.UNSUPPORTED_TYPE,
                                    f'{self.__class__.__name__} not support {var.val_type}')

    def read(self, var: IVar) -> T_Val:
        raise exception.SkError(exception.UNSUPPORTED_TYPE,
                                f'{self.__class__.__name__} not support {var.val_type}')

    def __set(self, port, index, bit, flag):
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

    def __push(self, port):
        var, data = self.data[port // 2]
        _, address, _ = var.uri.split(':')
        address = int(address)

        output_value = struct.unpack(
            f'<{len(data) * 2}H',
            struct.pack(f'<{len(data)}I', *data)
        )
        self._cmd(f_code=cst.WRITE_MULTIPLE_REGISTERS, address=address, output_value=output_value)
