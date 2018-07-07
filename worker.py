from PyQt5 import QtCore, QtWidgets, QtGui


class WorkerThread(QtCore.QThread):

    job_done = QtCore.pyqtSignal()

    def __init__(self, input_queue, output_queue, parent=None):
        super().__init__(parent=parent)
        self.running = False
        self.input_queue = input_queue
        self.output_queue = output_queue
        return

    def compute(self):
        function, args, kwargs = self.input_queue.get()
        if args is None:
            while not self.output_queue.empty():
                pass
            self.output_queue.put(function(self.parent().get_latest_data(), **kwargs))
        else:
            self.output_queue.put(function(*args, **kwargs))
        self.job_done.emit()
        return

    def run(self):
        self.running = True
        while self.running:
            self.compute()
        return

    # def wait_for_data(self):
    #     if output_queue