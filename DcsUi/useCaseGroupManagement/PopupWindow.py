import json

from PyQt5.QtWidgets import *

from DcsUi.useCaseGroupManagement.myTableView import tableView
from utils.ClientModels import Usecase, UsecaseGroup
from xps.ExploreTable import *


class NewRules(QWidget):
    my_Signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.sec = 0
        self.setWindowTitle('用例组管理')
        self.resize(800, 500)
        self.setFixedSize(self.width(), self.height())
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

        self.dic = {
            'header': ['编号', '名称'],
            'data': []
        }

        self.createTable()

    def createTable(self):
        h1 = QHBoxLayout()
        self.label1 = QLabel('用例组名称：')
        # self.label2 = QLabel('【提示：用例组可上下拖拽调整顺序！】')
        self.label3 = QLabel('用例组编号：')
        self.line = QLineEdit(self)
        self.number_line = QLineEdit(self)
        h1.addWidget(self.label1)
        h1.addWidget(self.line)
        # h1.addWidget(self.label2)
        # h1.addWidget(QSplitter())

        h3 = QHBoxLayout()
        h3.addWidget(self.label3)
        h3.addWidget(self.number_line)
        # h3.addWidget(QSplitter())
        # h3.addWidget(self.label2)

        h2 = QHBoxLayout()
        self.btn1 = QPushButton('全选')
        self.btn2 = QPushButton('全不选')
        self.btn3 = QPushButton('创建用例组')

        self.btn1.clicked.connect(self.selectAll)
        self.btn2.clicked.connect(self.noSelectAll)
        self.btn3.clicked.connect(self.newRulesGroup)

        h2.addWidget(QSplitter())
        h2.addWidget(self.btn1)
        h2.addWidget(self.btn2)
        h2.addWidget(self.btn3)
        h2.addWidget(QSplitter())

        self.selectSql()
        self.table = MyModel(self.dic['header'], self.dic['data'])
        self.tableview = tableView()
        self.tableview.setModel(self.table)

        mainLayout = QVBoxLayout(self)
        mainLayout.addLayout(h1)
        mainLayout.addLayout(h3)
        mainLayout.addWidget(self.tableview)
        mainLayout.addLayout(h2)

    def selectSql(self):
        pass
        # gops = Usecase.select()
        # for i in gops:
        #     self.dic['data'].append([i.number, i.name])

    def selectAll(self):
        pass
        # isOn = True
        # self.table.headerClick(isOn)

    def noSelectAll(self):
        pass
        # isOn = False
        # self.table.headerClick(isOn)

    def newRulesGroup(self):
        pass
        # text = self.line.text()
        # text_number = self.number_line.text()
        # row = 0
        # lis = []
        # if 'Checked' not in self.table.checkList:
        #     QMessageBox.information(self,
        #                             "Message",
        #                             "请至少选择一个用例！",
        #                             QMessageBox.Yes | QMessageBox.No)
        # elif text == "" or text_number == "":
        #     QMessageBox.information(self,
        #                             "Message",
        #                             "请完整填写用例组名称及用例编号！",
        #                             QMessageBox.Yes | QMessageBox.No)
        # else:
        #     for i in self.table.checkList:
        #         if i == 'Checked':
        #             lis.append(self.table.datas[row][1])
        #         row += 1
        #     usecasegroup = UsecaseGroup()
        #     usecasegroup.name = text  # 自己填写的用例组的名称
        #     usecasegroup.usecase = json.dumps(lis)
        #     usecasegroup.usecase_group_number = text_number
        #     check_usecasegroup = None
        #     try:
        #         check_usecasegroup = UsecaseGroup.get(UsecaseGroup.name == text)
        #     except:
        #         pass
        #     if check_usecasegroup:
        #         UsecaseGroup.delete_obj(check_usecasegroup.id)
        #         usecasegroup.save()
        #         QMessageBox.information(self,
        #                                 "消息框标题",
        #                                 "用例组创建成功",
        #                                 QMessageBox.Yes | QMessageBox.No)
        #         self.my_Signal.emit('用例组创建成功')
        #         self.close()
        #     else:
        #         usecasegroup.save()
        #         QMessageBox.information(self,
        #                                 "消息框标题",
        #                                 "用例组创建成功",
        #                                 QMessageBox.Yes | QMessageBox.No)
        #         self.my_Signal.emit('用例组创建成功')
        #         self.close()


if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    win = NewRules()
    win.show()
    sys.exit(app.exec_())
