import queue
import typing

from PyQt5 import QtCore
from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant, QAbstractListModel
from PyQt5.QtGui import QColor, QBrush

# from xps.myStack import Stack

# stack = Stack()

que = queue.LifoQueue()
que1 = queue.LifoQueue()


class myTableModel(QAbstractTableModel):
    def __init__(self, header, data: list):
        QAbstractTableModel.__init__(self, parent=None)
        self.datas = data
        self.header = header

    def append_data(self, x):
        self.datas.append(x)
        self.layoutChanged.emit()

    def remove_row(self, row):
        self.datas.pop(row)
        self.layoutChanged.emit()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if len(self.datas) > 0:
            return len(self.datas)
        return 0

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self.header)

    def get_data(self):
        return self

    def data(self, QModelIndex, role=None):
        if not QModelIndex.isValid():
            print("行或者列有问题")
            return QVariant()
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.datas[QModelIndex.row()][QModelIndex.column()])

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.header[section]


class checkModel(myTableModel):
    def __init__(self, header, data):
        myTableModel.__init__(self, header, data)

    def data(self, QModelIndex, role=None):
        if not QModelIndex.isValid():
            print("行或者列有问题")
            return QVariant()
        if role == Qt.BackgroundColorRole:
            if QModelIndex.row() == self.datas[QModelIndex.row()][0] - 1 and self.datas[QModelIndex.row()][-1] == True:
                return QBrush(QColor(Qt.green))
            if QModelIndex.row() == self.datas[QModelIndex.row()][0] - 1 and self.datas[QModelIndex.row()][-1] == False:
                return QBrush(QColor(Qt.red))
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.datas[QModelIndex.row()][QModelIndex.column()])


class MyModel(myTableModel):
    def __init__(self, header, data: list):
        myTableModel.__init__(self, header, data)
        self.checkList = ['Unchecked'] * len(self.datas)
        self.supportedDragActions()

    def data(self, index, role):
        row = index.row()
        col = index.column()
        if role == Qt.DisplayRole:
            return QVariant(self.datas[row][col])
        elif role == Qt.CheckStateRole:
            if col == 0:
                return Qt.Checked if self.checkList[row] == 'Checked' else Qt.Unchecked
        return QVariant()

    def setData(self, index, value, role):
        row = index.row()
        col = index.column()
        if role == Qt.CheckStateRole and col == 0:
            self.checkList[row] = 'Checked' if value == Qt.Checked else 'Unchecked'
        return True

    def flags(self, index):
        if index.isValid():
            return Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsUserCheckable
        return Qt.ItemIsDropEnabled | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerClick(self, isOn):
        self.beginResetModel()
        if isOn:
            self.checkList = ['Checked'] * len(self.datas)
        else:
            self.checkList = ['Unchecked'] * len(self.datas)
        self.endResetModel()

    def dragMoveEvent(self, event):
        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()

    def moveRow(self, sourceParent: QModelIndex, sourceRow: int, destinationParent: QModelIndex,
                destinationChild: int) -> bool:
        if self.datas[destinationChild] == self.datas[sourceRow]:
            return
        self.datas[sourceRow], self.datas[destinationChild] = self.datas[destinationChild], self.datas[sourceRow]
        self.layoutChanged.emit()


class smallTableModel(QAbstractTableModel):
    err = QtCore.pyqtSignal(str)

    def __init__(self, header, data):
        QAbstractTableModel.__init__(self, parent=None)
        self.datas = data
        self.header = header

    def remove_row(self, row):
        self.datas.pop(row)
        self.layoutChanged.emit()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if len(self.datas) > 0:
            return len(self.datas)
        return 0

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self.header)

    def get_data(self):
        return self

    def data(self, QModelIndex, role=None):
        from utils.core import MainWindowConfig
        if not QModelIndex.isValid():
            print("行或者列有问题")
            return QVariant()
        if role == Qt.BackgroundColorRole:
            if QModelIndex.column() == 0 and self.datas[QModelIndex.row()]['force_value'] != None:
                return QBrush(QColor(Qt.red))
        if role != Qt.DisplayRole:
            return QVariant()
        if role == Qt.DisplayRole:
            if QModelIndex.column() == 1:
                que.put(self.datas[QModelIndex.row()]['sig_name'])
                # stack.push(self.datas[QModelIndex.row()]['sig_name'])
                return QVariant(MainWindowConfig.IOMapping.current_value[self.datas[QModelIndex.row()]['sig_name']])
            else:
                return QVariant(self.datas[QModelIndex.row()][self.header[QModelIndex.column()][0]])

    def setData(self, index: QModelIndex, value: typing.Any, role: int = ...) -> bool:
        from utils.core import MainWindowConfig
        row = index.row()
        col = index.column()
        if value != '':
            self.datas[row][self.header[col][0]] = value
            try:
                MainWindowConfig.IOMapping.setforce(self.datas[row]['sig_name'], value)
            except Exception as e:
                MainWindowConfig.IOMapping.dumpforce(self.datas[row]['sig_name'])
                self.err.emit('%s' % e)
            self.statas = True
        else:
            self.statas = False
        return True

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if index.column() == 0:
            if str(self.datas[index.row()]['reg'])[0] != '4':
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
            else:
                return Qt.ItemIsEnabled | Qt.ItemIsSelectable
        if index.column() != 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.header[section][1]

        if orientation == Qt.Vertical:
            return section + 1


class listViewModel(QAbstractListModel):

    def __init__(self, query):
        super().__init__()
        self.ListItemDate = []
        self.data_init(query)

    def data_init(self, query):
        for point in query:
            ItemData = {'name': ''}
            ItemData['name'] = point.sig_name
            ItemData['data'] = point
            self.ListItemDate.append(ItemData)

    def data(self, index: QModelIndex, role: int = ...) -> typing.Any:
        if index.isValid() or (0 <= index.row() < len(self.ListItemData)):
            if role == Qt.DisplayRole:
                return QVariant(self.ListItemDate[index.row()]['name'])
            elif role == Qt.TextAlignmentRole:
                return QVariant(int(Qt.AlignLeft | Qt.AlignVCenter))
        else:
            return QVariant()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.ListItemDate)

    def addItem(self, itemData):
        if itemData:
            self.ListItemDate.append(itemData)
        self.layoutChanged.emit()

    def deleteItem(self, index):
        self.ListItemDate.pop(index)
        self.layoutChanged.emit()

    def updataItem(self, lis):
        self.ListItemDate = lis
        self.layoutChanged.emit()

    def getItem(self, index):
        if index > -1 and index < len(self.ListItemData):
            return self.ListItemData[index]


class variableModel(QAbstractTableModel):

    def __init__(self, header, data: list):
        QAbstractTableModel.__init__(self, parent=None)
        self.datas = data
        self.header = header

    def append_data(self, x):
        self.datas.append(x)
        self.layoutChanged.emit()

    def remove_row(self, row):
        self.datas.pop(row)
        self.layoutChanged.emit()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if len(self.datas) > 0:
            return len(self.datas)
        return 0

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self.header)

    def get_data(self):
        return self

    def data(self, QModelIndex, role=None):
        from communication import iomapping
        if not QModelIndex.isValid():
            print("行或者列有问题")
            return QVariant()
        if role != Qt.DisplayRole:
            return QVariant()
        if role == Qt.DisplayRole:
            if QModelIndex.column() == 5:
                que1.put(self.datas[QModelIndex.row()][1])
                return QVariant(iomapping.current_value[self.datas[QModelIndex.row()][1]])
            else:
                return QVariant(self.datas[QModelIndex.row()][QModelIndex.column()])

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.header[section]
