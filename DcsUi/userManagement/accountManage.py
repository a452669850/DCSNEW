from PyQt5.QtWidgets import QMessageBox

from DcsUi.userManagement.AccountManagement import userList, userGroupList, AccountManagement
from DcsUi.userManagement.deleteData import *
from DcsUi.userManagement.userWindow import NewBuildWindow, EditWindow, modifyPassworldWindow, newBuildGroupWindow, \
    userGroupSettingWindow


class user(userList):
    def __init__(self):
        userList.__init__(self)

    def getTableValue(self):
        """获取用户组的数据"""
        gops = User.select()
        lis = []
        row = 1
        for i in gops:
            groups_name = UserGroup.get_groups_of_user(i.id)
            if len(groups_name) > 1:
                for group_name in groups_name:
                    result0 = []
                    result0.append(row)
                    result0.append(i.username)
                    result0.append(i.name)
                    result0.append(group_name)
                    lis.append(result0)
                    row += 1
            elif len(groups_name) == 1:
                result1 = []
                result1.append(row)
                result1.append(i.username)
                result1.append(i.name)
                result1.append(groups_name[0])
                lis.append(result1)
                row += 1
        return lis

    def newBuild(self):
        """新建"""
        self.mywindow = NewBuildWindow()
        self.mywindow.my_Signal.connect(self.active_exit)
        self.mywindow.show()

    def active_exit(self):
        """退出窗口触发该函数"""
        self.queryModel.datas = self.getTableValue()
        self.queryModel.layoutChanged.emit()

    def actionHandler1(self):
        """编辑"""
        row = self.tableView.currentIndex().row()
        self.editwindow = EditWindow(self.getTableValue()[row][1:4])
        self.editwindow.my_Signal.connect(self.active_exit)
        self.editwindow.show()

    def actionHandler2(self):
        """删除"""
        reply = QMessageBox.information(
            self,
            "信息提示",
            "确认删除该用户吗",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == 16384:
            row = self.tableView.currentIndex().row()
            username = self.getTableValue()[row][1]
            groupname = self.getTableValue()[row][3]
            deleteData.userDelete(username, groupname)
            self.queryModel.datas = self.getTableValue()
            self.queryModel.layoutChanged.emit()

    def actionHandler3(self):
        """修改密码"""
        row = self.tableView.currentIndex().row()
        self.modifypassworld = modifyPassworldWindow(self.getTableValue()[row][1])
        self.modifypassworld.show()


class userGroup(userGroupList):
    def __init__(self):
        userGroupList.__init__(self)

    def getTableValue(self):
        """获取数据的函数"""
        gops = Group.select()
        lis = []
        row = 1
        for group in gops:
            result = []
            user_list = []
            opera_list = []
            users = UserGroup.get_users_in_group(group_id=group.id)
            operates = GroupOperatePermission.get_gop_by_group_id(group_id=group.id)
            for user in users:
                user_list.append(user)
            for operate in operates:
                ope = Operation.get_or_none(Operation.id == operate.operation_id)
                opera_list.append(ope.name)
            user_str = ",".join(user_list)
            opera_str = ",".join(opera_list)
            result.append(row)
            result.append(group.name)
            result.append(user_str)
            result.append(group.detail)
            result.append(opera_str)
            lis.append(result)
            row += 1
        return lis

    def newBuild(self):
        """新建"""
        self.buildGroup = newBuildGroupWindow()
        self.buildGroup.my_Signal.connect(self.active_exit)
        self.buildGroup.show()

    def active_exit(self):
        """窗口退出后触发该函数刷新表格"""
        self.queryModel.datas = self.getTableValue()
        self.queryModel.layoutChanged.emit()

    def actionHandler1(self):
        """设置"""
        row = self.tableView.currentIndex().row()
        currentGroupId = selectData.selectGroupID(self.getTableValue()[row][1])
        self.groupWindow = userGroupSettingWindow(currentGroupId)
        self.groupWindow.my_Signal.connect(self.active_exit)
        self.groupWindow.show()

    def actionHandler2(self):
        """删除"""
        reply = QMessageBox.information(
            self,
            "信息提示",
            "确认删除该用户组吗",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == 16384:
            row = self.tableView.currentIndex().row()
            groupname = self.getTableValue()[row][1]
            member = self.getTableValue()[row][2]
            deleteData.deleteGroup(groupname, member)
            self.queryModel.datas = self.getTableValue()
            self.queryModel.layoutChanged.emit()


class AccountManage(AccountManagement):

    def __init__(self):
        AccountManagement.__init__(self)

    def _setdata_(self):
        win1 = user()
        win2 = userGroup()
        self.lis_name = ['用户管理', '用户组管理']
        self.lis_win = [win1, win2]
        self.lis_img = [
            ':/static/UserManagement.png',
            ':/static/UserGroupManagement.png',
        ]

    def changeData(self):
        win = self.right_widget.currentWidget()
        win.queryModel.datas = win.getTableValue()
        win.queryModel.layoutChanged.emit()
