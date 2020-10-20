from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QListWidget, QStackedWidget
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QWidget


class AccountManagement(QWidget):
    '''左侧选项栏'''

    def __init__(self, lis_name, lis_win, lis_img, str):
        super(AccountManagement, self).__init__()
        self.resize(900, 600)
        self.setObjectName(str)
        self.lis_name = lis_name
        self.lis_win = lis_win
        self.lis_img = lis_img

        self.setFixedSize(self.width(), self.height())

        self.setWindowTitle(str)

        self.main_layout = QHBoxLayout(self, spacing=0)  # 窗口的整体布局
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.left_widget = QListWidget()  # 左侧选项列表
        self.main_layout.addWidget(self.left_widget)

        self.right_widget = QStackedWidget()
        self.main_layout.addWidget(self.right_widget)
        self.right_widget.currentChanged.connect(self.changeData)

        self._setup_ui()

    def _setup_ui(self):
        '''加载界面ui'''

        self.left_widget.currentRowChanged.connect(self.right_widget.setCurrentIndex)  # list和右侧窗口的index对应绑定

        self.left_widget.setFrameShape(QListWidget.NoFrame)  # 去掉边框

        self.left_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 隐藏滚动条
        self.left_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        for i in range(len(self.lis_name)):
            self.item = QListWidgetItem(
                QIcon(self.lis_img[i]),
                self.lis_name[i],
                self.left_widget
            )  # 左侧选项的添加
            self.item.setSizeHint(QSize(30, 60))
            self.item.setTextAlignment(Qt.AlignCenter)  # 居中显示
            self.right_widget.addWidget(self.lis_win[i])

    def changeData(self):
        win = self.right_widget.currentWidget()
        win.queryModel.datas = win.getTableValue()
        win.queryModel.layoutChanged.emit()
