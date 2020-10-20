#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtCore import Qt, QSize, QRect, QPoint
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtGui import QColor, QPixmap, QDrag, QPainter, QCursor
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QLabel, QRubberBand
from utils.ClientModels import Classification
import json

class DropListWidget(QListWidget):
    # 可以拖进来的QListWidget

    def __init__(self, *args, **kwargs):
        super(DropListWidget, self).__init__(*args, **kwargs)
        self.resize(400, 400)
        self.setAcceptDrops(True)
        # 设置从左到右、自动换行、依次排列
        self.setFlow(self.LeftToRight)
        self.setWrapping(True)
        self.setResizeMode(self.Adjust)
        # item的间隔
        self.setSpacing(5)

        self.setContextMenuPolicy(3)
        self.customContextMenuRequested[QPoint].connect(self.rightMenuShow)
        # self.customContextMenuRequested[QPoint].connect(self.delete)

    def rightMenuShow(self):
        # list的右键菜单
        rightMenu = QMenu(self)
        removeAction = QAction(u"删除", self, triggered=self.delete)       # triggered 为右键菜单点击后的激活事件。
        rightMenu.addAction(removeAction)
        rightMenu.exec_(QCursor.pos())

    def delete(self):
        # 右键菜单中的删除当前分组中的规程/用例/用例组事件
        # pro为规程类型 case为用例类型 group为用例组类型
        # self.pos = QCursor.pos()
        # print(self.pos)
        # print(self.pos.x(),self.pos.y())
        item =  self.currentItem()
        # print(item)
        if self.type == 'pro': # 判断list中盛放的信息种类
            clas = Classification.get_by_name(self.parent.chooseBox.currentText()) # 根据组名获取当前组的数据库对象
            if clas.procedures and clas.procedures != 'null':
                pros = json.loads(clas.procedures) # 数据库中存放的信息列表均为json类型
                pros.remove(self.itemWidget(item).text())
                clas.procedures = json.dumps(list(set(pros)))
            else:
                return
            clas.save()
        elif self.type == 'case':
            clas = Classification.get_by_name(self.parent.chooseBox.currentText())
            if clas.usecases and clas.usecases != 'null':
                cases = json.loads(clas.usecases)
                cases.remove(self.itemWidget(item).text())
                clas.usecases = json.dumps(list(set(cases)))
            else:
                return
            clas.save()
        elif self.type == 'group':
            clas = Classification.get_by_name(self.parent.chooseBox.currentText())
            if clas.usecasegroup and clas.usecasegroup != 'null':
                groups = json.loads(clas.usecasegroup)
                groups.remove(self.itemWidget(item).text())
                clas.usecasegroup = json.dumps(list(set(groups)))
            else:
                return
            clas.save()
        self.removeItemWidget(self.takeItem(self.row(item)))


    def makeItem(self, cname):
        # 响应拖拽时间后为当前list中添加item
        size = QSize(100, 100)
        item = QListWidgetItem(self)
        # item.setData(Qt.UserRole + 1, cname)  # 把颜色放进自定义的data里面
        item.setSizeHint(size)
        label = QLabel(self)  # 自定义控件
        # label.setMargin(2)  # 往内缩进2
        # label.resize(size)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignTop)
        # pixmap = QPixmap(size.scaled(96, 96, Qt.IgnoreAspectRatio))  # 调整尺寸
        # pixmap.fill(QColor(cname))
        # label.setPixmap(pixmap)
        label.setText(cname) # 信息使用label存放
        self.setItemWidget(item, label)

    def dragEnterEvent(self, event):
        mimeData = event.mimeData()
        if not mimeData.property('myItems'):
            event.ignore()
        else:
            event.acceptProposedAction()

    def dropEvent(self, event):
        # 获取拖放的items
        if self.parent.chooseBox.currentText():
            items = event.mimeData().property('myItems')
            event.accept()
            for item in items:
                # 取出item里的data并生成item
                if item.listWidget().type == self.type:
                    if self.type == 'pro':
                        clas = Classification.get_by_name(self.parent.chooseBox.currentText())
                        if clas.procedures and clas.procedures != 'null':
                            pros = json.loads(clas.procedures)
                            pros.append(item.data(Qt.UserRole + 1))
                            clas.procedures = json.dumps(list(set(pros)))
                        else:
                            clas.procedures = json.dumps([item.data(Qt.UserRole + 1)])
                        clas.save()
                    elif self.type == 'case':
                        clas = Classification.get_by_name(self.parent.chooseBox.currentText())
                        if clas.usecases and clas.usecases != 'null':
                            cases = json.loads(clas.usecases)
                            cases.append(item.data(Qt.UserRole + 1))
                            clas.usecases = json.dumps(list(set(cases)))
                        else:
                            clas.usecases = json.dumps([item.data(Qt.UserRole + 1)])
                        clas.save()
                    elif self.type == 'group':
                        clas = Classification.get_by_name(self.parent.chooseBox.currentText())
                        if clas.usecasegroup and clas.usecasegroup != 'null':
                            groups = json.loads(clas.usecasegroup)
                            groups.append(item.data(Qt.UserRole + 1))
                            clas.usecasegroup = json.dumps(list(set(groups)))
                        else:
                            clas.usecasegroup = json.dumps([item.data(Qt.UserRole + 1)])
                        clas.save()

                    nitem = self.count()
                    nodes = []
                    for i in range(nitem):
                        nodes.append(self.itemWidget(self.item(i)).text())
                    if item.data(Qt.UserRole + 1) not in nodes:
                        self.makeItem(item.data(Qt.UserRole + 1))


class DragListWidget(QListWidget):
    # 可以往外拖的QListWidget

    def __init__(self, *args, **kwargs):
        super(DragListWidget, self).__init__(*args, **kwargs)
        # self.resize(400, 400)
        # 隐藏横向滚动条
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 不能编辑
        self.setEditTriggers(self.NoEditTriggers)
        # 开启拖功能
        self.setDragEnabled(True)
        # 只能往外拖
        self.setDragDropMode(self.DragOnly)
        # 忽略放
        self.setDefaultDropAction(Qt.IgnoreAction)
        # ****重要的一句（作用是可以单选，多选。Ctrl、Shift多选，可从空白位置框选）****
        # ****不能用ExtendedSelection,因为它可以在选中item后继续框选会和拖拽冲突****
        self.setSelectionMode(self.ContiguousSelection)
        # 设置从左到右、自动换行、依次排列
        self.setFlow(self.LeftToRight)
        self.setWrapping(True)
        self.setResizeMode(self.Adjust)
        # item的间隔
        self.setSpacing(5)
        # 橡皮筋(用于框选效果)
        self._rubberPos = None
        self._rubberBand = QRubberBand(QRubberBand.Rectangle, self)

        # self.initItems()

    # 实现拖拽的时候预览效果图
    # 这里演示拼接所有的item截图(也可以自己写算法实现堆叠效果)
    def startDrag(self, supportedActions):
        items = self.selectedItems()
        drag = QDrag(self)
        mimeData = self.mimeData(items)
        # 由于QMimeData只能设置image、urls、str、bytes等等不方便
        # 这里添加一个额外的属性直接把item放进去,后面可以根据item取出数据
        mimeData.setProperty('myItems', items)
        drag.setMimeData(mimeData)
        pixmap = QPixmap(self.viewport().visibleRegion().boundingRect().size())
        pixmap.fill(Qt.transparent)
        painter = QPainter()
        painter.begin(pixmap)
        for item in items:
            rect = self.visualRect(self.indexFromItem(item))
            painter.drawPixmap(rect, self.viewport().grab(rect))
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(self.viewport().mapFromGlobal(QCursor.pos()))
        drag.exec_(supportedActions)

    def mousePressEvent(self, event):
        # 列表框点击事件,用于设置框选工具的开始位置
        super(DragListWidget, self).mousePressEvent(event)
        if event.buttons() != Qt.LeftButton or self.itemAt(event.pos()):
            return
        self._rubberPos = event.pos()
        self._rubberBand.setGeometry(QRect(self._rubberPos, QSize()))
        self._rubberBand.show()

    def mouseReleaseEvent(self, event):
        # 列表框点击释放事件,用于隐藏框选工具
        super(DragListWidget, self).mouseReleaseEvent(event)
        self._rubberPos = None
        self._rubberBand.hide()

    def mouseMoveEvent(self, event):
        # 列表框鼠标移动事件,用于设置框选工具的矩形范围
        super(DragListWidget, self).mouseMoveEvent(event)
        if self._rubberPos:
            pos = event.pos()
            lx, ly = self._rubberPos.x(), self._rubberPos.y()
            rx, ry = pos.x(), pos.y()
            size = QSize(abs(rx - lx), abs(ry - ly))
            self._rubberBand.setGeometry(
                QRect(QPoint(min(lx, rx), min(ly, ry)), size))

    def makeItem(self, cname):
        size = QSize(100, 100)
        item = QListWidgetItem(self)
        item.setData(Qt.UserRole + 1, cname)  # 把颜色放进自定义的data里面
        item.setSizeHint(size)
        label = QLabel(self)  # 自定义控件
        label.setMargin(2)  # 往内缩进2
        # label.resize(size)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignTop)
        # pixmap = QPixmap(size.scaled(96, 96, Qt.IgnoreAspectRatio))  # 调整尺寸
        # pixmap.fill(QColor(cname))
        # label.setPixmap(pixmap)
        label.setText(cname)
        self.setItemWidget(item, label)

    def initItems(self):
        size = QSize(100, 100)
        for cname in QColor.colorNames():
            self.makeItem(size, cname)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    # app.setStyleSheet("""QListWidget {
    #     outline: 0px;
    #     background-color: transparent;
    # }
    # QListWidget::item:selected {
    #     border-radius: 2px;
    #     border: 1px solid rgb(0, 170, 255);
    # }
    # QListWidget::item:selected:!active {
    #     border-radius: 2px;
    #     border: 1px solid transparent;
    # }
    # QListWidget::item:selected:active {
    #     border-radius: 2px;
    #     border: 1px solid rgb(0, 170, 255);
    # }
    # QListWidget::item:hover {

    #     border-radius: 2px;
    #     border: 1px solid rgb(0, 170, 255);
    # }"""
    #                   )
    wa = DragListWidget()
    wa.show()
    wo = DropListWidget()
    wo.show()
    sys.exit(app.exec_())