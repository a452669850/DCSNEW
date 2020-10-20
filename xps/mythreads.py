from PyQt5.QtCore import QThread, pyqtSignal

from utils.core import MainWindowConfig
from xps.ExploreTable import que


class mythread(QThread):
    sinOut = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.working = True
        self.data = False
        self.sinOut.connect(self.close_break)

    def __del__(self):
        self.working = False
        self.wait()

    def run(self) -> None:
        while True:
            if self.data:
                self.exec_()
            name = que.get()
            MainWindowConfig.IOMapping.setcurrent(name)

    def close_break(self):
        self.data = True

# from PyQt5.QtCore import QRunnable, QThreadPool, QThread, pyqtSignal
#
# from utils.core import MainWindowConfig
# # from xps.ExploreTable import stack
# from xps.ExploreTable import que
#
# StopEvent = object()
#
#
# class Thread(QRunnable):
#
#     def __init(self):
#         super(Thread, self).__init__()
#
#     def run(self) -> None:
#         name = que.get()
#             # name = stack.pop()
#         MainWindowConfig.IOMapping.setcurrent(name)
#         # except Exception:
#         #     pass
#
#
# class ThreadPool(object):
#
#     def __init__(self, thread_count, communicate):
#         super(ThreadPool, self).__init__()
#         self.thread_count = thread_count
#         self.communicate = communicate
#         self.state = False
#
#         self.pool = QThreadPool()  # 创建线程池
#         self.pool.globalInstance()
#
#         self.communicate.connect(self.thread_stop)
#
#     def thread_stop(self):
#         self.pool.clear()
#         self.state = True
#
#     def start(self):
#         self.pool.setMaxThreadCount(self.thread_count)
#         while True:
#             if self.state:
#                 break
#             thread_ins = Thread()
#             thread_ins.setAutoDelete(True)
#             self.pool.start(thread_ins)
#         self.pool.waitForDone()  # 等待线程结束
#
#
# class TasksThread(QThread):
#     sinOut = pyqtSignal(str)
#
#     def __init__(self, thread_count=20):
#         super(TasksThread, self).__init__()
#         self.thread_count = thread_count
#
#         self.thread = ThreadPool(thread_count=self.thread_count, communicate=self.sinOut)
#
#     def run(self) -> None:
#         self.thread.start()
