import queue
import typing

from PyQt5.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant

que1 = queue.LifoQueue()


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
        from RealtimeDB import iomapping
        if not QModelIndex.isValid():
            print("行或者列有问题")
            return QVariant()
        if role != Qt.DisplayRole:
            return QVariant()
        if role == Qt.DisplayRole:
            if QModelIndex.column() == 5:
                que1.put(self.datas[QModelIndex.row()][1])
                return QVariant(iomapping.mem.read(iomapping.read(self.datas[QModelIndex.row()][1])))
            else:
                return QVariant(self.datas[QModelIndex.row()][QModelIndex.column()])

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> typing.Any:
        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:
            return self.header[section]
