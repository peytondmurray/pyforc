from PyQt5 import QtWidgets, QtGui, QtCore
import PyFORCGUIBase
import QFileDialogExtended
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

    send_latest_data = QtCore.pyqtSignal()

    def __init__(self, app):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self._setup_buttons()

        self.current_job = 0

        # Set up thread which does work for the GUI behind the scenes
        log.info("Starting worker thread.")
        self.queued_jobs = mp.Queue()
        self.data_queue = mp.Queue()
        self.worker = worker.WorkerThread(input_queue=self.queued_jobs, data_queue=self.data_queue, parent=self)
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
        """Initialize the plots after the MplWidgets are first instantiated. This draws temporary axes, etc.
        
        """

        self.p_paths.axes.plot(list(), list(), '')
        self.p_map.axes.plot(list(), list(), '')
        self.p_map_in_paths.axes.plot(list(), list(), '')
        return

    def closeEvent(self, event):
        """Stops the worker thread and quits the application. PyQt5 QThread documentation says to avoid using
        terminate(), but I get a 'QThread destroyed' error if I don't terminate - and the application hangs
        if I try to use QThread.quit() and QThread.wait(). This function should never be called directly by the user.

        Parameters
        ----------
        event : QEvent
            A QCloseEvent is passed in when the 'x' button is clicked to close PyFORC.
        """

        self.worker.terminate()
        event.accept()
        return

    def _setup_buttons(self):
        """Connects the signals all the buttons to the corresponding slots for processing and displaying data.
        
        """

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

        self.b_export_csv.clicked.connect(self.export_csv)
        self.b_export_vtk.clicked.connect(self.export_vtk)
        self.b_export_pmc.clicked.connect(self.export_pmc)

        self.b_undo.clicked.connect(self.undo)

        return

    def _update_extension_widgets(self, current_text):
        """Enables or disables the widget which allows the user to input the number of points to use to fit the slope
        for dataset extension. The widget is enabled if the user selects 'slope' for the type of dataset extension.

        """

        self.f_extension_n_fit_points.setEnabled(current_text == 'slope')
        return

    def _setup_widget_triggers(self):
        """Some of the widgets need have special triggers. Setup this functionality here.
        
        """

        self.f_extension_type.currentTextChanged.connect(self._update_extension_widgets)
        return

    def import_file(self):
        """Imports a (PMC-formatted) dataset from disk.
        
        """

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
        """Carry out a slope correction on the dataset; this removes a linear background.
        
        """

        if not self.f_auto_slope.isChecked():
            try:
                value = float(self.f_slope.text())
            except ValueError:
                QtWidgets.QMessageBox.Critical(self,
                                               'Warning',
                                               'Manual slope correction value must be a float!')
                return

            job = [Forc.PMCForc.slope_correction, None, {'value': value}]
            text = 'Slope correction: manual'

        else:
            if self.f_slope_h_sat.text() == '':
                job = [Forc.PMCForc.slope_correction, None, dict()]
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
                job = [Forc.PMCForc.slope_correction,
                       None,
                       {'h_sat': None if self.f_slope_h_sat.text() else float(self.f_slope_h_sat.text())}]
                text = 'Slope correction: h_sat = {}'.format(h_sat)

        self.append_job(job=job, text=text)

        return

    def normalize(self):
        """Normalize the dataset so that the min and max of the moment is at -1 and +1, respectively.
        
        """

        self.append_job(job=[Forc.PMCForc.normalize,
                             None,
                             {'method': 'minmax'}],
                        text='Normalize moment')
        return

    def gauss(self):
        """Pass a gaussian filter over the dataset for smoothing.
        
        """

        raise NotImplementedError('Gaussian filtering not implemented')

    def compute_forc_distribution(self):
        """Compute the FORC distribution. The computation is usually short, as it only requires a convolution, but is
        still done in the worker thread for speed.
        
        """

        self.append_job(job=[Forc.PMCForc.compute_forc_distribution,
                             None,
                             {'sf': self.f_smoothing_factor.value(),
                              'method': 'savitzky-golay',
                              'extension': self.f_extension_type.currentText(),
                              'n_fit_points': self.f_extension_n_fit_points.value()}],
                        text='Compute FORC distribution')
        return

    def plot_paths(self):
        """Plot the FORC dataset in (H, M) space.
        
        """

        self.send_latest_data.emit()
        plotting.h_vs_m(ax=self.p_paths.axes,
                        forc=self.data_queue.get(),
                        mask=self.f_paths_mask.currentText(),
                        points=self.f_paths_points.currentText(),
                        cmap=self.f_paths_cmap.currentText())
        self.tabWidget.setCurrentIndex(0)
        return

    def plot_major_loop(self):
        """Plot the major loop.
        
        """

        self.send_latest_data.emit()
        plotting.major_loop(ax=self.p_paths.axes,
                            forc=self.data_queue.get(),
                            color='k')
        self.tabWidget.setCurrentIndex(0)
        return

    def plot_data_points(self):
        """Plot the location of the data points in (H, Hr) or (Hc, Hb) space.
        
        """

        self.send_latest_data.emit()
        plotting.plot_points(ax=self.p_map.axes,
                             forc=self.data_queue.get(),
                             coordinates=self.coordinates())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_hc_axis(self):
        """Add Hc-axis to the current 2D plot.

        """

        plotting.hc_axis(ax=self.p_map.axes, coordinates=self.coordinates())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_hb_axis(self):
        """Add Hb-axis to the current 2D plot.

        """

        plotting.hb_axis(ax=self.p_map.axes, coordinates=self.coordinates())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_h_axis(self):
        """Add H-axis to the current 2D plot.

        """

        plotting.h_axis(ax=self.p_map.axes, coordinates=self.coordinates())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_hr_axis(self):
        """Add Hr-axis to the current 2D plot.

        """

        plotting.hr_axis(ax=self.p_map.axes, coordinates=self.coordinates())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_heat_moment(self):
        """Plot the moment as a heat map in (H, Hr) or (Hc, Hb) space.

        """

        self.send_latest_data.emit()
        plotting.heat_map(ax=self.p_map.axes,
                          forc=self.data_queue.get(),
                          data_str='m',
                          mask=self.f_2d_mask.currentText(),
                          coordinates=self.coordinates(),
                          cmap=self.f_2d_cmap.text())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_heat_rho(self):
        """Plot the FORC distribution as a heat map in (H, Hr) or (Hc, Hb) space.
        
        """

        self.send_latest_data.emit()
        plotting.heat_map(ax=self.p_map.axes,
                          forc=self.data_queue.get(),
                          data_str='rho',
                          mask=self.f_2d_mask.currentText(),
                          coordinates=self.coordinates(),
                          cmap=self.f_2d_cmap.text())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_heat_rho_uncertainty(self):
        """Plot the FORC distribution uncertainty as a heat map in (H, Hr) or (Hc, Hb) space.
        
        """

        self.send_latest_data.emit()
        plotting.heat_map(ax=self.p_map.axes,
                          forc=self.data_queue.get(),
                          data_str='rho_uncertainty',
                          mask=self.f_2d_mask.currentText(),
                          coordinates=self.coordinates(),
                          cmap=self.f_2d_cmap.text())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_heat_temperature(self):
        """Plot the measurement temperature as a heat map in (H, Hr) or (Hc, Hb) space.
        
        """

        self.send_latest_data.emit()
        plotting.heat_map(ax=self.p_map.axes,
                          forc=self.data_queue.get(),
                          data_str='temperature',
                          mask=self.f_2d_mask.currentText(),
                          coordinates=self.coordinates(),
                          cmap=self.f_2d_cmap.text())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_contour_moment(self):
        """Plot the moment as a contour map in (H, Hr) or (Hc, Hb) space.
        
        """

        self.send_latest_data.emit()
        plotting.contour_map(ax=self.p_map.axes,
                             forc=self.data_queue.get(),
                             data_str='m',
                             mask=self.f_2d_mask.currentText(),
                             coordinates=self.coordinates(),
                             cmap=self.f_2d_cmap.text())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_contour_rho(self):
        """Plot the FORC distribution as a contour map in (H, Hr) or (Hc, Hb) space.
        
        """

        self.send_latest_data.emit()
        plotting.contour_map(ax=self.p_map.axes,
                             forc=self.data_queue.get(),
                             data_str='rho',
                             mask=self.f_2d_mask.currentText(),
                             coordinates=self.coordinates(),
                             cmap=self.f_2d_cmap.text())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_contour_rho_uncertainty(self):
        """Plot the FORC distribution uncertainty as a contour map in (H, Hr) or (Hc, Hb) space.
        
        """

        self.send_latest_data.emit()
        plotting.contour_map(ax=self.p_map.axes,
                             forc=self.data_queue.get(),
                             data_str='rho_uncertainty',
                             mask=self.f_2d_mask.currentText(),
                             coordinates=self.coordinates(),
                             cmap=self.f_2d_cmap.text())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_contour_temperature(self):
        """Plot the measurement temperature as a contour map in (H, Hr) or (Hc, Hb) space.
        
        """

        self.send_latest_data.emit()
        plotting.contour_map(ax=self.p_map.axes,
                             forc=self.data_queue.get(),
                             data_str='temperature',
                             mask=self.f_2d_mask.currentText(),
                             coordinates=self.coordinates(),
                             cmap=self.f_2d_cmap.text())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_levels_moment(self):
        """Plot the moment as contour levels in (H, Hr) or (Hc, Hb) space.
        
        """

        self.send_latest_data.emit()
        plotting.contour_levels(ax=self.p_map.axes,
                                forc=self.data_queue.get(),
                                data_str='m',
                                mask=self.f_2d_mask.currentText(),
                                coordinates=self.coordinates())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_levels_rho(self):
        """Plot the FORC distribution as contour levels in (H, Hr) or (Hc, Hb) space.
        
        """

        self.send_latest_data.emit()
        plotting.contour_levels(ax=self.p_map.axes,
                                forc=self.data_queue.get(),
                                data_str='rho',
                                mask=self.f_2d_mask.currentText(),
                                coordinates=self.coordinates())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_levels_rho_uncertainty(self):
        """Plot the FORC distribution uncertainty as contour levels in (H, Hr) or (Hc, Hb) space.
        
        """
        
        self.send_latest_data.emit()
        plotting.contour_levels(ax=self.p_map.axes,
                                forc=self.data_queue.get(),
                                data_str='rho_uncertainty',
                                mask=self.f_2d_mask.currentText(),
                                coordinates=self.coordinates())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_levels_temperature(self):
        """Plot the measurement temperature as contour levels in (H, Hr) or (Hc, Hb) space.
        
        """

        self.send_latest_data.emit()
        plotting.contour_levels(ax=self.p_map.axes,
                                forc=self.data_queue.get(),
                                data_str='temperature',
                                mask=self.f_2d_mask.currentText(),
                                coordinates=self.coordinates())
        self.tabWidget.setCurrentIndex(1)
        return

    def plot_curves_moment(self):
        """Plot the moment as a gouraud-shaded colormap into the reversal curves.
        
        """

        self.send_latest_data.emit()
        plotting.map_into_curves(ax=self.p_map_in_paths.axes,
                                 forc=self.data_queue.get(),
                                 data_str='m',
                                 mask=self.f_2d_mask.currentText(),
                                 interpolation=None)
        self.tabWidget.setCurrentIndex(2)
        return

    def plot_curves_rho(self):
        """Plot the FORC distribution as a gouraud-shaded colormap into the reversal curves.
        
        """

        self.send_latest_data.emit()
        plotting.map_into_curves(ax=self.p_map_in_paths.axes,
                                 forc=self.data_queue.get(),
                                 data_str='rho',
                                 mask=self.f_2d_mask.currentText(),
                                 interpolation=None)
        self.tabWidget.setCurrentIndex(2)
        return

    def plot_curves_rho_uncertainty(self):
        """Plot the FORC distribution uncertainty as a gouraud-shaded colormap into the reversal curves.
        
        """

        self.send_latest_data.emit()
        plotting.map_into_curves(ax=self.p_map_in_paths.axes,
                                 forc=self.data_queue.get(),
                                 data_str='rho_uncertainty',
                                 mask=self.f_2d_mask.currentText(),
                                 interpolation=None)
        self.tabWidget.setCurrentIndex(2)
        return

    def plot_curves_temperature(self):
        """Plot the measurement temperature as a gouraud-shaded colormap into the reversal curves.
        
        """

        self.send_latest_data.emit()
        plotting.map_into_curves(ax=self.p_map_in_paths.axes,
                                 forc=self.data_queue.get(),
                                 data_str='temperature',
                                 mask=self.f_2d_mask.currentText(),
                                 interpolation=None)
        self.tabWidget.setCurrentIndex(2)
        return

    def undo(self):
        """Undoes the last computation.

        """

        if self.d_jobs.count() > 0:
            self.worker.undo()
            self.d_jobs.takeItem(self.d_jobs.count()-1)
            self.current_job -= 1
        return

    def is_job_running(self):
        """Check whether a computation is currently running or not.

        Returns
        -------
        bool
            True if there are no queued jobs, otherwise False.
        """

        return not self.queued_jobs.empty()

    def update_status(self):
        """Update display and data. Called when worker subprocess completes a job and emits a job_done signal.

        """
        self._enable_plotting_buttons()
        self.d_jobs.item(self.current_job).setIcon(QtGui.QIcon('./checkmark.png'))
        self.current_job += 1
        return

    def append_job(self, job, text):
        """Appends a task to the job queue, which will be executed by the worker thread as soon as it is ready. Each
        time a task is appended to the job queue, an item is added to the list of computations shown in the GUI, so
        that the user can keep track of which computations have been done on the dataset.

        Parameters
        ----------
        job : List
            Each job is a list containing three objects:
                1. The function which contains the work to be done in the worker thread
                2. Arguments to be passed to the function
                3. A dict of kwargs to be passed to the function

            If the second item in the list is None, the worker thread simply takes the most recently processed FORC
            data and passes it to the function.
        text : str
            String to put in the list of computations shown in the GUI

        """

        self.queued_jobs.put(job)
        item = QtWidgets.QListWidgetItem(text)
        item.setToolTip(text)
        item.setIcon(QtGui.QIcon('./hourglass.png'))
        self.d_jobs.addItem(item)
        return

    def coordinates(self):
        """Get currently selected coordinates.
        
        Returns
        -------
        str
            'hhr' or 'hchb'
        """

        if self.f_hhr.isChecked():
            return 'hhr'
        else:
            return 'hchb'

    def _enable_plotting_buttons(self):
        """Enables or disables plotting buttons, depending on whether data is available to be plot. This prevents
        users from trying to plot data they don't have.
        
        """

        self.send_latest_data.emit()
        data = self.data_queue.get()

        self.b_paths.setEnabled(data.has_m())
        self.b_major_loop.setEnabled(data.has_m())
        self.b_data_points.setEnabled(data.has_m())

        self.b_hc_axis.setEnabled(data.has_m())
        self.b_hb_axis.setEnabled(data.has_m())
        self.b_h_axis.setEnabled(data.has_m())
        self.b_hr_axis.setEnabled(data.has_m())

        self.b_heat_moment.setEnabled(data.has_m())
        self.b_heat_rho.setEnabled(data.has_rho())
        self.b_heat_rho_uncertainty.setEnabled(data.has_rho_uncertainty())
        self.b_heat_temperature.setEnabled(data.has_temperature())

        self.b_contour_moment.setEnabled(data.has_m())
        self.b_contour_rho.setEnabled(data.has_rho())
        self.b_contour_rho_uncertainty.setEnabled(data.has_rho_uncertainty())
        self.b_contour_temperature.setEnabled(data.has_temperature())

        self.b_level_moment.setEnabled(data.has_m())
        self.b_level_rho.setEnabled(data.has_rho())
        self.b_level_rho_uncertainty.setEnabled(data.has_rho_uncertainty())
        self.b_level_temperature.setEnabled(data.has_temperature())

        self.b_map_curves_moment.setEnabled(data.has_m())
        self.b_map_curves_rho.setEnabled(data.has_rho() and data.has_m())
        self.b_map_curves_rho_uncertainty.setEnabled(data.has_rho_uncertainty() and data.has_m())
        self.b_map_curves_temperature.setEnabled(data.has_temperature() and data.has_m())

        return

    def export_pmc(self):
        self.send_latest_data.emit()
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Create a save file:', './test_data/')[0]
        self.data_queue.get().export_pmc(path)
        return

    def export_vtk(self):
        self.send_latest_data.emit()
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Create a save file:', './test_data/')[0]
        self.data_queue.get().export_vtk(path)
        return
    
    def export_csv(self):
        self.send_latest_data.emit()
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'Create a save file:', './test_data/')[0]
        self.data_queue.get().export_csv(path)
        return