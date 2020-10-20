"""
采样器进程
"""
import queue
import threading
import time

from Agreement.SM.skio import exception
from Agreement.SM.skio.define import LOGGER


class SampleThread(threading.Thread):
    def __init__(self, state):
        threading.Thread.__init__(self, daemon=True)
        self.queue = queue.Queue()
        self.state = state

    def run(self) -> None:
        while True:
            task = self.queue.get()
            if hasattr(task, 'fetch') and callable(task.fetch):
                try:
                    task.fetch(self.state)
                except exception.SkError as e:
                    LOGGER.exception(e)
                    time.sleep(.1)
                time.sleep(.1)
                self.queue.put(task)
