import multiprocessing
import sys
import os

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QApplication, QMdiArea, QMainWindow, QFrame,QHBoxLayout, QDockWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from historyinfluxDB.view.util.vartree import TreeDockWidget
from utils.WorkModels import NetworkConfig, PointModel
from historyinfluxDB.historyDB import select_history
import pyecharts.options as opts
from pyecharts.faker import  Faker
from pyecharts.charts import Line


class smallwindow(QMainWindow):
    """name代表influxdb的数据库库名"""

    def __init__(self, name, parent):
        super().__init__()
        self.name = name
        self.parent = parent.mdi
        self.initUI()

    def initUI(self):
        self.items = TreeDockWidget(self)
        self.items.tree_Signal.connect(self.windowAction)
        self.items.setFloating(False)
        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.items)

    def getdicdata(self):
        """获取数据的函数"""
        lis = []
        dev_list = NetworkConfig.filter(NetworkConfig.protocol == 'modbus')
        var_list = PointModel.filter(PointModel.slot.in_([x.slot for x in dev_list])).order_by(PointModel.id)
        for i in var_list:
            lis.append([i.id, i.sig_name, i.sig_type, i.slot, i.channel])
        return lis

    def clicked1(self):
        print(1)

    

    def windowAction(self, text):
        """在这里可以打开新的窗口同时调用select_history这个函数可以查出历史点的时间和值便于画图"""
        # print(text)
        sub = trendwindow(text,self.name)
        self.mdi.addSubWindow(sub)
        # sub.show()
        sub.showMaximized()
        # self.showMaximized()
        
        

class trendwindow(QMainWindow):
    '''历史趋势图展示窗口'''
    def __init__(self, name, dbName):
        # name为变量点的名称，dbName为当前库名
        super().__init__()
        self.name = name
        self.dbName = dbName
        self.initUI()

    def initUI(self):
        self.mainhboxLayout = QHBoxLayout(self)
        # self.dockWidget = QDockWidget(self)
        self.frame = QFrame()
        self.mainhboxLayout.addWidget(self.frame)
        self.hboxLayout = QHBoxLayout(self.frame)
        self.myHtml = QWebEngineView() # 创建html视图控件
        self.getTrend(self.name)
        self.myHtml.load(QUrl("file:///" + self.name + '.html'))
        self.hboxLayout.addWidget(self.myHtml) 
        self.setLayout(self.mainhboxLayout)
        self.setCentralWidget(self.frame)
        # self.dockWidget.setWidget(self.frame)

        # self.items = QFrame(self)
        # self.items.tree_Signal.connect(self.windowAction)
        # self.dockWidget.setFloating(False)
        # self.mdi = self.menuBar()
        # self.addDockWidget(Qt.LeftDockWidgetArea, self.dockWidget)
        # self.dockWidget.showMaximized()

    def getTrend(self, name) -> Line:
        # 获取趋势图
        allValue = select_history(name, '秒', self.dbName) # 调用历史趋势中的查询接口获取数据
        xValue = []
        yValue = []
        for x in allValue:
            xValue.append(x[0])
            yValue.append(x[1])
        c = (
            Line()
            .add_xaxis(xValue)
            .add_yaxis(name, yValue)
            .set_global_opts(title_opts=opts.TitleOpts(title=name),
                             datazoom_opts=[opts.DataZoomOpts(), opts.DataZoomOpts(type_="inside")], # 设置图中最下端拖拽箱体
                             brush_opts=opts.BrushOpts())

        )
        c.js_host = os.path.join(os.path.abspath(''), 'static\\') # 使用本地js文件
        c.render("{}.html".format(name))

if __name__ == '__main__':
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    ex = smallwindow('123456')
    ex.show()
    sys.exit(app.exec_())
