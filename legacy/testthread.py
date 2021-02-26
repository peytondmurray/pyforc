from PyQt5 import QtCore, QtWidgets
from itertools import count, islice


class Threaded(QtCore.QObject):
    result = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

    def start(self):
        print("Thread started")

    def calculatePrime(self, n):
        primes = (n for n in count(2) if all(n % d for d in range(2, n)))
        self.result.emit(list(islice(primes, 0, n))[-1])


class GUI(QtWidgets.QWidget):
    requestPrime = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        self._thread = QtCore.QThread()
        self._threaded = Threaded(result=self.displayPrime)
        self.requestPrime.connect(self._threaded.calculatePrime)
        self._thread.started.connect(self._threaded.start)
        self._threaded.moveToThread(self._thread)
        QtWidgets.qApp.aboutToQuit.connect(self._thread.quit)
        self._thread.start()

        l = QtWidgets.QVBoxLayout(self)
        self._iterationLE = QtWidgets.QLineEdit(self, placeholderText="Iteration (n)")
        self._requestBtn = QtWidgets.QPushButton("Calculate Prime", self, clicked=self.primeRequested)
        self._busy = QtWidgets.QProgressBar(self)
        self._resultLbl = QtWidgets.QLabel("Result:", self)
        l.addWidget(self._iterationLE)
        l.addWidget(self._requestBtn)
        l.addWidget(self._busy)
        l.addWidget(self._resultLbl)
        return

    def primeRequested(self):
        try:
            n = int(self._iterationLE.text())
        except:
            return
        self.requestPrime.emit(n)
        self._busy.setRange(0, 0)
        self._iterationLE.setEnabled(False)
        self._requestBtn.setEnabled(False)
        return

    def displayPrime(self, prime):
        self._resultLbl.setText("Result: {}".format(prime))
        self._busy.setRange(0, 100)
        self._iterationLE.setEnabled(True)
        self._requestBtn.setEnabled(True)
        return

if __name__ == "__main__":
    from sys import exit, argv

    a = QtWidgets.QApplication(argv)
    g = GUI()
    g.show()
    exit(a.exec_())
