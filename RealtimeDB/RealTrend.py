import sys
import random
import matplotlib
import time

matplotlib.use("Qt5Agg")
from PyQt5 import QtCore
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QSizePolicy, QWidget
from numpy import arange, sin, pi
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from RealtimeDB import iomapping
import datetime

class MyMplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100, varName = None):
        self.name = varName

        # 配置中文显示
        plt.rcParams['font.family'] = ['SimHei']  # 用来正常显示中文标签
        plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

        self.fig = Figure(figsize=(width, height), dpi=dpi)  # 新建一个figure
        self.axes = self.fig.add_subplot(111)  # 建立一个子图，如果要建立复合图，可以在这里修改

        #self.axes.hold(False)  # 每次绘图的时候不保留上一次绘图的结果

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        '''定义FigureCanvas的尺寸策略，这部分的意思是设置FigureCanvas，使之尽可能的向外填充空间。'''
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.t = 0
        self.t_list = []
        self.result_list = []

    '''启动绘制动态图'''

    def start_dynamic_plot(self, *args, **kwargs):
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)  # 每隔一段时间就会触发一次update_figure函数。
        timer.start(1000)  # 触发的时间间隔为1秒。

    '''动态图的绘图逻辑可以在这里修改'''

    def update_figure(self):
        # self.fig.suptitle('测试动态图')
        # l = [random.randint(0, 10) for i in range(4)]
        # self.axes.plot([0, 1, 2, 3], l, 'r')
        # self.axes.grid(True)
        # self.draw()
       
        if self.t % 50 == 0:
            self.axes.clear()
            self.t_list.clear()
            self.result_list.clear()
        self.t += 1
        self.axes.set_ylabel('当前值')
        self.axes.set_xlabel('时间')

        self.t_list.append(time.strftime('%H:%M:%S',time.localtime(time.time())))

        self.result_list.append(iomapping.mem.read(iomapping.read(self.name))) # iomapping.read(self.name)为读取选中变量点的实时数值
        self.axes.plot(self.t_list, self.result_list,c='r',ls='-', marker='o', mec='b',mfc='w')  ## 保存历史数据
        self.draw()
        #plt.plot(t, np.sin(t), 'o')



class MatplotlibWidget(QWidget):
    def __init__(self, parent=None, name = None):
        super(MatplotlibWidget, self).__init__(parent)
        self.name = name
        self.initUi()
        

    def initUi(self):
        self.layout = QVBoxLayout(self)
        self.mpl = MyMplCanvas(self, width=5, height=4, dpi=100, varName = self.name)
        self.mpl.start_dynamic_plot() # 如果你想要初始化的时候就呈现动态图
        self.mpl_ntb = NavigationToolbar(self.mpl, self)  # 添加完整的 toolbar
        self.layout.addWidget(self.mpl)
        self.layout.addWidget(self.mpl_ntb)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = MatplotlibWidget()
    # ui.mpl.start_dynamic_plot() # 测试动态图效果
    ui.show()
    sys.exit(app.exec_())
