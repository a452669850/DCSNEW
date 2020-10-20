import logging
import sched
import socket
import threading
import time

import modbus_tk.defines as cst
from modbus_tk import LOGGER
from modbus_tk.exceptions import ModbusError
from modbus_tk.modbus_tcp import TcpMaster

logging.basicConfig(
    level=logging.DEBUG,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)


class Block(object):
    __slots__ = ['address', 'reg_type', '_data']

    def __init__(self, address, size, reg_type):
        assert reg_type in {cst.COILS, cst.DISCRETE_INPUTS, cst.HOLDING_REGISTERS, cst.ANALOG_INPUTS}
        self.address = address
        self.reg_type = reg_type
        self._data = [0] * size

    def __repr__(self):
        return '<{cls} {reg_type}-{start}:{stop} {data}>'.format(
            cls=self.__class__.__name__,
            reg_type=self.reg_type,
            start=self.address,
            stop=self.address + len(self) - 1,
            data=self._data
        )

    def __len__(self):
        return len(self._data)

    @property
    def size(self):
        return len(self._data)

    @property
    def readonly(self):
        return self.reg_type in {cst.DISCRETE_INPUTS, cst.ANALOG_INPUTS}

    @property
    def minimum(self):
        return 0

    @property
    def maximum(self):
        return 1 if self.reg_type in {cst.COILS, cst.DISCRETE_INPUTS} else 0xffff

    def offset(self, address):
        if self.address <= address <= self.address + len(self):
            return address - self.address
        raise IndexError('Block address out of range')

    def memset(self, address, values):
        for value in values:
            if not (self.minimum <= value <= self.maximum):
                raise ValueError('value should between {min} and {max}'.format(min=self.minimum, max=self.maximum))
        start = self.offset(address)
        stop = self.offset(address + len(values))
        self._data[start:stop] = values

    def memcpy(self, address, size):
        start = self.offset(address)
        stop = self.offset(address + size)
        return self._data[start:stop]


class Slave(object):
    def __init__(self, host='127.0.0.1', port=502, slave_id=1, timeout=300):
        self.slave_id = slave_id
        self._master = TcpMaster(host, port, timeout_in_sec=timeout / 1000.0)
        self._sample_thread = threading.Thread(name='sampleLoop', target=self._sample_loop)
        self._is_looping = False
        self._memory = {
            cst.COILS: [],
            cst.DISCRETE_INPUTS: [],
            cst.HOLDING_REGISTERS: [],
            cst.ANALOG_INPUTS: [],
        }

    def add_block(self, block):
        assert isinstance(block, Block)
        self._memory[block.reg_type].append(block)

    def merge(self):
        _memory = {
            cst.COILS: [],
            cst.DISCRETE_INPUTS: [],
            cst.HOLDING_REGISTERS: [],
            cst.ANALOG_INPUTS: []
        }
        for reg_type, blocks in self._memory.items():
            sorted_blocks = sorted(blocks, key=lambda x: x.address)
            for block in sorted_blocks:
                if _memory[reg_type]:
                    _block = _memory[reg_type].pop()
                    if block.address + block.size < _block.address or _block.address + _block.size < block.address:
                        _memory[reg_type].append(_block)
                        _memory[reg_type].append(block)
                    else:
                        address = min(block.address, _block.address)
                        size = max(block.address + block.size, _block.address + _block.size) - address
                        _memory[reg_type].append(
                            Block(address=address, size=size, reg_type=reg_type)
                        )
                else:
                    _memory[reg_type].append(block)
        self._memory = _memory

    @property
    def blocks(self):
        for reg_type, blocks in self._memory.items():
            for block in blocks:
                yield block

    def memset(self, reg_type, address, values):
        if reg_type in {cst.COILS, cst.HOLDING_REGISTERS}:
            for block in self._memory.get(reg_type):
                try:
                    block.memset(address, values)
                    return block
                except IndexError:
                    pass
        raise IndexError('Block address out of range')

    def memcpy(self, reg_type, address, size):
        for block in self._memory.get(reg_type, []):
            try:
                return block.memcpy(address, size)
            except IndexError:
                pass
        raise IndexError('Block address out of range')

    def fetch(self):
        for block in self.blocks:
            try:
                result = self._master.execute(
                    slave=self.slave_id,
                    function_code=block.reg_type,
                    starting_address=block.address,
                    quantity_of_x=len(block)
                )
                block.memset(block.address, result)
            except (ModbusError, socket.error) as e:
                LOGGER.error(e)

    def push(self, block):
        function_code = cst.WRITE_MULTIPLE_COILS if block.reg_type is cst.COILS else cst.WRITE_MULTIPLE_REGISTERS
        try:
            result = self._master.execute(
                slave=self.slave_id,
                function_code=function_code,
                starting_address=block.address,
                quantity_of_x=block.size,
                output_value=block._data
            )
            # print result
        except (ModbusError, socket.error) as e:
            LOGGER.error(e)

    def _sample_loop(self, delay=50):
        scheduler = sched.scheduler(timefunc=time.time, delayfunc=time.sleep)

        def _task():
            if self._is_looping:
                scheduler.enter(delay=delay / 1000.0, priority=1, action=_task, argument=())
            # print time.time()
            self.fetch()
            self.ts = time.time()

        _task()
        scheduler.run()

    def start_loop(self):
        self._is_looping = True
        self._sample_thread.setDaemon(True)
        self._sample_thread.start()

    def stop_loop(self):
        self._is_looping = False
        if self._sample_thread.isAlive():
            self._sample_thread.join(.1)  # waiting a sample loop
