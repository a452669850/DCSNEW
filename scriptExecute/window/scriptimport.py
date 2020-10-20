import sys
from pathlib import Path

from PyQt5.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QPushButton, QApplication, \
    QSplitter, QTableView, QHBoxLayout

from scriptExecute.toLead.parse.xlsx import scan
from scriptExecute.window.importwind import importWindow
from scriptExecute.window.runwindow import ScriptWindow
from scriptExecute.window.tree.scripttree import TreeGroup
from utils.ClientModels import Script
from xps.ExploreTable import myTableModel


class scriptImprort(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.resize(750, 600)
        self.setFixedSize(self.width(), self.height())
        self.setWindowTitle('脚本')

        self.UI_init()

    def UI_init(self):
        self.createTreeGroup()
        self.createGroup()
        self.btn_import = QPushButton('导入脚本')
        self.btn_import.clicked.connect(self.script_import)
        h_layout = QHBoxLayout()
        g_layout = QHBoxLayout()
        v_layout = QVBoxLayout()
        h_layout.addWidget(QSplitter())
        h_layout.addWidget(self.btn_import)
        g_layout.addWidget(self.treegroup)
        g_layout.addWidget(self.group)
        v_layout.addLayout(h_layout)
        v_layout.addLayout(g_layout)
        self.setLayout(v_layout)

    def createTreeGroup(self):
        self.treegroup = TreeGroup()
        self.treegroup.tree_Signal.connect(self.windowAction)

    def createGroup(self):
        self.group = QGroupBox('配置')
        self.btn_renovate = QPushButton('刷新')
        self.btn_renovate.clicked.connect(self.renovate)
        self.btn_setup = QPushButton('设置')
        self.btn_setup.clicked.connect(self.setup)
        self.table = QTableView()

        self.querymodel = myTableModel(['信号名', '时间', '计时', '触发沿'], [])
        self.table.setModel(self.querymodel)
        h_layout = QHBoxLayout()
        v_layout = QVBoxLayout()
        h_layout.addWidget(QSplitter())
        h_layout.addWidget(self.btn_renovate)
        h_layout.addWidget(self.btn_setup)
        v_layout.addLayout(h_layout)
        v_layout.addWidget(self.table)
        self.group.setLayout(v_layout)

    def script_import(self):
        self.win = importWindow()
        self.win.my_sin.connect(self.action_sx)
        self.win.show()

    def renovate(self):
        pass

    def setup(self):
        pass

    def windowAction(self, text):
        pass

    def action_sx(self):
        self.treegroup.refreshTree()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = scriptImprort()
    demo.show()
    sys.exit(app.exec_())
