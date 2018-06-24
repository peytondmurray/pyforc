from PyQt5 import QtWidgets, QtGui
import PyFORCGUIBase
import multiprocessing as mp
import worker
import plotting
import Forc
import MplWidget
import logging
import pathlib

# REMOVE LATER
# import matplotlib
# matplotlib.use('Qt5Agg')
# import matplotlib.pyplot as plt
#

# Icons:
# https://icons8.com/icon/11849/checkmark
# https://icons8.com/icon/set/hourglass/windows

log = logging.getLogger(__name__)


class PyFORCGUI(PyFORCGUIBase.Ui_MainWindow, QtWidgets.QMainWindow):

    def __init__(self, app):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self._setup_buttons()

        self._data = []
        self.current_job = 0

        # Set up thread which does work for the GUI behind the scenes
        log.info("Starting worker thread.")
        self.queued_jobs = mp.Queue()
        self.finished_jobs = mp.Queue()
        self.worker = worker.WorkerThread(input_queue=self.queued_jobs, output_queue=self.finished_jobs, parent=self)
        app.aboutToQuit.connect(self.worker.quit)
        self.worker.job_done.connect(self.update_status)
        self.worker.start()

        # Set up plots
        self.p_paths = MplWidget.MplWidget(self, toolbar_loc='bottom')
        self.l_paths.addWidget(self.p_paths)
        self.p_map = MplWidget.MplWidget(self, toolbar_loc='bottom')
        self.l_map.addWidget(self.p_map)
        self.p_map_in_paths = MplWidget.MplWidget(self, toolbar_loc='bottom')
        self.l_map_in_paths.addWidget(self.p_map_in_paths)

        self._initialize_plots()

        return

    def _initialize_plots(self):
        self.p_paths.axes.plot(list(), list(), '')
        self.p_map.axes.plot(list(), list(), '')
        self.p_map_in_paths.axes.plot(list(), list(), '')
        return

    def closeEvent(self, event):
        self.worker.quit()
        event.accept()
        return

    def _setup_buttons(self):
        self.b_import.clicked.connect(self.import_file)
        self.b_slope.clicked.connect(self.slope)
        self.b_normalize.clicked.connect(self.normalize)
        self.b_gauss.clicked.connect(self.gauss)
        self.b_forc.clicked.connect(self.compute_forc_distribution)

        self.b_paths.clicked.connect(self.plot_paths)
        self.b_major_loop.clicked.connect(self.plot_major_loop)
        self.b_data_points.clicked.connect(self.plot_data_points)

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

        self.b_level_moment.clicked.connect(self.plot_levels_moment)
        self.b_level_rho.clicked.connect(self.plot_levels_rho)
        self.b_level_rho_uncertainty.clicked.connect(self.plot_levels_rho_uncertainty)
        self.b_level_temperature.clicked.connect(self.plot_levels_temperature)

        self.b_map_curves_moment.clicked.connect(self.plot_curves_moment)
        self.b_map_curves_rho.clicked.connect(self.plot_curves_rho)
        self.b_map_curves_rho_uncertainty.clicked.connect(self.plot_curves_rho_uncertainty)
        self.b_map_curves_temperature.clicked.connect(self.plot_curves_temperature)

        self.b_undo.clicked.connect(self.undo)

        self._enable_plotting_buttons(False)

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
        if not self.f_auto_slope.isChecked():
            try:
                value = float(self.f_slope.text())
            except ValueError:
                QtWidgets.QMessageBox.Critical(self,
                                               'Warning',
                                               'Manual slope correction value must be a float!')
                return

            job = [self._data[-1].slope_correction, list(), {'value': value}]
            text = 'Slope correction: manual'

        else:
            if self.f_slope_h_sat.text() == '':
                job = [self._data[-1].slope_correction, list(), dict()]
                text = 'Slope correction: auto'

            else:
                try:
                    h_sat = float(self.f_slope_h_sat.text())
                except ValueError:
                    QtWidgets.QMessageBox.Critical(self,
                                                   'Warning',
                                                   'h_sat must be blank or float: {}'.format(self.f_slope_h_sat.text()))
                    return

                h_sat = self.f_slope_h_sat.text()
                job = [self._data[-1].slope_correction,
                       list(),
                       {'h_sat': None if self.f_slope_h_sat.text() else float(self.f_slope_h_sat.text())}]
                text = 'Slope correction: h_sat = {}'.format(h_sat)

        self.append_job(job=job, text=text)

        return

    def normalize(self):
        self.append_job(job=[self._data[-1].normalize,
                             list(),
                             {'method': 'minmax'}],
                        text='Normalize moment')
        return

    def gauss(self):
        raise NotImplementedError('Gaussian filtering not implemented')
        return

    def compute_forc_distribution(self):
        self.append_job(job=[self._data[-1].compute_forc_distribution,
                             list(),
                             {'sf': self.f_smoothing_factor.value(),
                              'method': 'savitzky-golay',
                              'extension': self.f_extension_type,
                              'n_fit_points': self.f_extension_n_fit_points.value()}],
                        text='Compute FORC distribution')
        return

    def plot_paths(self):
        plotting.h_vs_m(ax=self.p_paths.axes,
                        forc=self._data[-1],
                        mask=self.f_paths_mask.currentText(),
                        points=self.f_paths_points.currentText(),
                        cmap=self.f_paths_cmap.currentText())
        self.tabWidget.setCurrentIndex(0)
        return

    def plot_major_loop(self):
        plotting.major_loop(ax=self.p_paths.axes,
                            forc=self._data[-1],
                            color='k')
        self.tabWidget.setCurrentIndex(0)
        return

    def plot_data_points(self):
        plotting.plot_points(ax=self.p_map.axes,
                             forc=self._data[-1],
                             coordinates=self.coordinates())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_contours(self):
        plotting.contour_map(ax=self.p_map.axes,
                             forc=self._data[-1],
                             data_str='m',
                             mask=self.f_2d_mask.currentText(),
                             coordinates=self.coordinates(),
                             cmap=self.f_2d_cmap.text())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_hc_axis(self):
        plotting.hc_axis(ax=self.p_map.axes,
                         coordinates=self.coordinates())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_hb_axis(self):
        plotting.hb_axis(ax=self.p_map.axes,
                         coordinates=self.coordinates())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_h_axis(self):
        plotting.h_axis(ax=self.p_map.axes,
                        coordinates=self.coordinates())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_hr_axis(self):
        plotting.hr_axis(ax=self.p_map.axes,
                         coordinates=self.coordinates())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_heat_moment(self):
        plotting.heat_map(ax=self.p_map.axes,
                          forc=self._data[-1],
                          data_str='m',
                          mask=self.f_2d_mask.currentText(),
                          coordinates=self.coordinates(),
                          cmap=self.f_2d_cmap.text())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_heat_rho(self):
        plotting.heat_map(ax=self.p_map.axes,
                          forc=self._data[-1],
                          data_str='rho',
                          mask=self.f_2d_mask.currentText(),
                          coordinates=self.coordinates(),
                          cmap=self.f_2d_cmap.text())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_heat_rho_uncertainty(self):
        plotting.heat_map(ax=self.p_map.axes,
                          forc=self._data[-1],
                          data_str='rho_uncertainty',
                          mask=self.f_2d_mask.currentText(),
                          coordinates=self.coordinates(),
                          cmap=self.f_2d_cmap.text())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_heat_temperature(self):
        plotting.heat_map(ax=self.p_map.axes,
                          forc=self._data[-1],
                          data_str='t',
                          mask=self.f_2d_mask.currentText(),
                          coordinates=self.coordinates(),
                          cmap=self.f_2d_cmap.text())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_contour_moment(self):
        plotting.contour_map(ax=self.p_map.axes,
                             forc=self._data[-1],
                             data_str='m',
                             mask=self.f_2d_mask.currentText(),
                             coordinates=self.coordinates(),
                             cmap=self.f_2d_cmap.text())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_contour_rho(self):
        plotting.contour_map(ax=self.p_map.axes,
                             forc=self._data[-1],
                             data_str='rho',
                             mask=self.f_2d_mask.currentText(),
                             coordinates=self.coordinates(),
                             cmap=self.f_2d_cmap.text())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_contour_rho_uncertainty(self):
        plotting.contour_map(ax=self.p_map.axes,
                             forc=self._data[-1],
                             data_str='rho_uncertainty',
                             mask=self.f_2d_mask.currentText(),
                             coordinates=self.coordinates(),
                             cmap=self.f_2d_cmap.text())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_contour_temperature(self):
        plotting.contour_map(ax=self.p_map.axes,
                             forc=self._data[-1],
                             data_str='t',
                             mask=self.f_2d_mask.currentText(),
                             coordinates=self.coordinates(),
                             cmap=self.f_2d_cmap.text())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_levels_moment(self):
        plotting.contour_levels(ax=self.p_map.axes,
                                forc=self._data[-1],
                                data_str='m',
                                mask=self.f_2d_mask.currentText(),
                                coordinates=self.coordinates())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_levels_rho(self):
        plotting.contour_levels(ax=self.p_map.axes,
                                forc=self._data[-1],
                                data_str='rho',
                                mask=self.f_2d_mask.currentText(),
                                coordinates=self.coordinates())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_levels_rho_uncertainty(self):
        plotting.contour_levels(ax=self.p_map.axes,
                                forc=self._data[-1],
                                data_str='rho_uncertainty',
                                mask=self.f_2d_mask.currentText(),
                                coordinates=self.coordinates())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_levels_temperature(self):
        plotting.contour_levels(ax=self.p_map.axes,
                                forc=self._data[-1],
                                data_str='t',
                                mask=self.f_2d_mask.currentText(),
                                coordinates=self.coordinates())
        self.tabWidget.setCurrentIndex(1)
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
        del self._data[-1]
        self.d_jobs.takeItem(self.current_job)
        self.current_job -= 1
        return

    def is_job_running(self):
        return not self.queued_jobs.empty()

    def update_status(self):
        """Update display and data. Called when worker subprocess completes a job and emits a job_done signal.

        """
        result = self.finished_jobs.get()
        if isinstance(result, Forc.ForcBase):
            self._data.append(result)
            if len(self._data) > 0:
                self._enable_plotting_buttons(True)
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

    def coordinates(self):
        if self.f_hhr.isChecked():
            return 'hhr'
        else:
            return 'hchb'

    def _enable_plotting_buttons(self, b=True):
        self.b_paths.setEnabled(b)
        self.b_major_loop.setEnabled(b)
        self.b_data_points.setEnabled(b)

        self.b_hc_axis.setEnabled(b)
        self.b_hb_axis.setEnabled(b)
        self.b_h_axis.setEnabled(b)
        self.b_hr_axis.setEnabled(b)

        self.b_heat_moment.setEnabled(b)
        self.b_heat_rho.setEnabled(b)
        self.b_heat_rho_uncertainty.setEnabled(b)
        self.b_heat_temperature.setEnabled(b)

        self.b_contour_moment.setEnabled(b)
        self.b_contour_rho.setEnabled(b)
        self.b_contour_rho_uncertainty.setEnabled(b)
        self.b_contour_temperature.setEnabled(b)

        self.b_level_moment.setEnabled(b)
        self.b_level_rho.setEnabled(b)
        self.b_level_rho_uncertainty.setEnabled(b)
        self.b_level_temperature.setEnabled(b)

        self.b_map_curves_moment.setEnabled(b)
        self.b_map_curves_rho.setEnabled(b)
        self.b_map_curves_rho_uncertainty.setEnabled(b)
        self.b_map_curves_temperature.setEnabled(b)

        return
