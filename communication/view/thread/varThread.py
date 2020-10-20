from PyQt5.QtCore import QThread, pyqtSignal

from communication import iomapping
from xps.ExploreTable import que1


class mythread(QThread):
    my_sin = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.working = True
        self.my_sin.connect(self.stop)
        self.data = False

    def __del__(self):
        self.working = False
        self.wait()

    def run(self) -> None:
        while True:
            if self.data:
                break
            name = que1.get()
            iomapping.set_Current(name)

    def stop(self):
        self.data = True
