# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'parse.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from utils.ClientModels import Phrase


class PhraseUI(QtWidgets.QDialog):
    '''短语库界面'''
    def __init__(self):
        super(PhraseUI, self).__init__()
        self.setupUi()
        self.getPhrase()

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(595, 450)

        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")

        self.phraseView = PhraseTabView(self)
        # self.phraseView.setGeometry(QtCore.QRect(20, 20, 551, 361))
        self.phraseView.setObjectName("phraseView")
        self.model = QtGui.QStandardItemModel(0,0)
        self.model.setHorizontalHeaderLabels(['ID', '名称', '操作','变量(可选)'])
        self.phraseView.setModel(self.model)
        self.phraseView.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.phraseView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.phraseView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)

        self.newButton = QtWidgets.QPushButton(self)
        # self.newButton.setGeometry(QtCore.QRect(304, 402, 81, 31))
        self.newButton.setObjectName("newButton")
        self.newButton.clicked.connect(self.newPhrase)

        self.editButton = QtWidgets.QPushButton(self)
        # self.editButton.setGeometry(QtCore.QRect(394, 402, 81, 31))
        self.editButton.setObjectName("editButton")
        self.editButton.clicked.connect(self.editPhrase)

        self.delButton = QtWidgets.QPushButton(self)
        # self.delButton.setGeometry(QtCore.QRect(484, 402, 81, 31))
        self.delButton.setObjectName("delButton")
        self.delButton.clicked.connect(self.delPhrase)

        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.editButton.setMinimumSize(QtCore.QSize(0, 25))
        self.newButton.setMinimumSize(QtCore.QSize(0, 25))
        self.delButton.setMinimumSize(QtCore.QSize(0, 25))
        self.gridLayout.addWidget(self.newButton, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.editButton, 1, 2, 1, 1)
        self.gridLayout.addWidget(self.delButton, 1, 3, 1, 1)
        self.gridLayout.addWidget(self.phraseView, 0, 0, 1, 4)
        self.gridLayout.addItem(spacerItem, 1, 0, 1, 1)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "短语库管理"))
        self.newButton.setText(_translate("Dialog", "新建"))
        self.editButton.setText(_translate("Dialog", "编辑"))
        self.delButton.setText(_translate("Dialog", "删除"))

    def getPhrase(self):
        # 从数据库中查询短语并添加到表格中
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['ID', '名称', '操作','变量(可选)'])
        allPhrase = Phrase.get_all()
        for phrase in allPhrase:
            phrasList = [phrase.id, phrase.name, phrase.operation, phrase.var]
            self.model.appendRow([QtGui.QStandardItem(str(x)) if x is not None else QtGui.QStandardItem(' ') for x in phrasList])
        self.model.layoutChanged.emit()
        
    def editPhrase(self):
        # 修改短语
        if self.phraseView.currentIndex().row() < 0:
            return
        currentId = self.model.item(self.phraseView.currentIndex().row(), 0).text() # 获取当前选中短语
        self.editUi = EditUi('edit', currentId, self) # 打开修改短语界面
        self.editUi.setWindowModality(QtCore.Qt.ApplicationModal)
        self.editUi.show()

    def delPhrase(self):
        # 删除短语库
        if self.phraseView.currentIndex().row() < 0:
            return
        currentId = self.model.item(self.phraseView.currentIndex().row(), 0).text()
        Phrase.delete_obj(currentId)
        self.getPhrase() # 删除后刷新当前界面视图

    def newPhrase(self):
        # 创建新短语
        self.newUi = EditUi('new', -1, self)
        self.newUi.setWindowModality(QtCore.Qt.ApplicationModal)
        self.newUi.show()


class EditUi(QtWidgets.QDialog):
    # 修改短语库界面（新建及修改均为同一类，根据传参显示不同类型界面）
    def __init__(self, uiType, ID, parent):
        # uiType：界面类型 ID：表格中当前索引 parent：父窗口
        super(EditUi, self).__init__()
        self.type = uiType
        self.ID = ID
        self.parent = parent
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Dialog")
        self.resize(436, 155)
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 3, 1, 1)
        self.label = QtWidgets.QLabel(self)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.label_2 = QtWidgets.QLabel(self)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 2, 0, 1, 1)

        # spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        # self.gridLayout.addItem(spacerItem2, 3, 0, 1, 1)

        self.label_3 = QtWidgets.QLabel(self)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)

        self.varEdit = QtWidgets.QLineEdit(self)
        self.varEdit.setObjectName("varEdit")
        self.gridLayout.addWidget(self.varEdit, 3, 1, 1, 5)

        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 4, 4, 1, 1)
        self.pushButton.clicked.connect(self.confirm)

        self.cancelButton = QtWidgets.QPushButton(self)
        self.cancelButton.setObjectName("cancelButton")
        self.cancelButton.clicked.connect(self.close)

        self.gridLayout.addWidget(self.cancelButton, 4, 5, 1, 1)
        self.nameEdit = QtWidgets.QLineEdit(self)
        self.nameEdit.setObjectName("nameEdit")
        self.gridLayout.addWidget(self.nameEdit, 0, 1, 1, 5)

        # self.oprEdit = QtWidgets.QLineEdit(self)
        # self.oprEdit.setObjectName("oprEdit")
        # self.gridLayout.addWidget(self.oprEdit, 1, 1, 1, 5)

        self.oprEditBox = QtWidgets.QComboBox(self)
        self.oprEditBox.addItem("SET")
        self.oprEditBox.addItem("CHECK")
        self.oprEditBox.addItem("CALL")
        self.oprEditBox.addItem("DELAY")
        self.oprEditBox.setObjectName("oprEdit")
        self.gridLayout.addWidget(self.oprEditBox, 1, 1, 1, 5)

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)
        if self.type == 'edit':
            self.nameEdit.setText(Phrase.get_by_id(self.ID).name)
            # self.oprEdit.setText(Phrase.get_by_id(self.ID).operation)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        if self.type == 'new':
            self.setWindowTitle(_translate("Dialog", "新建短语"))
        else:
            self.setWindowTitle(_translate("Dialog", "编辑短语"))
        self.label.setText(_translate("Dialog", "  名称："))
        self.label_2.setText(_translate("Dialog", "  操作："))
        self.label_3.setText(_translate("Dialog", "  变量："))
        self.pushButton.setText(_translate("Dialog", "确定"))
        self.cancelButton.setText(_translate("Dialog", "取消"))

    def confirm(self):
        # 确认按钮点击事件
        if self.type == 'new':
            try:
                Phrase.get(Phrase.name == self.nameEdit.text())
                # query = Phrase.update(name = self.nameEdit.text(), operation = self.oprEdit.text()).where(Phrase.name == self.nameEdit.text())
                query = Phrase.update(name = self.nameEdit.text(), operation = self.oprEditBox.currentText()).where(Phrase.name == self.nameEdit.text(), Phrase.var == self.varEdit.text())
                query.execute()
            except:
                # Phrase.create(name = self.nameEdit.text(), operation = self.oprEdit.text())
                Phrase.create(name = self.nameEdit.text(), operation = self.oprEditBox.currentText(), var = self.varEdit.text())
        if self.type == 'edit':
            try:
                # query = Phrase.update(name = self.nameEdit.text(), operation = self.oprEdit.text()).where(Phrase.id == self.ID)
                query = Phrase.update(name = self.nameEdit.text(), operation = self.oprEditBox.currentText(), var = self.varEdit.text()).where(Phrase.id == self.ID)   
                query.execute()
            except:
                print('error')
        self.parent.getPhrase()# 修改数据库后
        self.close()

class PhraseTabView(QtWidgets.QTableView):
    '''短语显示列表'''
    def __init__(self, parent):
        super(PhraseTabView, self).__init__()
        self.parent = parent

    def mouseDoubleClickEvent(self, event):
        # 重写表格中鼠标双击事件
        QtWidgets.QTableView.mouseDoubleClickEvent(self, event)
        pos = event.pos()
        item = self.indexAt(pos)
        if item:
            self.parent.editPhrase()



if __name__ == '__main__':  
    app = QtWidgets.QApplication([])
    dlg = PhraseUI() 
    dlg.show()   
    app.exec_() 
