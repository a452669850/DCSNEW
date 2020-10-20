from PyQt5.QtCore import QThread, pyqtSignal

from communication.model import VarModel


class addVarThread(QThread):
    sinOut = pyqtSignal(list)

    def __init__(self, name, number, interval, describe, unit, sig_type, slot, channel, chr, reg):
        super().__init__()
        self.working = True
        self.name = name
        self.number = number
        self.describe = describe
        # 定值
        self.interval = interval
        self.unit = unit
        self.sig_type = sig_type
        self.slot = slot
        self.channel = channel
        self.reg = reg
        self.chr = chr

    def __del__(self):
        self.working = False
        self.wait()

    def run(self):
        i = 0
        j = 0
        interval = 1000 + int(self.interval)
        while i < int(self.number):
            name = self.name + '%d' % j
            describe = self.describe + '%d' % j
            reg = self.reg + str(interval)
            if len(VarModel.select().where(VarModel.reg == reg)) != 0:
                interval += int(self.interval)
                continue
            if len(VarModel.select().where(VarModel.sig_name == name)) != 0:
                j += 1
                continue
            VarModel.create(
                sig_name=name, describe=describe, engineering_unit=self.unit,
                sig_type=self.sig_type, slot=self.slot, channel=self.channel,
                chr=self.chr, reg=reg, initial='0', block='0', offset='0',
                bit='0'
            )
            i += 1
            j += 1
            interval += int(self.interval)
            id = VarModel.get(VarModel.sig_name == name).id
            self.sinOut.emit([id, name, self.sig_type, self.slot, self.channel, ''])
