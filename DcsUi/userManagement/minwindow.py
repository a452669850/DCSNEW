from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, QPushButton, QVBoxLayout, QHBoxLayout, QSplitter, \
    QGridLayout, QGroupBox, QCheckBox

from DcsUi.userManagement.myQGroupBox import GroupBox


class myNewBuildWindow(QDialog):
    my_Signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

        self.init()

    def init(self):
        self.setWindowTitle('添加用户')

        self.lab_username = QLabel('用户名：')
        self.lab_name = QLabel('姓名：')
        self.lab_group = QLabel('所属组：')
        self.lab_passworld = QLabel('登录密码：')

        self.line_username = QLineEdit()
        self.line_name = QLineEdit()
        self.line_passworld = QLineEdit()
        self.line_passworld.setEchoMode(QLineEdit.Password)

        self.commit_but = QPushButton('保存')
        self.cancel_btn = QPushButton('取消')
        self.commit_but.clicked.connect(self.preservation)
        self.cancel_btn.clicked.connect(self.close)

        self.combobox_group = QComboBox(self, minimumWidth=100)

        lis = [
            self.lab_username, self.line_username,
            self.lab_name, self.line_name,
            self.lab_group, self.combobox_group,
            self.lab_passworld, self.line_passworld
        ]

        layout = QVBoxLayout()
        h_grid = QGridLayout()
        h_btn = QHBoxLayout()

        positions = [(i, j) for i in range(4) for j in range(2)]

        for position, control in zip(positions, lis):
            h_grid.addWidget(control, *position)

        h_btn.addWidget(QSplitter())
        h_btn.addWidget(self.commit_but)
        h_btn.addWidget(self.cancel_btn)
        h_btn.addWidget(QSplitter())

        layout.addLayout(h_grid)
        layout.addLayout(h_btn)

        self.setLayout(layout)
        self.initCombobox()

    def initCombobox(self):
        pass

    def preservation(self):
        pass


class myEditWindow(QDialog):
    my_Signal = QtCore.pyqtSignal(str)

    def __init__(self, lis):
        super().__init__()
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

        self.list1 = lis
        self.init()

    def init(self):
        self.setWindowTitle('编辑用户信息')

        self.lab_username = QLabel('用户名：')
        self.lab_name = QLabel('姓名：')
        self.lab_group = QLabel('所属组')

        self.line_username = QLineEdit(self.list1[0])
        self.line_name = QLineEdit(self.list1[1])

        self.btn_commit = QPushButton('保存')
        self.btn_cancel = QPushButton('取消')
        self.btn_commit.clicked.connect(self.preservation)
        self.btn_cancel.clicked.connect(self.close)

        self.combobox_group = QComboBox(self, minimumWidth=100)
        self.initCombobox()

        lis = [
            self.lab_username, self.line_username,
            self.lab_name, self.line_name,
            self.lab_group, self.combobox_group,
        ]

        layout = QVBoxLayout()
        h_grid = QGridLayout()
        h_btn = QHBoxLayout()

        positions = [(i, j) for i in range(4) for j in range(2)]

        for position, control in zip(positions, lis):
            h_grid.addWidget(control, *position)

        h_btn.addWidget(QSplitter())
        h_btn.addWidget(self.btn_commit)
        h_btn.addWidget(self.btn_cancel)
        h_btn.addWidget(QSplitter())

        layout.addLayout(h_grid)
        layout.addLayout(h_btn)

        self.setLayout(layout)

    def initCombobox(self):
        pass

    def preservation(self):
        pass


class modifyPassworld(QDialog):
    my_Signal = QtCore.pyqtSignal(str)

    def __init__(self, str):
        super().__init__()
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

        self.name = str

        self.init()

    def init(self):
        self.setWindowTitle('修改密码')

        self.lab_primitivePassword = QLabel('原始密码')
        self.lab_updatePassword = QLabel('更新密码')
        self.lab_confirmPassword = QLabel('确认密码')

        self.line_primitivePassword = QLineEdit()
        self.line_updatePassword = QLineEdit()
        self.line_confirmPassword = QLineEdit()
        self.line_primitivePassword.setEchoMode(QLineEdit.Password)
        self.line_updatePassword.setEchoMode(QLineEdit.Password)
        self.line_confirmPassword.setEchoMode(QLineEdit.Password)

        self.btn_commit = QPushButton('保存')
        self.btn_cancel = QPushButton('取消')
        self.btn_commit.clicked.connect(self.preservation)
        self.btn_cancel.clicked.connect(self.close)

        lis = [
            self.lab_primitivePassword, self.line_primitivePassword,
            self.lab_updatePassword, self.line_updatePassword,
            self.lab_confirmPassword, self.line_confirmPassword,
        ]

        layout = QVBoxLayout()
        h_grid = QGridLayout()
        h_btn = QHBoxLayout()

        positions = [(i, j) for i in range(3) for j in range(2)]

        for position, control in zip(positions, lis):
            h_grid.addWidget(control, *position)

        h_btn.addWidget(QSplitter())
        h_btn.addWidget(self.btn_commit)
        h_btn.addWidget(self.btn_cancel)
        h_btn.addWidget(QSplitter())

        layout.addLayout(h_grid)
        layout.addLayout(h_btn)

        self.setLayout(layout)

    def preservation(self):
        pass

    def modify_password(self, username, fieldData):
        pass


class newBuildGroup(QDialog):
    my_Signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)

        self.init()

    def init(self):
        self.setWindowTitle('添加组')

        self.lab_groupName = QLabel('组名')
        self.lab_groupDescribe = QLabel('组描述')

        self.line_groupName = QLineEdit()
        self.line_groupDescribe = QLineEdit()

        self.btn_commit = QPushButton('保存')
        self.btn_cancel = QPushButton('取消')
        self.btn_commit.clicked.connect(self.preservation)
        self.btn_cancel.clicked.connect(self.close)

        lis = [
            self.lab_groupName, self.line_groupName,
            self.lab_groupDescribe, self.line_groupDescribe
        ]

        layout = QVBoxLayout()
        h_grid = QGridLayout()
        h_btn = QHBoxLayout()

        positions = [(i, j) for i in range(2) for j in range(2)]
        for position, control in zip(positions, lis):
            h_grid.addWidget(control, *position)

        h_btn.addWidget(QSplitter())
        h_btn.addWidget(self.btn_commit)
        h_btn.addWidget(self.btn_cancel)
        h_btn.addWidget(QSplitter())

        layout.addLayout(h_grid)
        layout.addLayout(h_btn)

        self.setLayout(layout)

    def preservation(self):
        pass


class userGroupSettings(QDialog):
    my_Signal = QtCore.pyqtSignal(str)

    def __init__(self, group_id):
        super().__init__()
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint)
        self.setWindowTitle('用户组管理')

        self.lis = []

        self.group_id = group_id

        self.checkBox_list = []
        self.checkBox_lis = []

        self.init()

    def init(self):
        self.createCheckBox()
        self.createOperateCheckBox2()

        mainLayout = QVBoxLayout()
        hboxLayout = QHBoxLayout()
        mainLayout.addLayout(hboxLayout)
        mainLayout.addWidget(self.groupBox1)
        mainLayout.addWidget(self.groupBox3)

        self.setLayout(mainLayout)

    def createCheckBox(self):
        self.btn_allUser = QPushButton('全选用户')
        self.btn_unAllUser = QPushButton('全不选用户')
        self.btn_allUser.clicked.connect(self.addAllUser)
        self.btn_unAllUser.clicked.connect(self.unAddAllUser)

        self.groupBox1 = QGroupBox('用户管理')
        lis = self.get_group_users()
        layout = QGridLayout()
        positions = [(i, j) for i in range(len(self.get_all_users()) // 5 + 1) for j in range(5)]
        for position, name in zip(positions, self.get_all_users()):
            checkBox = QCheckBox(name.username)
            self.checkBox_list.append(checkBox)
            checkBox.stateChanged.connect(self.changecb)
            layout.addWidget(checkBox, *position)
            if name in lis:
                checkBox.setChecked(True)
        layout.addWidget(self.btn_allUser, len(self.get_all_users()) // 5 + 1, 5)
        layout.addWidget(self.btn_unAllUser, len(self.get_all_users()) // 5 + 1, 4)
        self.groupBox1.setLayout(layout)

    def createOperateCheckBox2(self):
        self.groupBox3 = QGroupBox('权限')
        layout = QVBoxLayout()
        self.group1 = GroupBox(name='工程模块', key=1, group_id=self.group_id)
        self.group2 = GroupBox(name='配置管理模块', key=2, group_id=self.group_id)
        self.group3 = GroupBox(name='执行模块', key=3, group_id=self.group_id)
        self.group4 = GroupBox(name='记录模块', key=4, group_id=self.group_id)
        self.group5 = GroupBox(name='账户管理', key=5, group_id=self.group_id)
        layout.addWidget(self.group1)
        layout.addWidget(self.group2)
        layout.addWidget(self.group3)
        layout.addWidget(self.group4)
        layout.addWidget(self.group5)
        self.groupBox3.setLayout(layout)

    def get_all_users(self):
        pass

    def get_all_operate(self):
        pass

    def get_group_operate(self):
        pass

    def get_group_users(self):
        pass

    def changecb(self, state):
        pass

    def addAllUser(self):
        pass

    def unAddAllUser(self):
        pass

    def closeEvent(self, event):
        pass
