from static.Qss import *
from PyQt5.QtCore import QFile


class CommonHelper:
    def __init__(self):
        pass

    @staticmethod
    def getQss():
        qss_file = QFile(':/static/psblack.Qss')
        qss_file.open(QFile.ReadOnly)
        qss = str(qss_file.readAll(), encoding = 'utf-8') # 读取Qss样式
        qss_file.close()
        return qss