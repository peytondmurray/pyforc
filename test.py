import sys
import time

import numpy as np

from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
# from matplotlib.figure import Figure

import MplWidget

class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self._main = QtWidgets.QWidget()
        self.setCentralWidget(self._main)
        layout = QtWidgets.QVBoxLayout(self._main)

        static_widget = MplWidget.MplWidget(self)
        layout.addWidget(static_widget)

        # static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        # layout.addWidget(static_canvas)
        # self.addToolBar(NavigationToolbar(static_canvas, self))

        # dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
        # layout.addWidget(dynamic_canvas)
        # self.addToolBar(QtCore.Qt.BottomToolBarArea,
        #                 NavigationToolbar(dynamic_canvas, self))
        dynamic_widget = MplWidget.MplWidget(self)
        layout.addWidget(dynamic_widget)


        # self._static_ax = static_canvas.figure.subplots()
        self._static_ax = static_widget.axes
        t = np.linspace(0, 10, 501)
        self._static_ax.plot(t, np.tan(t), ".")

        # self._dynamic_ax = dynamic_canvas.figure.subplots()
        self._dynamic_ax = dynamic_widget.axes
        self._dynamic_ax.set_xlim(0, 10)
        self._dynamic_ax.set_ylim(-1.1, 1.1)
        self._dynamic_line = self._dynamic_ax.plot([], [], '')[0]
        self._timer = dynamic_widget.new_timer(1, [(self._update_canvas, (), {})])
        # self._timer = dynamic_canvas.new_timer(1, [(self._update_canvas, (), {})])
        self._timer.start()

    def _update_canvas(self):
        t = np.linspace(0, 10, 101)
        self._dynamic_line.set_xdata(t)
        self._dynamic_line.set_ydata(np.sin(t + time.time()))
        self._dynamic_ax.figure.canvas.draw()


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow()
    app.show()
    qapp.exec_()