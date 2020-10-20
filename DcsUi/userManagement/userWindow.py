from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

from DcsUi.userManagement.minwindow import myNewBuildWindow, myEditWindow, modifyPassworld, newBuildGroup, \
    userGroupSettings
from utils.AcountModels import *


class NewBuildWindow(myNewBuildWindow):

    def __init__(self):
        myNewBuildWindow.__init__(self)

    def initCombobox(self):
        """下拉框的下拉列表"""
        gops = Group.select()
        lis = []
        for i in gops:
            lis.append(i.name)

        for i in range(len(lis)):
            self.combobox_group.addItem(lis[i])
        self.combobox_group.setCurrentIndex(-1)

    def preservation(self):
        """保存按钮功能函数"""
        username = self.line_username.text()
        name = self.line_name.text()
        groupname = self.combobox_group.currentText()
        passworld = self.line_passworld.text()

        if User.username_valid(username):
            if groupname != '':
                if User.password_valid(passworld):
                    group = Group.get(name=groupname)
                    if User.create_user(username=username, name=name, password=passworld):
                        user = User.get(username=username)
                        user.assign_group(group_id=group.id)
                        self.my_Signal.emit('exit')
                        self.close()
                    else:
                        return False
                    return True
                else:
                    QMessageBox.information(
                        self,
                        "信息提示",
                        "密码格式长度错误，请重新输入！",
                        QMessageBox.Yes | QMessageBox.No
                    )
            else:
                QMessageBox.information(
                    self,
                    "信息提示",
                    "请选择组或者创建组",
                    QMessageBox.Yes | QMessageBox.No
                )
        else:
            QMessageBox.information(
                self,
                "信息提示",
                "用户名格式错误，请重新输入！",
                QMessageBox.Yes | QMessageBox.No
            )


class EditWindow(myEditWindow):
    def __init__(self, lis):
        myEditWindow.__init__(self, lis)

    def initCombobox(self):
        """用户组下拉框列表"""
        gops = Group.select()
        lis = []
        for i in gops:
            lis.append(i.name)
        self.user = User.get_or_none(username=self.list1[0])
        group = UserGroup.get_groups_of_user(self.user)
        index = lis.index(group[0])
        for i in range(len(lis)):
            self.combobox_group.addItem(lis[i])
        self.combobox_group.setCurrentIndex(index)

    def preservation(self):
        """保存"""
        username = self.line_username.text()
        name = self.line_name.text()
        group = self.combobox_group.currentText()
        if username != self.list1[0] and group == self.list1[2]:
            self.user.username = username
            self.user.name = name
            self.user.save()
            self.my_Signal.emit('exit')
            self.close()
        elif username != self.list1[0] and group != self.list1[2]:
            group_id = Group.get(name=group)
            group_pro = Group.get_or_none(name=self.list1[2])
            UserGroup.delete_user_from_group(user_id=self.user.id, group_id=group_pro.id)
            self.user.username = username
            self.user.name = name
            self.user.save()
            self.user.assign_group(group_id=group_id.id)
            self.my_Signal.emit('exit')
            self.close()
        else:
            QMessageBox.information(
                self,
                "信息提示",
                "用户名未更改！",
                QMessageBox.Yes | QMessageBox.No
            )


class modifyPassworldWindow(modifyPassworld):

    def __init__(self, str):
        modifyPassworld.__init__(self, str)

    def preservation(self):
        """保存"""
        primitivePassword = self.line_primitivePassword.text()
        updatePassword = self.line_updatePassword.text()
        confirmPassword = self.line_confirmPassword.text()
        dic = {
            'primitivePassword': primitivePassword,
            'updatePassword': updatePassword,
            'confirmPassword': confirmPassword

        }
        user = User.get_or_none(username=self.name)
        if User.password_valid(primitivePassword):
            if user.verify_password(primitivePassword):
                mp = self.modify_password(username=self.name, fieldData=dic)
                if mp:
                    self.close()
            else:
                QMessageBox.information(
                    self,
                    "信息提示",
                    "原始密码错误，请重新输入",
                    QMessageBox.Yes | QMessageBox.No
                )
        else:
            QMessageBox.information(
                self,
                "信息提示",
                "原始密码格式错误，请重新输入",
                QMessageBox.Yes | QMessageBox.No
            )

    def modify_password(self, username, fieldData):
        """修改密码"""
        user = User.get(username=username)
        dic = fieldData
        primitivePassword = dic['primitivePassword']
        updatePassword = dic['updatePassword']
        confirmPassword = dic['confirmPassword']
        if User.password_valid(updatePassword):
            if User.password_valid(confirmPassword):
                if updatePassword == confirmPassword:
                    user.change_password(old_password=primitivePassword, new_password=confirmPassword)
                    return True
                else:
                    QMessageBox.information(
                        self,
                        "信息提示",
                        "两次密码输入不一致，请重新输入",
                        QMessageBox.Yes | QMessageBox.No
                    )
            else:
                QMessageBox.information(
                    self,
                    "信息提示",
                    "密码格式错误，请重新确认",
                    QMessageBox.Yes | QMessageBox.No
                )
        else:
            QMessageBox.information(
                self,
                "信息提示",
                "密码格式错误，请重新确认",
                QMessageBox.Yes | QMessageBox.No
            )


class newBuildGroupWindow(newBuildGroup):
    def __init__(self):
        newBuildGroup.__init__(self)

    def preservation(self):
        """保存"""
        groupName = self.line_groupName.text()
        groupDescribe = self.line_groupDescribe.text()
        lists = []
        groups = Group.select()
        for group in groups:
            lists.append(group.name)

        if groupName not in lists:
            if groupName:
                Group.create_group(name=groupName, detail=groupDescribe)
                self.my_Signal.emit('exit')
                self.close()
            else:
                QMessageBox.information(
                    self,
                    "信息提示",
                    "组名必填，请重新输入",
                    QMessageBox.Yes | QMessageBox.No
                )
        else:
            QMessageBox.information(
                self,
                "信息提示",
                "此组名已存在，请重新填写组名",
                QMessageBox.Yes | QMessageBox.No
            )


class userGroupSettingWindow(userGroupSettings):

    def __init__(self, group_id):
        userGroupSettings.__init__(self, group_id)

    def get_all_users(self):
        """获取所有用户"""
        users = User.select()
        lists = [user for user in users]
        return lists

    def get_all_operate(self):
        """获取所有操作"""
        operas = Operation.select()
        lis = [opera for opera in operas]
        return lis

    def get_group_operate(self):
        """获取某一个组中所有的操作"""
        return GroupOperatePermission.get_operations_of_group(group_id=self.group_id)

    def get_group_users(self):
        """获取某一个组中所有用户"""
        return [x.user for x in UserGroup.get_ug_by_group_id(self.group_id)]

    def changecb(self, state):
        """复选框状态改变"""
        checkBox = self.sender()
        user = User.get_user_by_username(checkBox.text())
        if state == Qt.Checked:
            UserGroup.add_user_to_group(user.id, self.group_id)
        else:
            UserGroup.delete_user_from_group(user.id, self.group_id)

    def addAllUser(self):
        """全选"""
        users = self.get_all_users()
        for user in users:
            UserGroup.add_user_to_group(user.id, self.group_id)
        for i in self.checkBox_list:
            i.setChecked(True)

    def unAddAllUser(self):
        """全不选"""
        users = self.get_all_users()
        for user in users:
            UserGroup.delete_user_from_group(user.id, self.group_id)
        for i in self.checkBox_list:
            i.setChecked(False)

    def closeEvent(self, event):
        """窗口自带的函数当窗口退出时触发"""
        self.my_Signal.emit('exit')
        self.lis.clear()
        self.close()
