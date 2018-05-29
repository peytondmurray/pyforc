from PyQt5 import QtWidgets
import PyFORCGUIBase


class PyFORCGUI(PyFORCGUIBase.Ui_MainWindow, QtWidgets.QMainWindow, object):

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self._setup_buttons()
        return

    def _setup_buttons(self):
        self.b_import.clicked.connect(self.import_file)
        self.b_slope.clicked.connect(self.slope)
        self.b_normalize.clicked.connect(self.normalize)
        self.b_offset.clicked.connect(self.offset)
        self.b_gauss.clicked.connect(self.gauss)
        self.b_forc.clicked.connect(self.forc)

        self.b_paths.clicked.connect(self.plot_paths)
        self.b_major_loop.clicked.connect(self.plot_major_loop)
        self.b_data_points.clicked.connect(self.plot_data_points)
        self.b_contours.clicked.connect(self.plot_contours)

        self.b_hc_axis.clicked.connect(self.plot_hc_axis)
        self.b_hb_axis.clicked.connect(self.plot_hb_axis)
        self.b_h_axis.clicked.connect(self.plot_h_axis)
        self.b_hr_axis.clicked.connect(self.plot_hr_axis)

        self.b_heat_moment.clicked.connect(self.plot_heat_moment)
        self.b_heat_rho.clicked.connect(self.plot_heat_rho)
        self.b_heat_rho_uncertainty.clicked.connect(self.plot_heat_rho_uncertainty)
        self.b_heat_temperature.clicked.connect(self.plot_heat_temperature)

        self.b_contour_moment.clicked.connect(self.plot_contour_moment)
        self.b_contour_rho.clicked.connect(self.plot_contour_rho)
        self.b_contour_rho_uncertainty.clicked.connect(self.plot_contour_rho_uncertainty)
        self.b_contour_temperature.clicked.connect(self.plot_contour_temperature)

        self.b_map_curves_moment.clicked.connect(self.plot_curves_moment)
        self.b_map_curves_rho.clicked.connect(self.plot_curves_rho)
        self.b_map_curves_rho_uncertainty.clicked.connect(self.plot_curves_rho_uncertainty)
        self.b_map_curves_temperature.clicked.connect(self.plot_curves_temperature)

        self.b_undo.clicked.connect(self.undo)

        return

    def _update_extension_widgets(self, current_text):
        self.f_extension_n_fit_points.setEnabled(current_text == 'slope')
        return

    def _setup_widget_triggers(self):

        self.f_extension_type.currentTextChanged.connect(self._update_extension_widgets)
        return

    def import_file(self):
        return

    def slope(self):
        return

    def normalize(self):
        return

    def offset(self):
        return

    def gauss(self):
        return

    def forc(self):
        return

    def plot_paths(self):
        return

    def plot_major_loop(self):
        return

    def plot_data_points(self):
        return

    def plot_contours(self):
        return

    def plot_hc_axis(self):
        return

    def plot_hb_axis(self):
        return

    def plot_h_axis(self):
        return

    def plot_hr_axis(self):
        return

    def plot_heat_moment(self):
        return

    def plot_heat_rho(self):
        return

    def plot_heat_rho_uncertainty(self):
        return

    def plot_heat_temperature(self):
        return

    def plot_contour_moment(self):
        return

    def plot_contour_rho(self):
        return

    def plot_contour_rho_uncertainty(self):
        return

    def plot_contour_temperature(self):
        return

    def plot_curves_moment(self):
        return

    def plot_curves_rho(self):
        return

    def plot_curves_rho_uncertainty(self):
        return

    def plot_curves_temperature(self):
        return

    def undo(self):
        return