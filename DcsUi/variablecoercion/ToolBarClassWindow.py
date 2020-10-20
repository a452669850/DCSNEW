from PyQt5.QtWidgets import QMessageBox

from DcsUi.variablecoercion.ToolBarClass import Deploy
from DcsUi.variablecoercion.model import variableGroupModel
from utils.WorkModels import PointModel


class DeployWindow(Deploy):

    def __init__(self, group_name=None, win_type=True):
        Deploy.__init__(self, group_name, win_type)

    def addGroup(self):
        """添加到组功能函数"""
        if self.group_name == None:
            return
        x = QMessageBox.information(
            self,
            "确认更新",
            "确认更新-[%s]组" % self.group_name,
            QMessageBox.Yes | QMessageBox.No
        )
        if x == 16384:
            points = variableGroupModel.getGroupData(self.group_name)
            variableGroupModel.updataGroup(self.group_name, points)
            self.updata_Group_Signal.emit('')

    def addActive(self, text):
        """保存新组的功能函数"""
        if self.group_name != None:
            points = variableGroupModel.getGroupData(self.group_name)
            if variableGroupModel.createGroup(text, points):
                self.add_Group_Signal.emit('')
                self.close()
            else:
                QMessageBox.information(
                    self,
                    "信息提示",
                    "组名重复",
                    QMessageBox.Yes | QMessageBox.No
                )
        else:
            points = PointModel.all_points()
            if variableGroupModel.createGroup(text, points):
                self.add_Group_Signal.emit('')
                self.close()
            else:
                QMessageBox.information(
                    self,
                    "信息提示",
                    "组名重复",
                    QMessageBox.Yes | QMessageBox.No
                )