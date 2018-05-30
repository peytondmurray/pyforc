from multiprocessing import Process
from PyQt5 import QtCore, QtWidgets, QtGui


class Worker(Process, QtCore.QObject):

    job_done = QtCore.pyqtSignal()

    def __init__(self, parent_gui, job_queue):
        QtCore.QObject.__init__(self)
        Process.__init__(self)

        self.job_queue = job_queue
        self.parent_gui = parent_gui

        return

    def run(self):
        while True:
            job = self.job_queue.get()
            if job == 'CLOSE':
                break
            else:
                job[0](*job[1])
                self.job_done.emit()
