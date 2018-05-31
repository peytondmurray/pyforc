# from multiprocessing import Process
from PyQt5 import QtCore, QtWidgets, QtGui, QThread


# class Worker(QtCore.QObject, Process):

#     job_done = QtCore.pyqtSignal()

#     def __init__(self, parent_gui, input_queue):
#         QtCore.QObject.__init__(self)
#         Process.__init__(self)

#         self.input_queue = input_queue
#         return

#     def run(self):
#         while True:
#             job = self.input_queue.get()
#             if job == 'CLOSE':
#                 break
#             else:
#                 job[0](*job[1])
#                 self.job_done.emit()


class Worker():

    def __init__(self, input_queue):
        self.input_queue = input_queue
        return

    def get_tasks(self):
        while True:
            task = self.input_queue.get()
            if task == "DONE":
                break
            else:
                task[0](*task[1], **task[2])
        return
