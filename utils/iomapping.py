import os
from pathlib import Path

from utils.WorkModels import PointModel


class IOMapping:
    def __init__(self, path, number):
        super().__init__()
        if number == 1:
            from Agreement.FQ.skio.manage import SkIO
        elif number == 2:
            from Agreement.modus.skio.manage import SkIO
        elif number == 3:
            from Agreement.SM.skio.manage import SkIO

        self.skio = SkIO()
        self.skio.setup(Path(os.path.join(path, 'demo')))

        self.current_value = {point.sig_name: None for point in PointModel.all_points()}
        self.force_value = {point.sig_name: None for point in PointModel.all_points()}

    def setforce(self, name, value):
        self.force_value[name] = self.skio.write(name, value)[0]

    def dumpforce(self, name):
        self.force_value[name] = None

    def setcurrent(self, name):
        self.current_value[name] = self.skio.read(name, remote=True)

    def setupvalue(self):
        self.current_value = {point.sig_name: None for point in PointModel.all_points()}
        self.force_value = {point.sig_name: None for point in PointModel.all_points()}
