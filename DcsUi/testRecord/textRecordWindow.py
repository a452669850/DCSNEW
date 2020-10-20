import os
import sys

from PyQt5.QtWidgets import QMessageBox, QApplication

from DcsUi.testRecord.TestRecord import Record
from DcsUi.testRecord.dialogWindow import exportWindow
from DcsUi.testRecord.diolog import diologWin
from DcsUi.testRecord.fileOperation import export_procedure_result
from DcsUi.testRecord.textRecordModel import *


class textRecordWindow(Record):

    def __init__(self):
        Record.__init__(self)

    def onCombobox1Activate(self):
        """该函数是实现查找功能的函数"""
        conditionChoice1 = self.all1.currentText()
        conditionChoice2 = self.all2.currentText()
        text1 = self.qle1.text()
        text2 = self.qle2.text()
        if conditionChoice1 == "全部":
            conditionChoice1 = 0
        elif conditionChoice1 == "规程":
            conditionChoice1 = 1
        elif conditionChoice1 == '用例组':
            conditionChoice1 = 2
        else:
            conditionChoice1 = 3

        if conditionChoice2 == '全部':
            conditionChoice2 = 0
        elif conditionChoice2 == '已完成':
            conditionChoice2 = 1
        else:
            conditionChoice2 = 2
        if conditionChoice1 == 0 and conditionChoice2 == 0 and text1 == '' and text2 == '':
            datas, lis = textRecordModel.search_data(type=conditionChoice1, is_complete=conditionChoice2, number=text1,
                                                     name=text2)
            self.data = lis
            self.runList = datas
            self.dic['data'] = datas
            self.queryModel.datas = self.dic['data']
        else:
            datas, lis = textRecordModel.search_data(type=conditionChoice1, is_complete=conditionChoice2, number=text1,
                                                     name=text2)
            self.data = lis
            self.runList = datas
            self.dic['data'] = datas
            self.queryModel.datas = self.dic['data']

    def searchButtonClicked(self):
        """查找按钮功能函数"""
        self.onCombobox1Activate()
        self.queryModel.layoutChanged.emit()

    def self_certification(self):
        """导出自证报告"""
        row = self.tableView.currentIndex().row()
        if row >= 0:
            data = self.data[row]
            self.export1 = diologWin(data, 'zz')
            self.export1.show()
        else:
            QMessageBox.information(
                self,
                "信息提示",
                "请选择测试结果！",
                QMessageBox.Yes | QMessageBox.No
            )

    def myExport(self):
        """该函数导出测试报告"""
        row = self.tableView.currentIndex().row()
        if row >= 0:
            data = self.data[row]
            self.export2 = diologWin(data, 'cs')
            self.export2.show()
        else:
            QMessageBox.information(
                self,
                "信息提示",
                "请选择测试结果！",
                QMessageBox.Yes | QMessageBox.No
            )

    def openReport(self):
        """该函数打开报告"""
        row = self.tableView.currentIndex().row()
        if row >= 0:
            data = self.data[row]
            result_dir = "..\..\static"
            export_procedure_result(data.run_uuid, data.run_time, result_dir, tmp_file=True)
            cmd = r"D:\dcsdb\static\test_result_template.docx"
            os.system(cmd)
        else:
            QMessageBox.information(
                self,
                "信息提示",
                "请选择测试结果！",
                QMessageBox.Yes | QMessageBox.No
            )

    def actionHandler(self):
        """删除报告"""
        reply = QMessageBox.information(
            self,
            "信息提示",
            "确认删除该报告吗",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == 16384:
            row = self.tableView.currentIndex().row()
            RunResult.delete_obj(self.runList[row][5])
            self.runList.pop(row)
            self.queryModel.datas = self.runList
            self.queryModel.layoutChanged.emit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = textRecordWindow()
    win.show()
    sys.exit(app.exec_())
