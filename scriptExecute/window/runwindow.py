import pickle
import time

from PyQt5 import QtGui
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QPushButton, QTableView, QHBoxLayout, QVBoxLayout, QSplitter
from pubsub import pub

from scriptExecute.execute.runtime import DcsRunTime
from scriptExecute.execute.utils import RunMode
from scriptExecute.window.tableModel.queryModel import tableModel, jgTableModel
from utils.ClientModels import RunResult
from utils.WorkModels import TimeCard


class ScriptWindow(QWidget):
    def __init__(self, data):
        QWidget.__init__(self)
        self.dic1 = None
        self.dic2 = None
        self.run_time = None
        self.data = data
        self.setWindowTitle(self.data.name)
        self.lis = []
        self.list_bg = []
        self.setup_dic1()
        self.setup_dic2()
        pub.subscribe(self.snoop, pub.ALL_TOPICS)

        self.timer = QTimer(self)
        self.timer.start(50)
        self.timer.timeout.connect(self.on_timer)

        self.btn_zd = QPushButton('自动执行')
        self.btn_zd.clicked.connect(self.auto_execution)
        self.btn_db = QPushButton('单步执行')
        self.btn_db.clicked.connect(self.single_step)
        self.btn_xb = QPushButton('下一步')
        self.btn_xb.clicked.connect(self.next_step)
        self.btn_exit = QPushButton('退出')
        self.btn_exit.clicked.connect(self.script_exit)
        self.btn_sx = QPushButton('刷新')
        self.btn_sx.clicked.connect(self.refresh)
        self.btn_sz = QPushButton('设置')
        self.btn_sz.clicked.connect(self.setting)

        # 执行表格
        self.table1 = QTableView()
        self.querymodel1 = tableModel(header=self.dic1['header'], data=self.dic1['data'])
        self.table1.setModel(self.querymodel1)

        # 显示结果表格
        self.table2 = QTableView()
        self.querymodel2 = jgTableModel(header=self.dic2['header'], data=self.dic2['data'])
        self.table2.setModel(self.querymodel2)

        h1_layout = QHBoxLayout()
        h2_layout = QHBoxLayout()
        v_layout = QVBoxLayout()
        h1_layout.addWidget(self.btn_zd)
        h1_layout.addWidget(self.btn_db)
        h1_layout.addWidget(self.btn_xb)
        h1_layout.addWidget(QSplitter())
        h1_layout.addWidget(self.btn_exit)
        h1_layout.addWidget(QSplitter())
        h1_layout.addWidget(self.btn_sx)
        h1_layout.addWidget(self.btn_sz)
        h2_layout.addWidget(self.table1)
        h2_layout.addWidget(self.table2)
        v_layout.addLayout(h1_layout)
        v_layout.addLayout(h2_layout)
        self.setLayout(v_layout)

    def setup_dic1(self):
        lis = ['Step']
        for i in self.data.lines:
            if i.stepNo == 0:
                continue
            lis.append(i.Comments + str(i.stepNo) + str(i.Input_Capture_Times))
        lis1 = []
        lis2 = []
        for i in self.data.lines:
            for j in i.lines:
                if j.lineNo == 1:
                    continue
                else:
                    for z in j.ops:
                        if z.name not in lis1:
                            lis1.append(z.name)
                        lis2.append(z.value)
        lis3 = [lis2[i:i + int(len(lis2) / (len(lis) - 1))] for i in
                range(0, len(lis2), int(len(lis2) / (len(lis) - 1)))]
        l = [i for i in sc(lis3)]
        lis_header = []
        for i in zip(lis1, l):
            a = i[1]
            b = i[0]
            a.insert(0, b)
            lis_header.append(a)
        self.dic1 = {
            'header': lis,
            'data': lis_header,
        }

    def setup_dic2(self):
        self.dic2 = {
            'header': ['信号名', '时间', '计时', '触发沿', '结果'],
            'data': TimeCard.selectTimer(self.data.name)
        }

    def auto_execution(self):
        self.querymodel1.updataStart()
        self.threading = DcsRunTime()
        self.threading.Start(self.data)
        self.threading.start()

    def single_step(self):
        self.querymodel1.updataStart()
        self.threading = DcsRunTime()
        self.threading.SetMode(RunMode.STEP)
        self.threading.Start(self.data)
        self.threading.start()

    def next_step(self):
        self.threading.Next()

    def script_exit(self):
        self.threading.Exit()

    def refresh(self):
        pass

    def setting(self):
        pass

    def snoop(self, topicObj=pub.AUTO_TOPIC, **mesgData):
        line = mesgData['line']
        stepNo = mesgData['stepNo']
        start = mesgData['返回状态']
        if '返回值' in mesgData and mesgData['name'] not in ('T1', 'T2', 'T3'):
            value = mesgData['返回值']
            self.lis.append(value)
        if '报告' in mesgData:
            if mesgData['name'] not in ('T1', 'T2', 'T3'):
                bg = mesgData['报告']
                data = pickle.dumps(bg, protocol=0)
                self.list_bg.append(data)
        if 'finished' in mesgData and mesgData['finished'] == True:
            timeArray = time.localtime(int(pickle.loads(self.list_bg[0]).record.children[0].time))
            self.run_time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            data = [{
                'run_uuid': None,
                'procedure_number': None,
                'usecase_number': None,
                'script_number': self.data.name,
                'run_type': 4,
                'procedure_name': None,
                'script_name': self.data.name,
                'usecase_group_name': None,
                'usecase_group_number': None,
                'run_usecase_index': None,
                'operation_section': 0,
                'section_sort': 0,
                'run_text': self.list_bg,
                'certification': '',
                'run_time': self.run_time,
                'run_result': 1,
                'is_stop': 0,
                'run_big_sort': 0
            }]
            RunResult.insert_many(data).execute()
        if line == 1:
            return
        try:
            self.querymodel1.start[line - 2][stepNo] = start
            for i in range(len(self.lis)):
                self.querymodel2.datas[i][-1] = self.lis[i]
        except:
            pass

    def on_timer(self):
        self.querymodel1.layoutChanged.emit()
        self.querymodel2.layoutChanged.emit()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.threading.is_alive():
            self.threading.close()


def sc(lis):
    for j in range(len(lis[0])):
        l = []
        for i in lis:
            l.append(i[j])
        yield l
