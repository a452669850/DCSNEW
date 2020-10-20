from static.Png import *
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QLineEdit, QToolButton, QStyle


class SearchLineEdit(QLineEdit):
    """自定义的搜索框"""

    def __init__(self, parent=None):
        super(SearchLineEdit, self).__init__(parent)
        self.searchButtonPixmap = QtGui.QPixmap(':/static/1232043.png')
        self.searchButton = QToolButton(self)
        self.searchButton.setIcon(QtGui.QIcon(self.searchButtonPixmap))
        self.searchButton.setStyleSheet('border: 3px; padding: 3px;')
        self.searchButton.setCursor(QtCore.Qt.ArrowCursor)
        searchwith = self.style().pixelMetric(
            QStyle.PM_DefaultFrameWidth)

        searchButtonSize = self.searchButton.sizeHint()
        self.setMinimumSize(max(self.minimumSizeHint().width(), searchButtonSize.width() + searchwith * 2 + 2),
                            max(self.minimumSizeHint().height(), searchButtonSize.height() + searchwith * 2 + 2))

        self.clearButtonPixmap = QtGui.QPixmap(':/static/1209039.png')

        self.clearButton = QToolButton(self)
        self.clearButton.setIcon(QtGui.QIcon(self.clearButtonPixmap))
        self.clearButton.setStyleSheet('border: 0px; padding: 0px;')
        self.clearButton.setCursor(QtCore.Qt.ArrowCursor)

        frameWidth = self.style().pixelMetric(
            QStyle.PM_DefaultFrameWidth)

        clearButtonSize = self.clearButton.sizeHint()

        self.setMinimumSize(max(self.minimumSizeHint().width(), clearButtonSize.width() + frameWidth * 2 + 2),
                            max(self.minimumSizeHint().height(), clearButtonSize.height() + frameWidth * 2 + 2))

        self.setStyleSheet('''
                            QLineEdit{
                                border: 2px solid gray;
                                border-radius: 12px;
                                padding-right: %dpx;
                                padding-left: %dpx;
                            }
                           ''' % (clearButtonSize.width() + frameWidth + 2,
                                  searchButtonSize.width()
                                  )
                           )

        self.clearButton.setVisible(False)
        self.clearButton.clicked.connect(self.clearButtonClicked)

        self.textChanged.connect(self.__updateClearButton)

    def resizeEvent(self, event):
        buttonSize = self.clearButton.sizeHint()
        frameWidth = self.style().pixelMetric(
            QStyle.PM_DefaultFrameWidth)
        self.clearButton.move(self.rect().right() - frameWidth - buttonSize.width(),
                              (self.rect().bottom() - buttonSize.height() + 1) / 2)
        super(SearchLineEdit, self).resizeEvent(event)

    def __updateClearButton(self):
        self.clearButton.setVisible(bool(self.text()))

    def clearButtonClicked(self):
        self.clear()
