# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Classification.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from DcsUi.DragListWIdget import DropListWidget, DragListWidget
from utils.ClientModels import Procedure, Usecase, UsecaseGroup, Classification
import sys
import json

class ClassificationUi(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ClassificationUi, self).__init__(parent)
        self.setupUi()

    def setupUi(self):
        # Form.setObjectName("Form")
        self.resize(976, 707)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 1, 1, 3)
        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 6, 1, 1, 1)

        self.allProList = DragListWidget(self)
        self.allProList.type = 'pro'
        self.allProList.setObjectName("allProList")
        self.gridLayout.addWidget(self.allProList, 5, 1, 1, 1)

        self.proList = DropListWidget(self)
        self.proList.parent = self
        self.proList.type = 'pro'
        self.proList.setObjectName("proList")
        self.gridLayout.addWidget(self.proList, 5, 3, 1, 1)

        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 4, 1, 1, 1)

        self.groupList = DropListWidget(self)
        self.groupList.type = 'group'
        self.groupList.parent = self
        self.groupList.setObjectName("groupList")
        self.gridLayout.addWidget(self.groupList, 9, 3, 1, 1)

        self.line = QtWidgets.QFrame(self)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 9, 2, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.nameEdit = QtWidgets.QLineEdit(self)
        self.nameEdit.setObjectName("nameEdit")
        self.horizontalLayout_2.addWidget(self.nameEdit)

        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)

        self.createButton = QtWidgets.QPushButton(self)
        self.createButton.setObjectName("createButton")
        self.createButton.clicked.connect(self.createClass)
        self.horizontalLayout_2.addWidget(self.createButton)

        self.horizontalLayout_2.setStretch(0, 5)
        self.horizontalLayout_2.setStretch(2, 1)
        self.gridLayout.addLayout(self.horizontalLayout_2, 2, 1, 1, 3)

        self.allCaseList = DragListWidget(self)
        self.allCaseList.type = 'case'
        self.allCaseList.setObjectName("allCaseList")
        self.gridLayout.addWidget(self.allCaseList, 7, 1, 1, 1)

        self.label_4 = QtWidgets.QLabel(self)
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 8, 3, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()

        self.horizontalLayout.setObjectName("horizontalLayout")
        self.chooseBox = QtWidgets.QComboBox(self)
        self.chooseBox.setObjectName("chooseBox")
        self.horizontalLayout.addWidget(self.chooseBox)

        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)

        self.delButton = QtWidgets.QPushButton(self)
        self.delButton.setObjectName("delButton")
        self.horizontalLayout.addWidget(self.delButton)
        self.delButton.clicked.connect(self.deleteClass)

        self.horizontalLayout.setStretch(0, 5)
        self.horizontalLayout.setStretch(2, 1)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 1, 1, 3)
        self.label_5 = QtWidgets.QLabel(self)
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 6, 3, 1, 1)

        self.allGroupList = DragListWidget(self)
        self.allGroupList.setObjectName("allGroupList")
        self.allGroupList.type = 'group'
        self.gridLayout.addWidget(self.allGroupList, 9, 1, 1, 1)

        spacerItem3 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem3, 0, 0, 11, 1)
        self.line_2 = QtWidgets.QFrame(self)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.gridLayout.addWidget(self.line_2, 7, 2, 1, 1)
        self.line_3 = QtWidgets.QFrame(self)
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.gridLayout.addWidget(self.line_3, 5, 2, 1, 1)

        self.caseList = DropListWidget(self)
        self.caseList.type = 'case'
        self.caseList.parent = self
        self.caseList.setObjectName("caseList")
        self.gridLayout.addWidget(self.caseList, 7, 3, 1, 1)

        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem4, 10, 1, 1, 3)
        self.label_3 = QtWidgets.QLabel(self)
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 8, 1, 1, 1)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem5, 0, 4, 11, 1)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem6, 3, 1, 1, 3)
        self.label_6 = QtWidgets.QLabel(self)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 4, 3, 1, 1)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

        self.updateAll()

    def createClass(self):
        # 创建分类
        className = self.nameEdit.text()
        if className:
            if Classification.select().where(Classification.name == className):
                return
            else:
                T = Classification().insert(name = className, procedures = '', usecases = '',usecasegroup = '')
                T.execute()
            self.updateAll()

    def deleteClass(self):
        # 删除当前分类
        reply = QtWidgets.QMessageBox.question(self,
                                     'Check',
                                     "是否要删除选中组？",
                                     QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                     QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            T = Classification.delete().where(Classification.name == self.chooseBox.currentText())
            T.execute()
        else:
            return
        self.updateAll()


    def updateAll(self):
        # 更新界面中所有控件
        self.chooseBox.clear()
        for x in [self.allProList, self.allCaseList, self.allGroupList, self.proList, self.caseList, self.groupList]:
            x.clear()
        procedureList = Procedure.get_all()
        usecaseList = Usecase.get_all()
        usecaseGroupList = UsecaseGroup.get_all()
        classList = Classification.get_all()
        for pro in procedureList:
            pname = pro.name.replace('.xlsx', '')
            self.allProList.makeItem(pname)
            # print(pname)

        for case in usecaseList:
            self.allCaseList.makeItem(case.name)
            # print(case.name)

        for group in usecaseGroupList:
            self.allGroupList.makeItem(group.name)
            # print(group.name)
        try:
            self.chooseBox.addItems([x.name for x in classList])
            currentClass = Classification.get_by_name(self.chooseBox.currentText())
        except:
            return

        if currentClass.procedures and currentClass.procedures != 'null':
            currentPros = json.loads(currentClass.procedures)
            for pro in currentPros:
                self.proList.makeItem(pro)
        if currentClass.usecases and currentClass.usecases != 'null':
            currentUsecases = json.loads(currentClass.usecases)
            for case in currentUsecases:
                self.caseList.makeItem(case)
        if currentClass.usecasegroup and currentClass.usecasegroup != 'null':
            currentUsecasesGroup = json.loads(currentClass.usecasegroup)
            for group in currentUsecasesGroup:
                self.groupList.makeItem(group)





    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        # self.setWindowTitle(_translate("self", "self"))
        self.label_2.setText(_translate("self", "用例列表"))
        self.label.setText(_translate("self", "规程列表"))
        self.createButton.setText(_translate("self", "创建新组"))
        self.label_4.setText(_translate("self", "组内用例组"))
        self.delButton.setText(_translate("self", "删除当前组"))
        self.label_5.setText(_translate("self", "组内用例"))
        self.label_3.setText(_translate("self", "用例组列表"))
        self.label_6.setText(_translate("self", "组内规程"))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    form = Classification()
    form.show()
    app.exec_()