from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QGridLayout, QCheckBox

from DcsUi.userManagement.deleteData import GroupOperatePermission, selectData
from utils.AcountModels import Operation
from utils.core import MainWindowConfig


class myGroupBox(QGroupBox):

    def __init__(self, name, key, group_id):
        super().__init__()
        self.key = key
        self.name = name
        self.group_id = group_id
        self.lis = []
        self.map_list = MainWindowConfig.DIC[self.key]

        self.checkBox_list = []

        self.setTitle(self.name)

        self.setCheckable(True)
        self.setChecked(False)

        self.clicked.connect(self.change)

        self.statechecked()

        gridLayout = QGridLayout()
        positions = [(i, j) for i in range(len(self.map_list) // 5 + 1) for j in range(5)]
        for position, name in zip(positions, self.map_list):
            checkBox = QCheckBox(name)
            self.checkBox_list.append(checkBox)
            checkBox.stateChanged.connect(self.operateChangecb)
            gridLayout.addWidget(checkBox, *position)
            if name in self.select_operations_of_group():
                checkBox.setChecked(True)
        self.setLayout(gridLayout)

    def select_operations_of_group(self):
        pass

    def statechecked(self):
        pass

    def operateChangecb(self, state):
        pass

    def change(self, checked):
        pass


class GroupBox(myGroupBox):
    """自定义的groupBox"""
    def __init__(self, name, key, group_id):
        myGroupBox.__init__(self, name, key, group_id)

    def select_operations_of_group(self):
        """查询租的操作"""
        return GroupOperatePermission.get_operations_of_group(group_id=self.group_id)

    def statechecked(self):
        """groupbox中自带的函数用来检查复选卡的状态是否选中"""
        operagroup = selectData.selectOperationGroup(self.group_id)
        for i in operagroup:
            if i.name in self.map_list:
                self.setChecked(True)
        self.clicked.connect(self.change)

    def operateChangecb(self, state):
        """当复选框状态变更时触发该函数"""
        checkBox = self.sender()
        opera = Operation.get_operation(checkBox.text())
        if state == Qt.Checked:
            GroupOperatePermission.add_operation_to_group(opera.id, self.group_id)
        else:
            GroupOperatePermission.delete_operation_from_group(opera.id, self.group_id)

    def change(self, checked):
        """用来改变复选框状态"""
        if checked == False:
            for i in self.checkBox_list:
                i.setChecked(False)
        if checked == True:
            for j in self.checkBox_list:
                j.setChecked(True)
