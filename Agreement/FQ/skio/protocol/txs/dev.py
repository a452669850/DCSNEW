import ast
import socket
import struct
import time
import typing

from modbus_tk import defines as cst
from modbus_tk.exceptions import ModbusError
from modbus_tk.modbus_tcp import TcpMaster

import socket
import json
from Agreement.FQ.skio import exception
from Agreement.FQ.skio.define import IDev, IVar, T_Val, ValType, SigType, LOGGER

from Agreement.FQ.skio.define import IDev, IVar, T_Val, ValType, SigType
from utils.WorkModels import PointModel
import time

import re

_T_OUTPUT_VALUE = typing.Union[typing.Tuple[int], typing.List[int], int]
Type_Dic = {
    SigType.FAI: 1,
    SigType.FAV: 2,
    SigType.FDO: 3,
    SigType.FPT100: 4,
    SigType.FAO: 1,
    SigType.FDI: 3,

}

# 他们给定的 rpc1_1:5 rpc2_1:6 rpc3_1:7 rpc4_1:8 rpc1_2:1 rpc2_2:2 rpc3_2:3 rpc4_2:4
refer_dic = {
    'RPC1_1': 5,
    'RPC2_1': 6,
    'RPC3_1': 7,
    'RPC4_1': 8,
    'RPC1_2': 1,
    'RPC2_2': 2,
    'RPC3_2': 3,
    'RPC4_2': 4
}


class TXS_PXI_Dev(IDev, TcpMaster):
    '''
    设备表，主要有两种类型：
        1.modbus协议，用于和下位机对接
        2.socket协议，用于和linux server对接
    '''
    _slave: int = 1

    def __init__(self):
        IDev.__init__(self)
        TcpMaster.__init__(self)

    def setup(self, uri):
        host, port = uri.split(':')
        self._host = host
        self._port = int(port)

    def write(self, var: IVar, value: T_Val) -> T_Val:
        if var.trans_value:
            value = var.trans_value

        # TODO:应用在福清txs_pxi通信
        if isinstance(var.sig_type, str):
            var.sig_type = SigType[var.sig_type.upper()]

        if var.sig_type in (SigType.FAI, SigType.FAO, SigType.FDI, SigType.FDO, SigType.FAV, SigType.FPT100):
            channel = str(var.channel)
            rpc, in_or_out = var.uri.split(':')
            if re.search(r'(\d+)', in_or_out):
                in_or_out_value = re.search(r'(\d+)', in_or_out).groups()[0]
            else:
                raise exception.SkError(exception.UNSUPPORTED_TYPE,
                                        f'{var.name} uri中没有(IN|OUT)的值 ')
            if 'RPC' in rpc.upper():
                if var.sig_type == SigType.FAI:
                    self.clear_channel_ai(f'{rpc}_{channel}_CHANNEL')

                var_start: PointModel = PointModel.get(PointModel.sig_name == f'{rpc}_{channel}_START_VALUE')
                var_channel: PointModel = PointModel.get(PointModel.sig_name == f'{rpc}_{channel}_CHANNEL')
                var_type: PointModel = PointModel.get(PointModel.sig_name == f'{rpc}_{channel}_TYPE')
                var_trigger: PointModel = PointModel.get(PointModel.sig_name == f'{rpc}_{channel}_TRIGGER')

                print('+++ tigger: ', var.trigger)

                # TODO: 切通道逻辑 ,by csq
                # 一个硬件保护功能，避免中间状态， type channel :1 2 -> 0 0 -> 2 5 避免 1 2 -> 2 3
                var_type_oldvalue = self._read(var_type)
                var_channel_oldvalue = self._read(var_channel)
                if var_type_oldvalue != Type_Dic[
                    var.sig_type] and var_channel_oldvalue != in_or_out_value and var_type_oldvalue != 0 and var_channel_oldvalue != 0:
                    self._write(var_channel.uri, 0, var_channel.val_type)
                    self._write(var_type.uri, 0, var_type.val_type)
                    time.sleep(1)

                # 跳变的时候只给跳变值
                # TODO：如果在设置跳变值之前切了通道，此时channel为0，硬件不会输出。
                if var.trigger:
                    self._write(var_trigger.uri, value, var_trigger.val_type)
                    # 除了置跳变，还需要把参考信号置为相应的值
                    sys_refer: PointModel = PointModel.get(PointModel.sig_name == f'__SYS.REFER_{var.trigger}')
                    # 得到是RPC(x) 从上面的字典里面取
                    # rpc_x = refer_list[(int(rpc[3:])) + 2 ** (int(channel) - 1) - 2]
                    rpc_x = refer_dic[f'{rpc}_{channel}']

                    self._write(sys_refer.uri, rpc_x, sys_refer.val_type)
                # 否则就给起始值
                else:
                    print('起始值： ', value)
                    # 先给类型再给通道比较好
                    self._write(var_type.uri, Type_Dic[var.sig_type], var_type.val_type)
                    self._write(var_channel.uri, in_or_out_value, var_channel.val_type)
                    self._write(var_start.uri, value, var_start.val_type)

                    # TODO：由于他会在发start信号之后把所有跳变都发出去，所以我们在初始的时候把所有跳变值都设置为起始值
                    self._write(var_trigger.uri, value, var_trigger.val_type)

            elif 'ESFAC' in rpc.upper():
                # TODO: 如果在其他通道被占用的情况下，需要先把该通道切到0，再切指定通道
                for i in range(1, 6):
                    check_channel: PointModel = PointModel.get(PointModel.sig_name == f'{rpc}_{i}_CHANNEL')
                    v = self._read(check_channel)
                    # print('>>>v,channel,i:', v, channel,i)
                    if v == int(in_or_out_value) and int(channel) != i:
                        self._write(check_channel.uri, 0, check_channel.val_type)

                var_channel: PointModel = PointModel.get(PointModel.sig_name == f'{rpc}_{channel}_CHANNEL')
                self._write(var_channel.uri, in_or_out_value, var_channel.val_type)
        elif var.sig_type == SigType.FREG:
            return self._write(var.uri, value, var.val_type)
        else:
            raise exception.SkError(exception.UNSUPPORTED_TYPE,
                                    f'{self.__class__.__name__} not support {var.sig_type}')

        return value

    def _write(self, uri, value, val_type):
        if isinstance(val_type, str):
            val_type = ValType[val_type.upper()]
        try:
            if val_type == ValType.B1:
                value = int(value)
                value = 1 if value > 0 else 0
            elif val_type in (ValType.F32, ValType.D64):
                value = float(value)
            else:
                value = int(value)

        except (TypeError, ValueError):
            raise exception.SkError(exception.VAR_CFG_ERROR, f'{uri} config error')

        f_code, address, length = map(int, uri.split(':'))
        print('>>+_+_+', address, value)
        if f_code == cst.COILS:
            value = 1 if int(value) > 0 else 0
            self._cmd(f_code=cst.WRITE_SINGLE_COIL, address=address, output_value=value)

        elif f_code == cst.HOLDING_REGISTERS:
            if val_type == ValType.D64:
                output_value = struct.unpack('<HHHH', struct.pack('<d', value))
            elif val_type == ValType.U64:
                output_value = struct.unpack('<HHHH', struct.pack('<Q', value))
            elif val_type == ValType.U32:
                output_value = struct.unpack('<HH', struct.pack('<L', value))
            elif val_type == ValType.U16:
                output_value = (value,)
            else:
                raise exception.SkError(exception.UNSUPPORTED_TYPE,
                                        f'{self.__class__.__name__} not support {val_type}')

            self._cmd(f_code=cst.WRITE_MULTIPLE_REGISTERS, address=address, output_value=output_value)

        else:
            raise exception.SkError(exception.READ_ONLY, f'{uri} is ReadOnly')
        return value

    def read(self, var: IVar) -> T_Val:
        # 没有指定通道，无法设置，直接返回0

        # if not var.channel and var.sig_type != SigType.FREG:
        # raise exception.SkError(exception.VAR_CFG_ERROR, f'{var.name} 没有设置通道')
        # return 0

        # TODO:ESFAC专用，当发过来的channel不为空，既要设置，又要读
        if var.sig_type == SigType.FREG:
            # 把Val_type 转为ValModel.val_type
            # var.val_type = var.val_type.name
            return self._read(var)
        else:
            channel = var.channel
            rpc, in_or_out = var.uri.split(':')
            if re.search(r'(\d+)', in_or_out):
                in_or_out_value = re.search(r'(\d+)', in_or_out).groups()[0]
                in_or_out_value = int(in_or_out_value)
            else:
                raise exception.SkError(exception.UNSUPPORTED_TYPE,
                                        f'{var.name} uri中没有(IN|OUT)的值 ')

            # 有通道，就需要设置,设置好读状态
            if rpc.startswith('ESFAC'):
                # TODO: 如果在其他通道被占用的情况下，需要先把该通道切到0，再切指定通道
                for i in range(1, 6):
                    check_channel: PointModel = PointModel.get(PointModel.sig_name == f'{rpc}_{i}_CHANNEL')
                    v = self._read(check_channel)
                    if v == int(in_or_out_value) and int(channel) != i:
                        self._write(check_channel.uri, 0, check_channel.val_type)

                var_channel: PointModel = PointModel.get(PointModel.sig_name == f'{rpc}_{channel}_CHANNEL')
                self._write(var_channel.uri, in_or_out_value, var_channel.val_type)
                # 等待2s来让设置有用
                time.sleep(2)
                var_state: PointModel = PointModel.get(PointModel.sig_name == f'{rpc}_{channel}_STATE')
                state = self._read(var_state)
                return state
            # rpc 直接检查状态，不需要切通道,只用于读取16个停堆信号，其他rpc不能读取状态和时间
            else:
                var_state: PointModel = PointModel.get(PointModel.sig_name == f'{rpc}_{in_or_out_value}_STATE')
                state = self._read(var_state)
                return state

    def _read(self, var: IVar) -> T_Val:
        if isinstance(var, PointModel):
            val_type = ValType[var.val_type.upper()]
        else:
            val_type = var.val_type

        try:
            f_code, address, length = map(int, var.uri.split(':'))
        except (TypeError, ValueError):
            raise exception.SkError(exception.VAR_CFG_ERROR, f'{var} config error')

        data = self._cmd(f_code=f_code, address=address, quantity_of_x=length)
        if val_type == ValType.D64:
            print('read value:', struct.unpack('<d', struct.pack('<HHHH', *data))[0])
            return struct.unpack('<d', struct.pack('<HHHH', *data))[0]
        elif val_type == ValType.B1:
            return data[0]
        elif val_type == ValType.U64:
            return struct.unpack(f'<Q', struct.pack(f'<HHHH', *data))[0]
        elif val_type == ValType.U16:
            return data[0]
        else:
            raise exception.SkError(exception.UNSUPPORTED_TYPE,
                                    f'{self.__class__.__name__} not support {val_type}')

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
            raise exception.SkError(exception.PROTOCOL_ERROR, e)

    def clear_channel_ai(self, now_channel):
        '''
        当多个AI时使用，避免多个通道都给ai值的情况发生
        :return:
        '''
        for i in range(1, 5):
            for j in range(1, 3):
                var_channel = f'RPC{i}_{j}_CHANNEL'
                var_type = f'RPC{i}_{j}_TYPE'
                var_s_v = f'RPC{i}_{j}_START_VALUE'
                iv_channel: PointModel = PointModel.get(PointModel.sig_name == var_channel)
                iv_type: PointModel = PointModel.get(PointModel.sig_name == var_type)
                iv_s_value: PointModel = PointModel.get(PointModel.sig_name == var_s_v)
                v_ty = self._read(iv_type)
                if now_channel == var_channel or v_ty != 1:
                    continue

                v = self._read(iv_channel)
                if v != 0:
                    self._write(iv_s_value.uri, 0, iv_s_value.val_type)
                    self._write(iv_type.uri, 3, iv_type.val_type)
                    self._write(iv_channel.uri, 0, iv_channel.val_type)


class TXS_Dev(IDev):
    def __int__(self):
        IDev.__init__(self)

    def setup(self, uri):
        host, port = uri.split(':')
        self._url = host
        self._port = port
        # self.socket_client.listen(5)

    def read(self, var: IVar):
        if var.group:

            # 只有M1,只读一个
            if len(list(filter(lambda x: x.channel == 'M2', var.group))) <= 0:
                # 对点专用
                if var.txs_port:
                    var.group[0].txs_port = var.txs_port
                return self._read(var.group[0])

            # 用于比较读到的值是否相同
            value_list = []
            # 当有多个点时，返回所有M2点的值，再进行比较
            for iv in var.group:
                # 对点专用
                if var.txs_port:
                    iv.txs_port = var.txs_port

                if iv.channel == 'M2':
                    value_list.append(self._read(iv))

            # 匹配该点的所有拓展名下的M2的值，如果不相同就报错，相同就返回
            value_list_final = value_list[0]
            for v in value_list:
                if value_list_final != v:
                    raise exception.SkError(f'{var.name}的所有拓展名下的M2值不相同')

            return value_list_final

        return self._read(var)

    def write(self, var: IVar, value: T_Val):
        # 带proc_val使用，会取到一系列的点
        if var.group:
            all_is_m1 = True
            # 只有M1,只读一个
            if len(list(filter(lambda x: x.channel == 'M2', var.group))) > 0:
                all_is_m1 = False

            for iv in var.group:
                # 只设置 M1,这个时候给值就行,通常是取消强制
                if len(var.group) == 1:
                    return self._write(iv, value)

                # 'M2'
                if iv.channel == 'M2':
                    self._write(iv, value)
                # 都是'M1'
                if iv.channel == 'M1':
                    if all_is_m1:
                        self._write(iv, value)
                    # 有M2，M1置为1
                    else:
                        self._write(iv, 1)

            if all_is_m1:
                return int(value)
            else:
                return float(value)

        # 这种情况是直接赋值单点，不带proc_val的时候使用
        else:
            return self._write(var, value)

    def _read(self, var: IVar):
        try:
            print((self._url, int(self._port)))
            socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_client.connect((self._url, int(self._port)))
        except Exception:
            raise exception.SkError(f'与远程主机{self._url}:{self._port}通信被拒绝')
            return
        diagram, block, parameter, cpuid = var.uri.split(':')
        if cpuid:
            data = {
                'message': 'read_cpu',
                'diagram': diagram,
                'block': block,
                'parameter': parameter,
                'cpuid': cpuid,
            }
        else:
            data = {
                'message': 'read',
                'diagram': diagram,
                'block': block,
                'parameter': parameter,
            }

        # 当硬件给值的时候M2不会跟着硬件改变，需要检查port
        # cpuid.port("diagram","block","AO1").value().v
        if var.txs_port:
            data['message'] = 'read_port'

        data = json.dumps(data).encode()
        # size = str(len(data)).encode()
        # print(size)
        # socket_client.send(size)
        socket_client.send(data)
        response = socket_client.recv(1024)
        # print(response)
        response = json.loads(response.decode())
        LOGGER.error('+++', response)
        if response['message'] == 'OK':
            # socket_client.close()
            return response['value']
        else:
            raise exception.SkError(exception.NETWORK_ERROR, f'TXS remote error, {var}, response={response}')

    def _write(self, var: IVar, value: T_Val):
        try:
            socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_client.connect((self._url, int(self._port)))
        except Exception:
            raise exception.SkError(f'与远程主机{self._url}:{self._port}通信被拒绝')
            # return False

        diagram, block, parameter, cpuid = var.uri.split(':')
        try:
            if var.val_type == ValType.B1:
                value = int(value)
                value = 1 if value > 0 else 0
            elif var.val_type == ValType.D64:
                value = float(value)
            else:
                value = int(value)
        except (TypeError, ValueError):
            raise exception.SkError(exception.VAR_CFG_ERROR, f'{var} config error')

        data = {
            'message': 'write_cpu',
            'diagram': diagram,
            'block': block,
            'parameter': parameter,
            'cpuid': cpuid,
            'value': value,
            'type': var.val_type.name,
        }

        data = json.dumps(data).encode()
        # size = str(len(data)).encode()
        # print(size)
        # socket_client.send(size)
        socket_client.send(data)

        response = socket_client.recv(1024)
        response = json.loads(response.decode())

        if response['message'] == 'OK':
            return value
        else:
            raise exception.SkError(exception.VAR_CFG_ERROR, f'Network error {var} not found response:{response}')
        return False

        # socket_client.close()


class TxsPy(object):
    """
    Txs 初始化脚本解释器
    """

    def __init__(self):
        self.source = None
        self.ast = None

    @classmethod
    def compile(cls, source):
        module = ast.parse(source)

        self = TxsPy()
        self.source = source
        self.ast = module
        return self

    def execute(self, sw):
        for exp in self.ast.body:
            if isinstance(exp, (ast.ImportFrom, ast.Import)):
                continue

            if isinstance(exp, ast.Expr):
                try:
                    self.__case_exp(exp, sw)
                except Exception as e:
                    print(e, exp)
                    continue

    def __case_exp(self, exp, sw):
        value = exp.value

        # cpu1111.memory("XRRP111SI103","ASIG001","M1").setValue(1)
        if isinstance(value, ast.Call):
            func = value.func
            if func.attr == 'setValue':
                args = func.value.args
                m_func = func.value.func
                if m_func.attr == 'memory':
                    key, ext, flag = args
                    key = key.s
                    ext = ext.s
                    flag = flag.s
                    cpu = m_func.value.id
                    val = value.args[0].n
                    # 这里有个问题，就是很多点不存在我们的数据库里
                    # txs_uri = f'{key}:{ext}:{flag}:{cpu}'
                    # txs_var = VarModel.filter(VarModel.uri == txs_uri)
                    # if not txs_var:
                    #     LOGGER.error(f'Find Txs By uri={txs_uri} failed')
                    #     return
                    # txs_var = txs_var.first()
                    # print('txs_var>>>', txs_var)
                    # sw.write(txs_var.sig_name, value=f'{val}(TX)')

                    # 临时解决方法，直接把语句发过去
                    script = f'{cpu}.memory("{key}","{ext}","{flag}").setValue({val})'
                    self.write(script)
                    return
            elif func.attr == 'sleep':
                val = value.args[0].n
                time.sleep(val)

    def write(self, script):
        try:
            socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            socket_client.connect(('192.168.20.5', 19513))
        except Exception:
            raise exception.SkError(f'与远程主机{self._url}:{self._port}通信被拒绝')
            # return False

        data = {
            'message': 'exec_python',
            'script': script,
        }

        data = json.dumps(data).encode()
        # size = str(len(data)).encode()
        # print(size)
        # socket_client.send(size)
        socket_client.send(data)

        response = socket_client.recv(1024)
        response = json.loads(response.decode())

        print(response)
        if response['message'] == 'OK':
            return True
        else:
            raise exception.SkError(exception.VAR_CFG_ERROR, f'Network error {script} execute error:{response}')
        return False
