import numpy as np
import pathlib
import errors
import logging
import abc
# import pandas as pd
import scipy.interpolate as si
import scipy.ndimage as sn

log = logging.getLogger(__name__)


class ForcBase(abc.ABC):
    """Base class for all FORC subclasses.

    Attributes
    ----------
    h : ndarray
        2D array of floats containing the field H at each data point.

    hr : ndarray
        2D array of floats containing the reversal field H_r at each data point.

    m : ndarray
        2D array of floats containing the magnetization M at each point.

    T : ndarray
        2D array of floats containing the temperature T at each point

    drift_points : ndarray
        1D array of magnetization values corresponding to drift measurements. If no drift measurements
        were taken, these are taken from the last points in each reversal curve.
    """

    def __init__(self, input):

        super(ForcBase, self).__init__()

        self.h = None
        self.hr = None
        self.m = None
        self.T = None
        self.drift_points = None

        return


class PMCForc(ForcBase):
    """FORC class for PMC-formatted data. See the PMC format spec for more info. Magnetization (and, if present,
    temperature) data is optionally drift corrected upon instantiation before being interpolated on a
    uniform grid in (H, H_r) space.


    Parameters
    ----------
    path : str
        Path to PMC formatted data file.
    """

    def __init__(self, path, step, method='nearest', drift=False, radius=4, density=3):

        super(PMCForc, self).__init__(None)

        self.h = []               # Field
        self.hr = []              # Reversal field
        self.m = []               # Moment
        self.T = None             # Temperature (if any)
        self.rho = None           # FORC distribution.
        self.drift_points = []    # Drift points

        self._h_min = np.nan
        self._h_max = np.nan
        self._hr_min = np.nan
        self._hr_max = np.nan
        self._m_min = np.nan
        self._m_max = np.nan
        self._T_min = np.nan
        self._T_max = np.nan

        self._from_file(path)
        self._update_data_limits()

        if drift:
            self._drift_correction(radius=radius, density=density)
        self._interpolate(step=step, method=method)

        return

    @classmethod
    def from_file(cls, path, step, method='nearest', drift=False, radius=4, density=3):
        return cls(path, step, method, drift, radius, density)

    def _from_file(self, path):
        """Read a PMC-formatted file from path.

        Parameters
        ----------
        path : str
            Path to PMC-formatted csv file.
        """

        file = pathlib.Path(path)
        log.info("Extracting data from file: {}".format(file))

        try:
            with open(file, 'r') as f:
                lines = f.readlines()
        except ...:
            print("Error opening specified data file: {}".format(file))
            raise

        self._extract_raw_data(lines)

        return

    def _has_drift_points(self, lines):
        """Checks whether the measurement space has been specified in (Hc, Hb) coordinates or in (H, Hr). If it
        has been measured in (Hc, Hb) coordinates, the header will contain references to the limits of the
        measured data. If the measurement has been done in (Hc, Hb), drift points are necessary before the
        start of each reversal curve, which affects how the data is extracted.

        Parameters
        ----------
        lines : str
            Lines from a PMC-formatted data file.

        Returns
        -------
        bool
            True if 'Hb1' is detected in the start of a line somewhere in the data file, False otherwise.
        """

        for i in range(len(lines)):
            if "Hb1" == lines[i][:3]:
                return True
        return False

    def _has_temperature(self, line):
        """Checks for temperature measurements in a file. If line has 3 data values, the third is considered
        a temperature measurement.

        Parameters
        ----------
        line : str
            PMC formatted line to check

        Returns
        -------
        bool
            True if the line contains 3 floats or False if not.
        """

        return len(line.split(sep=',')) == 3

    def _extract_raw_data(self, lines):
        """Extracts the raw data from lines of a PMC-formatted csv file.

        Parameters
        ----------
        lines : str
            Contents of a PMC-formatted data file.
        """

        i = self._find_first_data_point(lines)
        if self._has_temperature(lines[i]):
            self._T = []

        if self._has_drift_points(lines):
            while i < len(lines) and lines[i][0] in ['+', '-']:
                self._extract_drift_point(lines[i])
                i += 2
                i += self._extract_next_forc(lines[i:])
                i += 1
        else:
            while i < len(lines) and lines[i][0]in ['+', '-']:
                i += self._extract_next_forc(lines[i:])
                self._extract_drift_point(lines[i-1:])
                i += 1

        return

    def _find_first_data_point(self, lines):
        """Return the index of the first data point in the PMC-formatted lines.

        Parameters
        ----------
        lines : str
            Contents of a PMC-formatted data file.

        Raises
        ------
        errors.DataFormatError
            If no lines begin with '+' or '-', an error is raised. Data points must begin with '+' or

        Returns
        -------
        int
            Index of the first data point. Skips over any header info at the start of the file, as long as
            the header lines do not begin with '+' or '-'.
        """

        for i in range(len(lines)):
            if lines[i][0] in ['+', '-']:
                return i

        raise errors.DataFormatError("No data found in file. Check data format spec.")

    def _extract_next_forc(self, lines):
        """Extract the next curve from the data.

        Parameters
        ----------
        lines : str
            Raw csv data in string format, from a PMC-type formatted file.

        Returns
        -------
        int
            Number of lines extracted
        """

        _h, _m, _hr, _T = [], [], [], []
        i = 0

        while lines[i][0] in ['+', '-']:
            split_line = lines[i].split(',')
            _h.append(float(split_line[0]))
            _hr.append(_h[0])
            _m.append(float(split_line[1]))
            if self.T is not None:
                _T.append(float(split_line[2]))
            i += 1

        self.h.append(_h)
        self.hr.append(_hr)
        self.m.append(_m)
        if self.T is not None:
            self.T.append(_T)

        return len(_h)

    def _extract_drift_point(self, line):
        """Extract the drift point from the specified input line. Only records the moment,
        not the measurement field from the drift point (the field isn't used in any drift correction).
        Appends the drift point to self.drift_points.

        Parameters
        ----------
        line : str
            Line from data file which contains the drift point.
        """

        self.drift_points.append(float(line.split(sep=',')[-1]))
        return

    @property
    def shape(self):
        if isinstance(self.h, np.ndarray):
            return self.h.shape
        else:
            raise ValueError("self.h has not been interpolated to numpy.ndarray! Type: {}".format(type(self.h)))

    def _interpolate(self, step, method='nearest'):

        _h, _hr = np.meshgrid(np.arange(self._h_min, self._h_max, step),
                              np.arange(self._hr_min, self._hr_max, step))

        data_hhr = [[self.h[i][j], self.hr[i][j]] for i in range(len(self.h)) for j in range(len(self.h[i]))]
        data_m = [self.m[i][j] for i in range(len(self.h)) for j in range(len(self.h[i]))]

        _m = si.griddata(np.array(data_hhr), np.array(data_m), (_h, _hr), method=method)
        if self.T is not None:
            data_T = [self.T[i][j] for i in range(len(self.h)) for j in range(len(self.h[i]))]
            self.T = si.griddata(np.array(data_hhr), np.array(data_T), (_h, _hr), method=method)

        _m[_h < _hr] = np.nan

        self.h = _h
        self.hr = _hr
        self.m = _m

        return

    def _drift_correction(self, radius=4, density=3):

        kernel_size = 2*radius+1
        kernel = np.ones(kernel_size)/kernel_size

        average_drift = np.mean(self.drift_points)
        moving_average = sn.convolve(self.drift_points, kernel, mode='nearest')
        interpolated_drift = si.interp1d(np.arange(start=0, stop=len(self.drift_points), step=density),
                                         moving_average[::density],
                                         kind='cubic')

        for i in range(len(self.m)):
            drift = (interpolated_drift(i) - average_drift)
            self.drift_points[i] -= drift
            for j in range(len(self.m[i])):
                self.m[i][j] -= drift

        return

    def _update_data_limits(self):

        if isinstance(self.h, list):
            # numpy.ravel doesn't work properly on ragged lists. Need to manually flatten the lists.
            _h = []
            _hr = []
            _m = []

            for i in range(len(self.h)):
                _h.extend(self.h[i])
                _hr.extend(self.hr[i])
                _m.extend(self.m[i])

            _h = np.array(_h)
            _hr = np.array(_hr)
            _m = np.array(_m)

            if self.T is not None:
                _T = []
                for i in range(len(self.h)):
                    _T.extend(self.T[i])
                _T = np.array(_T)

        elif isinstance(self.h, np.ndarray):
            _h = self.h
            _hr = self.hr
            _m = self.m
            _T = self.T

        else:
            raise ValueError("Data is an unintended type: {}".format(type(self.h)))

        self._h_min = np.nanmin(_h)
        self._h_max = np.nanmax(_h)
        self._hr_min = np.nanmin(_hr)
        self._hr_max = np.nanmax(_hr)
        self._m_min = np.nanmin(_m)
        self._m_max = np.nanmax(_m)

        if self.T is None or np.all(np.isnan(self.T)):
            self._T_min = np.nan
            self._T_max = np.nan
        else:
            self._T_min = np.nanmin(_T)
            self._T_max = np.nanmax(_T)

        return

    def h_range(self):
        return (self._h_min, self._h_max)

    def hr_range(self):
        return (self._hr_min, self._hr_max)

    def m_range(self):
        return (self._m_min, self._m_max)

    def _extend_dataset(self, sf, method):

        return

    def _compute_forc_sg(self, sf):

        return

    def compute_forc_distribution(self, sf=3, method='savitzky-golay', extension='flat'):

        self._extend_dataset(sf=3, method=extension)

        if method == 'savitzky-golay':
            self._compute_forc_sg(sf=3)

        return