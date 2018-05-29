import multiprocessing
import PyQt5.QtCore

class Worker(multiprocessing.Process, PyQt5.QtCore.QObject):

    job_done = PyQt5.QtCore.pyqtBoundSignal()

    def __init__(self, parent, job_queue):
        multiprocessing.Process.__init__(self)

        self.job_queue = job_queue
        self.parent = parent

        return

    def run(self):
        while True:
            job = self.job_queue.get()
            if job == 'DONE':
                break
            else:
                job[0](*job[1])
                self.job_done.emit()
