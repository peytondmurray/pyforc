
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MplWidget(QtWidgets.QWidget):
    """This class allows matplotlib figures to be embedded in PyQt5 GUIs. Instantiate this widget once when the GUI
    is started.
    
    Parameters
    ----------
    parent : QtWidgets.QWidget
        Parent widget where the MplWidget should be drawn.
    
    toolbar_loc : str
        Location of toolbar. Can be 'top' or 'bottom'.
    
    """

    def __init__(self, parent=None, toolbar_loc='bottom'):
        super().__init__(parent=parent)
        self.sublayout = QtWidgets.QVBoxLayout(self)
        self.fig = Figure()
        self.axes = self.fig.add_subplot(111)
        self.figurecanvas = FigureCanvas(self.fig)

        if toolbar_loc == 'bottom':
            self.sublayout.addWidget(self.figurecanvas)
            self.sublayout.addWidget(NavigationToolbar(self.figurecanvas, self))
        elif toolbar_loc == 'top':
            self.sublayout.addWidget(NavigationToolbar(self.figurecanvas, self))
            self.sublayout.addWidget(self.figurecanvas)
        else:
            raise ValueError('Invalid toolbar location: {}'.format(toolbar_loc))

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.updateGeometry()
        return
