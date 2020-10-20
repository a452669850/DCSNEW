from PyQt5.QtCore import QThread, pyqtSignal, QMutex

from Agreement.SM.skio.exception import SkError
from utils import core
from utils.WorkModels import PointModel

qmut = QMutex()


class Checking(QThread):
    sinOut = pyqtSignal(list)
    interrupt = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.working = True
        self.num = 0
        self.interrupt.connect(self.forceInterrupt)
        self.data = False

    def __del__(self):
        self.working = False
        self.wait()

    def run(self):
        """线程主函数用来检查配置点能否跟下位机进行通讯"""
        qmut.lock()
        points = PointModel.all_points()
        for point in points:
            if self.data:
                break
            try:
                core.MainWindowConfig.IOMapping.skio.read(point.sig_name)
                if point.rhi:
                    core.MainWindowConfig.IOMapping.skio.write(point.sig_name, point.rlo)
                    core.MainWindowConfig.IOMapping.skio.write(point.sig_name, point.rhi)
                    core.MainWindowConfig.IOMapping.skio.write(point.sig_name, (point.rlo + point.rhi) / 2)
                # self.sleep(1)
                stats = True
                lis = [point.id, point.sig_name, point.sig_type, point.channel, stats]
                self.sinOut.emit(lis)
            except SkError as e:
                stats = False
                lis = [point.id, point.sig_name, point.sig_type, point.channel, stats]
                self.sinOut.emit(lis)
        qmut.unlock()

    def forceInterrupt(self):
        self.data = True
