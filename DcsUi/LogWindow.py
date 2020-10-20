import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import logging
from logging import handlers
import traceback


class QPlainTextEditLogger(logging.Handler):
    '''日志记录类'''
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class LogWindow(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__()
        if parent.__class__.__name__ == 'VariableSettingsUi':
            return
        logging.basicConfig(level=logging.DEBUG,#控制台打印的日志级别
                    format= '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                    )
        log_fmt = '%(asctime)s\tFile \"%(filename)s\",line %(lineno)s\t%(levelname)s: %(message)s'
        formatter = logging.Formatter(log_fmt)
        fh = handlers.TimedRotatingFileHandler(filename=f'{parent.projectPath}\\log\\DcsLog.log',when="D",interval=1,backupCount=15)
        fh.suffix = "%Y-%m-%d_%H-%M.log"
        fh.setFormatter(formatter)
        logTextBox = QPlainTextEditLogger(self)
     # 控制日志输出信息
        logTextBox.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(logTextBox)
        logging.getLogger().addHandler(fh)
     # 控制日志记录等级
        logging.getLogger().setLevel(logging.INFO)

        layout = QtWidgets.QVBoxLayout()
     
        layout.addWidget(logTextBox.widget)
        self.setLayout(layout)
        self.resize(800, 600)

    @classmethod
    def errorLog(etype, value, tb):
        error_msg = ''.join(traceback.format_exception(etype, value, tb))
        logging.error(error_msg)

    def infoLog(self, info):
        logging.info(info)

    def warningLog(self, warning):
        logging.warning(warning)

    def closeEvent(self, event):
        self.hide()

if __name__ == '__main__':
    app = None
    if (not QtWidgets.QApplication.instance()):
        app = QtWidgets.QApplication([])
    dlg = LogWindow()
    dlg.show()
    dlg.raise_()
    if (app):
        app.exec_()