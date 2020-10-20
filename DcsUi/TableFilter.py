#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QTabWidget, QDockWidget, QTableView, QHeaderView, QTableWidget, QMessageBox, QAbstractItemView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush
from PyQt5.QtCore import Qt
from DcsUi.DockCLass import NewDockWidget
from DcsUi.variablecoercion.model import variableGroupModel
from DcsUi.variablecoercion.smallWindow import mySearchWindow
from xps.ExploreTable import smallTableModel
from utils import core

class VarDockWidget(NewDockWidget):
    def __init__(self, title, parent=None):
        NewDockWidget.__init__(self, title, parent=parent)
        self.varTab = QTabWidget()
        self.varTab.setTabsClosable(True)
        self.varTab.tabCloseRequested.connect(self.closeTab)
        self.parent = parent

    # def addVar(self, group):
    #     if group:
    #         self.TabelView = VarTabelView(group[1])
    #         self.varTab.addTab (self.TabelView, group[1])
    #         self.setWidget(self.varTab)

    def addVar(self, group):
        if group:
            self.TabelView = mySearchWindow()
            group_points = variableGroupModel.selectGroupData(name = group[1])
            self.TabelView.queryModel.datas = group_points
            self.varTab.addTab(self.TabelView, group[1])
            self.setWidget(self.varTab)

    def closeTab(self, index):
        self.varTab.removeTab(index)

class VarTabelView(QTableView):
    def __init__(self, group):
        QTableView.__init__(self)
        self.date = {
            'header': core.MainWindowConfig.header,
            'date':[]
        }
        self.horizontalHeader().setStretchLastSection(True)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.queryModel = smallTableModel(self.date['header'],self.date['date'])
        group_points = variableGroupModel.selectGroupData(name = group)
        self.queryModel.datas = group_points
        self.queryModel.layoutChanged.emit()
        self.setModel(self.queryModel)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.customContextMenuRequested.connect(self.showContextMenu)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        # self.searchButtonClicked()


class myWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(myWindow, self).__init__(parent)
        self.centralwidget  = QtWidgets.QWidget(self)
        self.lineEdit       = QtWidgets.QLineEdit(self.centralwidget)
        self.view           = QtWidgets.QTableView(self.centralwidget)

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.view, 1, 0, 1, 3)
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.setCentralWidget(self.centralwidget)

        self.model = QtGui.QStandardItemModel(self)

        for rowName in range(3 * 5):
            self.model.invisibleRootItem().appendRow(
                [   QtGui.QStandardItem("row {0} col 1".format(rowName))    
                    for column in range(3)
                    ]
                )

        self.proxy = QtCore.QSortFilterProxyModel(self)
        self.proxy.setSourceModel(self.model)

        self.view.setModel(self.proxy)

        # self.comboBox.currentIndexChanged.connect(self.on_comboBox_currentIndexChanged)

        self.horizontalHeader = self.view.horizontalHeader()
        self.horizontalHeader.sectionClicked.connect(self.on_view_horizontalHeader_sectionClicked)

    @QtCore.pyqtSlot(int)
    def on_view_horizontalHeader_sectionClicked(self, logicalIndex):
        self.logicalIndex = logicalIndex
        self.on_comboBox_currentIndexChanged(self.logicalIndex)
        menuName = '_' + str(logicalIndex) + 'Menu'
        if not hasattr(self, menuName):
            setattr(self, menuName, QtWidgets.QMenu(self))
            self.menuValues = getattr(self, menuName)
            menuEdit = QtWidgets.QLineEdit()
            inputAction = QtWidgets.QWidgetAction(self.menuValues)
            inputAction.setDefaultWidget(menuEdit)
            self.menuValues.addAction(inputAction)
            menuEdit.textChanged.connect(self.on_lineEdit_textChanged)

        self.menuValues = getattr(self, menuName)
        self.romoveAction(self.menuValues)  

        self.signalMapper = QtCore.QSignalMapper(self)  
        self.menuValues.mouseReleaseEvent = self._menu_mouseReleaseEvent

        actionAll = QtWidgets.QAction("All", self)
        actionAll.triggered.connect(self.on_actionAll_triggered)
        actionAll.setProperty('canHide', True)
        actionAll.setCheckable(True)
        self.menuValues.addAction(actionAll)
        self.menuValues.addSeparator()

        valuesUnique = [self.proxy.data(self.proxy.index(row, self.logicalIndex))
                            for row in range(self.proxy.rowCount())
                            ]
        for actionNumber, actionName in enumerate(sorted(list(set(valuesUnique)))):              
            action = QtWidgets.QAction(actionName, self)
            self.signalMapper.setMapping(action, actionNumber)  
            action.triggered.connect(self.signalMapper.map) 
            action.setCheckable(True) 
            self.menuValues.addAction(action)

        self.signalMapper.mapped.connect(self.on_signalMapper_mapped)  

        headerPos = self.view.mapToGlobal(self.horizontalHeader.pos())        

        posY = headerPos.y() + self.horizontalHeader.height()
        posX = headerPos.x() + self.horizontalHeader.sectionPosition(self.logicalIndex)
        getattr(self, menuName).exec_(QtCore.QPoint(posX, posY))

    @QtCore.pyqtSlot()
    def on_actionAll_triggered(self):
    	# 显示全部
        filterColumn = self.logicalIndex
        filterString = QtCore.QRegExp(  "",
                                        QtCore.Qt.CaseInsensitive,
                                        QtCore.QRegExp.RegExp
                                        )

        self.proxy.setFilterRegExp(filterString)
        self.proxy.setFilterKeyColumn(filterColumn)

    @QtCore.pyqtSlot(int)
    def on_signalMapper_mapped(self, i):
        # stringAction = self.signalMapper.mapping(i).text()
        stringActions = '|'.join([x.text() for x in getattr(self, '_' + str(self.logicalIndex) + 'Menu').actions() if x.isChecked()])
        filterColumn = self.logicalIndex
        print(stringActions)
        filterString = QtCore.QRegExp(  stringActions,
                                        QtCore.Qt.CaseSensitive,
                                        # QtCore.QRegExp.FixedString
                                        )
        self.proxy.setFilterRegExp(filterString)
        self.proxy.setFilterKeyColumn(filterColumn)

    @QtCore.pyqtSlot(str)
    def on_lineEdit_textChanged(self, text):
        # 搜索框文字变化函数
        search = QtCore.QRegExp(    text,
                                    QtCore.Qt.CaseInsensitive,
                                    QtCore.QRegExp.RegExp
                                    )

        self.proxy.setFilterRegExp(search)

    @QtCore.pyqtSlot(int)
    def on_comboBox_currentIndexChanged(self, index):
        self.proxy.setFilterKeyColumn(index)

    def _menu_mouseReleaseEvent(self, event):
        action = self.menuValues.actionAt(event.pos())
        if not action:
            # 没有找到action就交给QMenu自己处理
            return QtWidgets.QMenu.mouseReleaseEvent(self.menuValues, event)
        if action.property('canHide'):  # 如果有该属性则给菜单自己处理
            return QtWidgets.QMenu.mouseReleaseEvent(self.menuValues, event)
        # 找到了QAction则只触发Action
        action.activate(action.Trigger)

    def romoveAction(self, menu):
    	# 删除输入框之外的按钮1
        for action in menu.actions():
            if type(action) != QtWidgets.QWidgetAction:
                menu.removeAction(action)

    # def _checkAction(self):
    #     # 三个action都响应该函数
    #     self.labelInfo.setText('\n'.join(['{}\t选中：{}'.format(
    #         action.text(), action.isChecked()) for action in self.menuValues.actions()]))

if __name__ == "__main__":
    import sys
    app  = QtWidgets.QApplication(sys.argv)
    main = myWindow()
    main.show()
    main.resize(400, 600)
    sys.exit(app.exec_())