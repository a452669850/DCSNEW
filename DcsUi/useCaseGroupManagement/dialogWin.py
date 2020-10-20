import json

from PyQt5.QtWidgets import QMessageBox

from utils.ClientModels import Usecase, UsecaseGroup
from DcsUi.useCaseGroupManagement.PopupWindow import NewRules


class newBuildWindow(NewRules):
    def __init__(self):
        NewRules.__init__(self)

    def selectSql(self):
        """从数据库中查找所有数据的函数"""
        gops = Usecase.select()
        for i in gops:
            self.dic['data'].append([i.number, i.name])

    def selectAll(self):
        """全选"""
        isOn = True
        self.table.headerClick(isOn)

    def noSelectAll(self):
        """全不选"""
        isOn = False
        self.table.headerClick(isOn)

    def newRulesGroup(self):
        """新用例组"""
        text = self.line.text()
        text_number = self.number_line.text()
        row = 0
        lis = []
        if 'Checked' not in self.table.checkList:
            QMessageBox.information(self,
                                    "Message",
                                    "请至少选择一个用例！",
                                    QMessageBox.Yes | QMessageBox.No)
        elif text == "" or text_number == "":
            QMessageBox.information(self,
                                    "Message",
                                    "请完整填写用例组名称及用例编号！",
                                    QMessageBox.Yes | QMessageBox.No)
        else:
            for i in self.table.checkList:
                if i == 'Checked':
                    lis.append(self.table.datas[row][1])
                row += 1
            usecasegroup = UsecaseGroup()
            usecasegroup.name = text  # 自己填写的用例组的名称
            usecasegroup.usecase = json.dumps(lis)
            usecasegroup.usecase_group_number = text_number
            check_usecasegroup = None
            try:
                check_usecasegroup = UsecaseGroup.get(UsecaseGroup.name == text)
            except:
                pass
            if check_usecasegroup:
                UsecaseGroup.delete_obj(check_usecasegroup.id)
                usecasegroup.save()
                QMessageBox.information(self,
                                        "消息框标题",
                                        "用例组创建成功",
                                        QMessageBox.Yes | QMessageBox.No)
                self.my_Signal.emit('用例组创建成功')
                self.close()
            else:
                usecasegroup.save()
                QMessageBox.information(self,
                                        "消息框标题",
                                        "用例组创建成功",
                                        QMessageBox.Yes | QMessageBox.No)
                self.my_Signal.emit('用例组创建成功')
                self.close()