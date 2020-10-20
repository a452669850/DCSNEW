import typing

from PyQt5.QtCore import QAbstractTableModel, QVariant, Qt, QModelIndex
from PyQt5.QtGui import QBrush, QColor


class tableModel(QAbstractTableModel):
    def __init__(self, header, data: list):
        QAbstractTableModel.__init__(self)
        self.datas = data
        self.header = header
        self.start = [[None for j in i] for i in self.datas]

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
        elif role == Qt.BackgroundColorRole:
            if QModelIndex.column() != 0 and self.start[QModelIndex.row()][QModelIndex.column()] == False:
                return QBrush(QColor(Qt.red))
            elif QModelIndex.column() != 0 and self.start[QModelIndex.row()][QModelIndex.column()] == True:
                return QBrush(QColor(Qt.green))
            else:
                return QBrush(QColor(Qt.white))
        elif role != Qt.DisplayRole:
            return QVariant()
        return QVariant(self.datas[QModelIndex.row()][QModelIndex.column()])

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.header[section]

    def updataStart(self):
        self.start = [[None for j in i] for i in self.datas]
        self.layoutChanged.emit()


class jgTableModel(QAbstractTableModel):
    def __init__(self, header, data: list):
        QAbstractTableModel.__init__(self)
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
