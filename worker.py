from PyQt5 import QtCore, QtWidgets, QtGui


class WorkerThread(QtCore.QThread):

    job_done = QtCore.pyqtSignal()

    def __init__(self, input_queue, data_queue, parent=None):
        super().__init__(parent=parent)
        self.running = False
        self.input_queue = input_queue
        self.data_queue = data_queue
        self._data = []
        self.parent().send_latest_data.connect(self.queue_latest_data)
        return

    def compute(self):
        function, args, kwargs = self.input_queue.get()
        if args is None:
            self._data.append(function(self._data[-1], **kwargs))
        else:
            self._data.append(function(*args, **kwargs))
        self.job_done.emit()
        return

    def run(self):
        self.running = True
        while self.running:
            self.compute()
        self.running = False
        return

    def queue_latest_data(self):
        self.data_queue.put(self._data[-1])
        return

    def get_n_data(self):
        return len(self._data)

    def undo(self):
        del self._data[-1]
        return
