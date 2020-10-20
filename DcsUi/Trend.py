# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Trend.ui'
#
# Created by: PyQt5 UI code generator 5.12
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
import numpy as np
import sys
import openpyxl


class TrendUi(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(TrendUi, self).__init__(parent)
        self.setupUi()

    def setupUi(self):
        self.setObjectName("Form")
        self.resize(1037, 669)
        wb = openpyxl.load_workbook('TEST.xlsx')
        ws = wb.active
        self.dic = {}
        for row in list(ws.iter_rows())[2:]:
            l = [x.value for x in row]
            self.dic[l[1]] = l[4:6]
        self.gridLayout = QtWidgets.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")

       

        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")

        self.comboBox = QtWidgets.QComboBox(self)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.currentIndexChanged.connect(self.selectionchange)
        self.horizontalLayout_3.addWidget(self.comboBox)

        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_3.addWidget(self.lineEdit)
        self.pushButton = QtWidgets.QPushButton(self)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_3.addWidget(self.pushButton)
        self.horizontalLayout_3.setStretch(0, 2)
        self.horizontalLayout_3.setStretch(1, 5)
        self.horizontalLayout_3.setStretch(2, 1)
        self.gridLayout.addLayout(self.horizontalLayout_3, 1, 1, 1, 1)
        self.listWidget = QtWidgets.QListWidget(self)
        self.listWidget.setObjectName("listWidget")
        self.gridLayout.addWidget(self.listWidget, 2, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 3)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 0, 0, 1, 2)
        self.label = QtWidgets.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 1)
        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 2)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)
        self.plotTrend()
        self.addVar()
        self.addData()

    def plotTrend(self):
        if 1:
            tick_y = [str(x) for x in range(0,21)]
        else:
            tick_y = ['0','0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9','1.0']
        # tick_x = ['2019/11/28','2019/11/29','2019/11/30','2019/11/31', '2019/11/32', '2019/11/33']
        tick_x = [str(x) + '\n1' for x in range(500)]
        tick_x_list = self.getList(len(tick_x))
        tick_y_list = self.getList(len(tick_y))
        ticks_x = [(i,j) for i, j in zip(tick_x_list, tick_x)]
        ticks_y = [(i,j) for i, j in zip(tick_y_list, tick_y)]
        ticks_y_dict = {}
        x_Axis = pg.AxisItem(orientation='bottom')
        y_Axis = pg.AxisItem(orientation='left')
        x_Axis.setTicks([ticks_x])
        y_Axis.setTicks([ticks_y])
        self.trendWidget = pg.PlotWidget(title = f'{1}趋势图', axisItems = {'bottom' : x_Axis, 'left' : y_Axis})
        self.gridLayout.addWidget(self.trendWidget, 2, 1, 1, 1)
        x = np.array([x/10 for x in range(500)], dtype=np.float_)
        # y = np.array([4,5,6], dtype=np.float_)
        # self.trendWidget.plot(y, pen = 'r')
        self.trendWidget.plot(x, pen = 'r')

    def addVar(self):
        self.listWidget.addItems(['1','2','3'])

    def addData(self):
        self.comboBox.addItems(['1','2','3'])

    def selectionchange(self):
        print(self.comboBox.currentText())

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Form", "趋势图"))
        self.pushButton.setText(_translate("Form", "搜索"))
        self.label.setText(_translate("Form", "变量点"))

    def getList(self, length):
        l = [0]
        n = 0
        for x in range(length):
            n += 2
            l.append(n)
        return l

    def getValues(self):
        index = 0   
        with open('demo.txt',"rb") as f: 
            for fLine in f: 
                print(fLine)
                index += 1
        if index/2 <= 500:
            xAxisNumber = index
        else:
            xAxisNumber = getXAxisNumber(index)
            

    def getXAxisNumber(self, index):
        xAxisNumber = 0
        interval = 0
        if index // 500 == 0:
            interval = index/500
        else:
            interval = index//500 + 1
        xAxisNumberSet = {x for x in list(range(index, interval))}



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    form = TrendUi()
    form.show()
    app.exec_()
