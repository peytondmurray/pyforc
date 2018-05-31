from PyQt5 import QtCore, QtWidgets, QtGui


class WorkerThread(QtCore.QThread):

    def __init__(self, input_queue, parent=None):
        super(WorkerThread, self).__init__(self, parent=parent)
        self.input_queue = input_queue
        return

    def get_tasks(self):
        while True:
            task = self.input_queue.get()
            if task == "DONE":
                break
            else:
                function, *args, **kwargs = task
                function(*args, **kwargs)
                self.
        return
