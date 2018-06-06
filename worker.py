from PyQt5 import QtCore, QtWidgets, QtGui


class WorkerThread(QtCore.QThread):

    def __init__(self, input_queue, output_queue, parent=None):
        super().__init__(parent=parent)
        # super(WorkerThread, self).__init__(self, parent=parent)
        self.running = False
        self.input_queue = input_queue
        self.output_queue = output_queue
        return

    def get_tasks(self):
        self.running = True
        while self.running:
            function, args, kwargs = self.input_queue.get()
            self.output_queue.put(function(*args, **kwargs))
            self.finished.emit()
        return

    def stop(self):
        self.running = False
        return
