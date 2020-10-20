import json
import sys
import os

from pyecharts import options as opts
from pyecharts.charts import Page, Tree
from pyecharts.globals import CurrentConfig
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication,QWidget,QHBoxLayout,QFrame
from PyQt5.QtWebEngineWidgets import QWebEngineView
from utils.ClientModels import Procedure, Usecase, UsecaseGroup, Classification, RunResult






class LabelTree(QWidget):
    def __init__(self, projectpath):
        super(LabelTree, self).__init__()
        self.path = os.path.join(projectpath, '.userdata', 'Tree.html').replace('\\', '/')
        self.mainLayout()

    def mainLayout(self):
        self.mainhboxLayout = QHBoxLayout(self)
        self.frame = QFrame(self)
        self.mainhboxLayout.addWidget(self.frame)
        self.hboxLayout = QHBoxLayout(self.frame)
        self.myHtml = QWebEngineView()
        self.getTree()
        self.myHtml.load(QUrl("file:///" + self.path))
        
        self.hboxLayout.addWidget(self.myHtml)
        self.setLayout(self.mainhboxLayout)

    def getpro(self, groupName):
        # 获取树形图中规程信息
        try:
            l =  json.loads(Classification.get_by_name(groupName).procedures)
            r = []
            for a in l:
                try:
                    exist_runresult = RunResult.get(RunResult.procedure_name == a) # 根据运行结果库获取分类中规程执行状态
                    if exist_runresult.is_stop == 1:
                        name = a + '  未完成'
                        r.append({'name' : name})
                    else:
                        name = a + '  已完成'
                        r.append({'name' : name})
                except:
                    name = a + '  未执行'
                    r.append({'name' : name})
            return r
        except:
            return []

    def getcase(self, groupName):
        # 获取树形图中的用例信息
        try:
            l =  json.loads(Classification.get_by_name(groupName).usecases)
            r = []
            for a in l:
                try:
                    exist_runresult = RunResult.get(RunResult.usecase_numbaer == a)
                    if exist_runresult.is_stop == 1:
                        name = a + '  未完成'
                        r.append({'name' : name})
                    else:
                        name = a + '  已完成'
                        r.append({'name' : name})
                except:
                    name = a + '  未执行'
                    r.append({'name' : name})
            return r
        except:
            return []

    def getgroup(self, groupName):
        # 获取树形图中的用例组
        try:
            l =  json.loads(Classification.get_by_name(groupName).usecasegroup)
            r = []
            for a in l:
                try:
                    exist_runresult = RunResult.get(RunResult.usecase_group_name == a)
                    if exist_runresult.is_stop == 1:
                        name = a + '  未完成'
                        r.append({'name' : name})
                    else:
                        name = a + '  已完成'
                        r.append({'name' : name})
                except:
                    name = a + '  未执行'
                    r.append({'name' : name})
            return r
        except:
            return []

    def getTree(self):
        # 获取树形图
        allGroup = [x.name for x in Classification.get_all()]
        dist = {"name": "所有组别", "children":[]}
        for group in allGroup:
            dist['children'] =  [{"name": x, "children": [{"name" : '规程', 'children' : self.getpro(x)}, {"name" : '用例', 'children' : self.getcase(x)}, {"name" : '用例组', 'children' : self.getgroup(x)}]} for x in allGroup]
    #     data = [
    #     {
    #         "children": [
    #             {"name": "规程"},
    #             {
    #                 "children": [
    #                     {"children": [{"name": "I"}], "name": "E"},
    #                     {"name": "F"},
    #                 ],
    #                 "name": "用例",
    #             },
    #             {
    #                 "children": [
    #                     {"children": },
    #                     {"name": "H"},
    #                 ],
    #                 "name": "用例组",
    #             },
    #         ],
    #         "name": "所有组别",
    #     }
    # ]
        data = [dist]
 
        tree=(
         Tree(init_opts=opts.InitOpts(width='2000px',height='1000px',)).add("", data).set_global_opts(title_opts=opts.TitleOpts(title="规程分组"))
            )
        tree.js_host = os.path.join(os.path.abspath(''), 'static\\')
        # print(tree.js_host)

        tree.render(self.path)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = LabelTree()
    ex.show()
    sys.exit(app.exec_())
