from PyQt5 import QtCore, QtWidgets, QtGui


class WorkerThread(QtCore.QThread):

    job_done = QtCore.pyqtSignal()

    def __init__(self, input_queue, output_queue, parent=None):
        super().__init__(parent=parent)
        # super(WorkerThread, self).__init__(self, parent=parent)
        self.running = False
        self.input_queue = input_queue
        self.output_queue = output_queue
        return

    def compute(self):
        function, args, kwargs = self.input_queue.get()
        self.output_queue.put(function(*args, **kwargs))
        return

    def run(self):
        self.running = True
        while self.running:
            self.compute()
            self.job_done.emit()
        return
