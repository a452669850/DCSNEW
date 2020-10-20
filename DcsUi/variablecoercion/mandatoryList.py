from DcsUi.variablecoercion.model import variableGroupModel
from DcsUi.variablecoercion.smallWindow import searchWindow


class mandatoryListWindow(searchWindow):

    def __init__(self, group_name=None):
        searchWindow.__init__(self, group_name)

    def onComboboxActivate(self):
        """强制窗口下拉框函数"""
        text1 = self.line1.text()
        text2 = self.line2.text()
        conditiontext1 = self.comboboxColumn1.currentText()
        conditiontext2 = self.comboboxColumn2.currentText()
        conditiontext3 = self.combobox.currentText()
        if self.group_name == None:
            group_points = variableGroupModel.mandatorysearchDate(
                column1=conditiontext1,
                column2=conditiontext2,
                value1=text1,
                value2=text2,
                relation=conditiontext3
            )
        else:
            group_points = variableGroupModel.mandatorySelectGroupData(
                name=self.group_name,
                column1=conditiontext1,
                column2=conditiontext2,
                value1=text1,
                value2=text2,
                relation=conditiontext3
            )
        self.queryModel.datas = group_points
        self.queryModel.layoutChanged.emit()
