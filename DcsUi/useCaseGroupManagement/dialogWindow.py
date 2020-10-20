import json
import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

from DcsUi.useCaseGroupManagement.PopupWindow import NewRules
from DcsUi.useCaseGroupManagement.dialogWin import newBuildWindow
from utils.ClientModels import UsecaseGroup


class editUsecaseGroup(newBuildWindow):

    def __init__(self, name):
        super().__init__()
        self.name = name
        self.btn3.setText('修改用例组')

        self.line.setText(self.name)

    def newRulesGroup(self):
        """修改用例组"""
        text = self.line.text()
        row = 0
        lis = []
        if 'Checked' not in self.table.checkList:
            QMessageBox.information(self,
                                    "Message",
                                    "请至少选择一个用例！",
                                    QMessageBox.Yes | QMessageBox.No)
        elif text == "":
            QMessageBox.information(self,
                                    "Message",
                                    "请输入用例组名称！",
                                    QMessageBox.Yes | QMessageBox.No)
        else:
            for i in self.table.checkList:
                if i == 'Checked':
                    lis.append(self.table.datas[row][1])
                row += 1
            usecasegroup = UsecaseGroup.get(UsecaseGroup.name == self.name)
            usecasegroup.name = text  # 自己填写的用例组的名称
            usecasegroup.usecase = json.dumps(lis)
            usecasegroup.save()
            QMessageBox.information(self,
                                    "消息框标题",
                                    "用例组修改成功",
                                    QMessageBox.Yes | QMessageBox.No)
            self.my_Signal.emit('用例组创建成功')
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    example = editUsecaseGroup()
    # 显示窗口
    example.show()
    sys.exit(app.exec_())
