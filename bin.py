import sys, os
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from DcsUi.InitProject import Ui_InitProject
from DcsUi.LogWindow import LogWindow
from PyQt5 import QtWidgets
from static.Stylesheets.ImportQss import load_stylesheet_pyqt5

if __name__ == '__main__':
    sys.excepthook = LogWindow.errorLog # 初始化日志记录系统
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = Ui_InitProject()
    app.setStyleSheet(load_stylesheet_pyqt5(style="style_Classic")) # 设置窗口Qss样式
    mainWindow.show()
    sys.exit(app.exec_())
