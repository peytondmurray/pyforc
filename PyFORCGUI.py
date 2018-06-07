from PyQt5 import QtWidgets, QtGui
import PyFORCGUIBase
import multiprocessing as mp
import worker
import plotting
import Forc
import logging
import pathlib

# REMOVE LATER
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
#

# Icons:
# https://icons8.com/icon/11849/checkmark
# https://icons8.com/icon/set/hourglass/windows

log = logging.getLogger(__name__)


# Example of aboutToQuit siganl for stopping QThread: https://gist.github.com/metalman/10721983

class PyFORCGUI(PyFORCGUIBase.Ui_MainWindow, QtWidgets.QMainWindow):

    def __init__(self, app):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self._setup_buttons()

        self._data = []
        self.current_job = 0

        log.info("Starting worker thread.")
        self.queued_jobs = mp.Queue()
        self.finished_jobs = mp.Queue()
        self.worker = worker.WorkerThread(input_queue=self.queued_jobs, output_queue=self.finished_jobs, parent=self)
        app.aboutToQuit.connect(self.worker.stop)
        self.worker.finished.connect(self.update_status)
        self.worker.start()

        return

    def closeEvent(self, event):
        self.worker.stop()
        event.accept()
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

    def _add_queue_item(self, job, label):
        """Puts a job into the jobs queue, and adds a corresponding item with loading icon to the jobs display widget.
        """
        self.d_jobs.addItem(QtWidgets.QListWidgetItem(icon=QtWidgets.QIcon('plz_wait.png'),
                                                      text=label))
        self.jobs.put(job)
        return

    def import_file(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose a data file:', './test_data/')[0]
        if pathlib.Path(path).is_file():
            self.append_job(job=[Forc.PMCForc,
                                 list(),
                                 {'path': path,
                                  'step': None if self.f_step_auto.isChecked() else self.f_step_manual.value(),
                                  'method': self.f_dataset_interpolation_type.currentText(),
                                  'drift': self.f_drift.isChecked(),
                                  'radius': self.f_drift_radius.value(),
                                  'density': self.f_drift_density.value()}],
                            text='Imported: {}'.format(path))
        else:
            self.statusBar().showMessage('No file found: {}'.format(path))
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
        _, ax = plt.subplots(1, 1)
        plotting.h_vs_m(ax=ax,
                        forc=self._data[-1],
                        mask=self.f_paths_mask.currentText(),
                        points=self.f_paths_points.currentText(),
                        cmap=self.f_paths_cmap.currentText())
        plt.show()
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
        _, ax = plt.subplots(1, 1)
        plotting.m_hhr(ax=ax,
                       forc=self._data[-1],
                       mask=self.f_2d_mask.currentText(),
                       cmap=self.f_2d_cmap.text())
        plt.show()
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

    def update_status(self):
        """Update display and data. Called when worker subprocess completes a job and emits a job_done signal.

        """
        result = self.finished_jobs.get()
        if isinstance(result, Forc.ForcBase):
            self._data.append(result)
        self.d_jobs.item(self.current_job).setIcon(QtGui.QIcon('./checkmark.png'))
        self.current_job += 1
        return

    def append_job(self, job, text):
        self.queued_jobs.put(job)
        item = QtWidgets.QListWidgetItem(text)
        item.setToolTip(text)
        item.setIcon(QtGui.QIcon('./hourglass.png'))
        self.d_jobs.addItem(item)
        return
