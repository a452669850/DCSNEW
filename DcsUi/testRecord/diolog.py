from PyQt5.QtWidgets import QFileDialog

from DcsUi.testRecord.dialogWindow import exportWindow
from DcsUi.testRecord.fileOperation import export_procedure_result, exportCertification


class diologWin(exportWindow):

    def __init__(self, data, ctype):
        exportWindow.__init__(self, data, ctype)

    def commitFile(self):
        """导出报告按钮功能函数"""
        text = self.qle.text()
        if self.type == 'cs':
            export_procedure_result(self.data.run_uuid, self.data.run_time, text)
        elif self.type == 'zz':
            exportCertification(self.data.run_uuid, self.data.run_time, text)
        self.close()

    def commitPath(self):
        """选择文件功能函数"""
        fname = QFileDialog.getExistingDirectory(self,
                                                 "选取文件夹",
                                                 "C:/")  # 起始路径
        self.qle.setText(fname)
