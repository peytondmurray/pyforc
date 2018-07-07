import numpy as np
import pathlib
import logging
import abc
# import pandas as pd
import scipy.interpolate as si
import scipy.ndimage.filters as snf
import scipy.optimize as so
import util
import numba as nb

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
        self.temperature = None
        self.drift_points = None

        return


spec = [('_h_min ', nb.float32),
        ('_h_max ', nb.float32),
        ('_hr_min', nb.float32),
        ('_hr_max', nb.float32),
        ('_hc_min', nb.float32),
        ('_hc_max', nb.float32),
        ('_hb_min', nb.float32),
        ('_hb_max', nb.float32),
        ('_m_min ', nb.float32),
        ('_m_max ', nb.float32),
        ('_T_min ', nb.float32),
        ('_T_max ', nb.float32),
        ('h', nb.float32[:]),
        ('hr', nb.float32[:]),
        ('hc', nb.float32[:]),
        ('hb', nb.float32[:]),
        ('m', nb.float32[:]),
        ('m_hchb', nb.float32[:]),
        ('rho', nb.float32[:]),
        ('rho_hchb', nb.float32[:]),
        ('temperature', nb.float32[:]),
        ('temperature_hchb', nb.float32[:]),
        ('rho_uncertainty', nb.float32[:]),
        ('rho_uncertainty_hchb', nb.float32[:]),
        ('step', nb.float32)]
@nb.jitclass(spec)
class PMCForc(ForcBase):
    """FORC class for PMC-formatted data. See the PMC format spec for more info. Magnetization (and, if present,
    temperature) data is optionally drift corrected upon instantiation before being interpolated on a
    uniform grid in (H, H_r) space.


    Parameters
    ----------
    path : str
        Path to PMC formatted data file.
    """

    def __init__(self, path=None, step=None, method='cubic', drift=False, radius=4, density=3,
                 h=None, hr=None, m=None, T=None, rho=None):

        super(PMCForc, self).__init__(None)

        self._h_min = np.nan
        self._h_max = np.nan
        self._hr_min = np.nan
        self._hr_max = np.nan
        self._hc_min = np.nan
        self._hc_max = np.nan
        self._hb_min = np.nan
        self._hb_max = np.nan
        self._m_min = np.nan
        self._m_max = np.nan
        self._T_min = np.nan
        self._T_max = np.nan

        if all([item is not None for item in (h, hr, m)]):
            self.h = None             # Field
            self.hr = None            # Reversal field
            self.m = None             # Moment
            self.temperature = None             # Temperature (if any)
            self.rho = None           # FORC distribution.

            self.hc = None
            self.hb = None
            self.m_hchb = None
            self.temperature_hchb = None
            self.rho_hchb = None
            self._from_input_arrays(h, hr, m, T, rho)
            self.step = self._determine_step()

        elif path is not None:
            self.h = []               # Field
            self.hr = []              # Reversal field
            self.m = []               # Moment
            self.temperature = None             # Temperature (if any)
            self.rho = None           # FORC distribution.
            self.drift_points = []    # Drift points

            self.hc = None
            self.hb = None
            self.m_hchb = None
            self.temperature_hchb = None
            self.rho_hchb = None

            self._from_file(path)
            if drift:
                self._drift_correction(radius=radius, density=density)

            if step is None:
                self.step = self._determine_step()
            else:
                self.step = step

            self._interpolate(method=method)

        else:
            raise IOError('PMCForc can only be specified from valid path or from numpy arrays!')

        self._interpolate_hchb(method=method)
        self._update_data_range()

        return

    def _from_input_arrays(self, h, hr, m, T, rho):
        if all([isinstance(item, np.ndarray) for item in (h, hr, m)]):
            self.h = h
            self.hr = hr
            self.m = m

            if isinstance(T, np.ndarray):
                self.temperature = T
            elif T is not None:
                raise IOError('Invalid input type for T: {}'.format(type(T)))

            if isinstance(rho, np.ndarray):
                self.rho = rho
            elif rho is not None:
                raise IOError('Invalid input type for rho: {}'.format(type(rho)))

        else:
            raise IOError('Invalid input type for h, hr, or m arrays.')

        return

    def _from_file(self, path):
        """Read a PMC-formatted file from path.

        Parameters
        ----------
        path : str
            Path to PMC-formatted csv file.
        """

        file = pathlib.Path(path)
        log.info("Extracting data from file: {}".format(file))

        with open(file, 'r') as f:
            lines = f.readlines()

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

        raise DataFormatError("No data found in file. Check data format spec.")

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
            if self.temperature is not None:
                _T.append(float(split_line[2]))
            i += 1

        self.h.append(_h)
        self.hr.append(_hr)
        self.m.append(_m)
        if self.temperature is not None:
            self.temperature.append(_T)

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

    def _determine_step(self):
        """Calculate the field step size. Only works along the h-direction, since that's where most of the points live
        in hhr space. Takes the mean of the field steps along each reversal curve, then takes the mean of those means
        as the field step size.

        #TODO could this be better? make a histogram and do a fit?

        Returns
        -------
        float
            Field step size.
        """

        step_sizes = np.empty(len(self.h))

        for i in range(step_sizes.shape[0]):
            step_sizes[i] = np.mean(np.diff(self.h[i], n=1))

        return np.mean(step_sizes)

    def _interpolate(self, method='cubic'):

        # Determine min and max values of (h, hr) from raw input lists for interpolation.
        h_min = self.h[0][0]
        h_max = self.h[0][0]
        hr_min = self.hr[0][0]
        hr_max = self.hr[0][0]
        for i in range(len(self.h)):
            h_min = np.min(self.h[i]) if np.min(self.h[i]) < h_min else h_min
            h_max = np.max(self.h[i]) if np.max(self.h[i]) > h_max else h_max
            hr_min = np.min(self.hr[i]) if np.min(self.hr[i]) < hr_min else hr_min
            hr_max = np.max(self.hr[i]) if np.max(self.hr[i]) > hr_max else hr_max

        _h, _hr = np.meshgrid(np.arange(h_min, h_max, self.step),
                              np.arange(hr_min, hr_max, self.step))

        data_hhr = [[self.h[i][j], self.hr[i][j]] for i in range(len(self.h)) for j in range(len(self.h[i]))]
        data_m = [self.m[i][j] for i in range(len(self.h)) for j in range(len(self.h[i]))]

        _m = si.griddata(np.array(data_hhr), np.array(data_m), (_h, _hr), method=method)
        if self.temperature is not None:
            data_T = [self.temperature[i][j] for i in range(len(self.h)) for j in range(len(self.h[i]))]
            self.temperature = si.griddata(np.array(data_hhr), np.array(data_T), (_h, _hr), method=method)

        _m[_h < _hr] = np.nan

        self.h = _h
        self.hr = _hr
        self.m = _m

        return

    def _interpolate_hchb(self, method='cubic'):
        """Interpolate the data (m (and if applicable) T and rho)

        method : str, optional
            Interpolation method. (the default is 'cubic', but if the interpolated dataset looks messed up, use
            'linear'.)
        """

        hc, hb = util.hhr_to_hchb(self.h, self.hr)
        indices_nonnan = np.nonzero(np.logical_not(np.isnan(self.m)))
        data_hchb = np.vstack((np.ravel(hc[indices_nonnan]), np.ravel(hb[indices_nonnan]))).T
        data_m = np.ravel(self.m[indices_nonnan])

        self.hc, self.hb = np.meshgrid(np.arange(np.min(data_hchb[:, 0]), np.max(data_hchb[:, 0]), self.step_hchb),
                                       np.arange(np.min(data_hchb[:, 1]), np.max(data_hchb[:, 1]), self.step_hchb))

        self.m_hchb = si.griddata(data_hchb, data_m, (self.hc, self.hb), method=method)
        if self.temperature is not None:
            indices_nonnan = np.nonzero(np.logical_not(np.isnan(self.temperature)))
            data_hchb = np.vstack((np.ravel(hc[indices_nonnan]), np.ravel(hb[indices_nonnan]))).T
            data_T = np.ravel(self.temperature[indices_nonnan])
            self.temperature = si.griddata(data_hchb, data_T, (self.hc, self.hb), method=method)

        if self.rho is not None:
            indices_nonnan = np.nonzero(np.logical_not(np.isnan(self.rho)))
            data_hchb = np.vstack((np.ravel(hc[indices_nonnan]), np.ravel(hb[indices_nonnan]))).T
            data_rho = np.ravel(self.rho[indices_nonnan])
            self.rho_hchb = si.griddata(data_hchb, data_rho, (self.hc, self.hb), method=method)

        return

    def _drift_correction(self, radius=4, density=3):

        kernel_size = 2*radius+1
        kernel = np.ones(kernel_size)/kernel_size

        average_drift = np.mean(self.drift_points)
        moving_average = snf.convolve(self.drift_points, kernel, mode='nearest')
        interpolated_drift_indices = np.arange(start=0, stop=len(self.drift_points), step=1)

        if len(self.drift_points) % density == 0:
            interpolated_drift = si.interp1d(np.arange(start=0, stop=len(self.drift_points), step=density),
                                             moving_average[::density],
                                             kind='cubic')
        else:
            interpolated_drift = si.interp1d(np.hstack((np.arange(start=0, stop=len(self.drift_points), step=density),
                                                        len(self.drift_points)-1)),
                                             np.hstack((moving_average[::density],
                                                        np.array(moving_average[-1]))),
                                             kind='cubic')

        for i in interpolated_drift_indices:
            drift = (interpolated_drift(i) - average_drift)
            self.drift_points[i] -= drift
            for j in range(len(self.m[i])):
                self.m[i][j] -= drift

        return

    def _update_data_range(self):
        """Cache the limits of the data in hhr and hchb space to make plotting faster.

        """

        _hc, _hb = util.hhr_to_hchb(self.h, self.hr)

        self._h_min = np.min(self.h)
        self._h_max = np.max(self.h)
        self._hr_min = np.min(self.hr)
        self._hr_max = np.max(self.hr)
        self._hc_min = np.min(self.hc)
        self._hc_max = np.max(self.hc)
        self._hb_min = np.min(self.hb)
        self._hb_max = np.max(self.hb)
        self._m_min = np.nanmin(self.m)
        self._m_max = np.nanmax(self.m)

        if self.temperature is None or np.all(np.isnan(self.temperature)):
            self._T_min = np.nan
            self._T_max = np.nan
        else:
            self._T_min = np.nanmin(self.temperature)
            self._T_max = np.nanmax(self.temperature)

        return

    def h_range(self):
        return (self._h_min, self._h_max)

    def hr_range(self):
        return (self._hr_min, self._hr_max)

    def hc_range(self):
        return (self._hc_min, self._hc_max)

    def hb_range(self):
        return (self._hb_min, self._hb_max)

    def m_range(self):
        return (self._m_min, self._m_max)

    @property
    def extent_hhr(self):
        """Get extent of dataset in (H, Hr) space for plotting maps. Values returned are offset from actual data so
        that each data point corresponds to the center of a pixel on the map, rather than the corner.

        Returns
        -------
        list of floats
            h_min, h_max, hr_min, hr_max
        """

        return [self._h_min-0.5*self.step, self._h_max+0.5*self.step,
                self._hr_min-0.5*self.step, self._hr_max+0.5*self.step]

    @property
    def extent_hchb(self):
        """Get extent of dataset in (Hc, Hb) space for plotting maps. Values returned are offset from actual data so
        that each data point corresponds to the center of a pixel on the map, rather than the corner.

        Returns
        -------
        list of floats
            hc_min, hc_max, hb_min, hb_max
        """

        return [self._hc_min-0.5*self.step_hchb, self._hc_max+0.5*self.step_hchb,
                self._hb_min-0.5*self.step_hchb, self._hb_max+0.5*self.step_hchb]

    @property
    def step_hchb(self):
        return self.step/(2**0.5)  # Space is distorted from (H, Hr) -> (Hc, Hb) transformation

    def _extend_dataset(self, sf, method, n_fit_points=10):

        if method == 'truncate':
            return

        h_extend, hr_extend = np.meshgrid(np.arange(self._h_min - 2*sf*self.step, self._h_min, self.step),
                                          np.arange(self._hr_min, self._hr_max+self.step, self.step))

        self.h = np.concatenate((h_extend, self.h), axis=1)
        self.hr = np.concatenate((hr_extend, self.hr), axis=1)
        self.m = np.concatenate((h_extend*np.nan, self.m), axis=1)

        if method == 'flat':
            self._extend_flat(self.h, self.m)
        elif method == 'slope':
            self._extend_slope(self.h, self.m, n_fit_points)
        else:
            raise NotImplementedError

        if self.temperature is not None:
            self.temperature = np.concatenate((h_extend*np.nan, self.temperature), axis=1)

        # Not necessary, as this function should never be called outside compute_forc_distribution,
        # which returns a new PMCForc instance which does this anyway
        # self._update_data_range()

        return

    @classmethod
    def _compute_forc_sg(cls, m, sf, step_x, step_y):
        kernel = cls._sg_kernel(sf, step_x, step_y)
        # return snf.convolve(m, kernel, mode='constant', cval=np.nan)
        return util.fast_symmetric_convolve(m, kernel)

    @staticmethod
    def _sg_kernel(sf, step_x, step_y):

        xx, yy = np.meshgrid(np.linspace(sf*step_x, -sf*step_x, 2*sf+1),
                             np.linspace(sf*step_y, -sf*step_y, 2*sf+1))

        xx = np.reshape(xx, (-1, 1))
        yy = np.reshape(yy, (-1, 1))

        coefficients = np.linalg.pinv(np.hstack((np.ones_like(xx), xx, xx**2, yy, yy**2, xx*yy)))

        kernel = np.reshape(coefficients[5, :], (2*sf+1, 2*sf+1))

        return kernel

    def compute_forc_distribution(self, sf=3, method='savitzky-golay', extension='flat', n_fit_points=10):

        log.debug("Computing FORC distribution: sf={}, method={}, extension={}".format(sf, method, extension))

        # Only extend the dataset if rho has not been computed yet. Don't want to extend more than once.
        if self.rho is None:
            self._extend_dataset(sf=3, method=extension, n_fit_points=n_fit_points)

        if method == 'savitzky-golay':
            rho = self._compute_forc_sg(self.m, sf=3, step_x=self.step, step_y=self.step)
        else:
            raise NotImplementedError("method {} not implemented for FORC distribution calculation".format(method))

        return PMCForc(h=self.h, hr=self.hr, m=self.m, rho=rho, T=self.temperature)

    @classmethod
    def _extend_flat(cls, h, m):
        for i in range(m.shape[0]):
            first_data_index = util.arg_first_not_nan(m[i])
            m[i, 0:first_data_index] = m[i, first_data_index]
        return

    @classmethod
    def _extend_slope(cls, h, m, n_fit_points=10):
        for i in range(m.shape[0]):

            j = util.arg_first_not_nan(m[i])
            popt, _ = so.curve_fit(util.line, h[i, j:j+n_fit_points], m[i, j:j+n_fit_points])
            m[i, 0:j] = util.line(h[i, 0:j], *popt)

        return

    def major_loop(self):
        """Construct a major loop from the FORC data. Takes all of the uppermost curve, and appends the reversal points
        from each curve to create the descending hysteresis curve. Uses the lowermost curve as the ascending
        hysteresis curve.

        Returns
        -------
        tuple of arrays
            h-values, hr-values, m-values as 1D arrays.
        """

        upper_curve = self.shape[0]-1
        upper_curve_length = np.sum(self.h[upper_curve] >= self.hr[upper_curve, 0])
        h = np.empty(2*(self.shape[0]+upper_curve_length-1)-1)*0
        hr = np.empty(2*(self.shape[0]+upper_curve_length-1)-1)*0
        m = np.empty(2*(self.shape[0]+upper_curve_length-1)-1)*0

        for i in range(upper_curve_length-1):
            pt_index = self.shape[1]-1-i
            h[i] = self.h[upper_curve, pt_index]
            hr[i] = self.hr[upper_curve, pt_index]
            m[i] = self.m[upper_curve, pt_index]
        for i in range(self.shape[0]):
            forc_index = self.shape[0]-1-i
            major_loop_index = upper_curve_length-1+i
            h[major_loop_index] = self.hr[forc_index, 0]
            hr[major_loop_index] = self.hr[forc_index, 0]
            m[major_loop_index] = self.m[forc_index, self.h[forc_index] >= self.hr[forc_index, 0]][0]

        h[self.shape[0]+upper_curve_length-2:] = self.h[0, self.h[0] >= self.hr[0, 0]]
        hr[self.shape[0]+upper_curve_length-2:] = self.hr[0, self.h[0] >= self.hr[0, 0]]
        m[self.shape[0]+upper_curve_length-2:] = self.m[0, self.h[0] >= self.hr[0, 0]]

        return h, hr, m

    def slope_correction(self, h_sat=None, value=None):

        if value is None:
            if h_sat is None:

                first_non_nan = util.arg_first_not_nan(self.m[self.shape[0]-1])
                last_non_nan = util.arg_last_non_nan(self.m[self.shape[0]-1])

                popt, _ = so.curve_fit(util.line,
                                       self.h[self.shape[0]-1, first_non_nan:last_non_nan],
                                       self.m[self.shape[0]-1, first_non_nan:last_non_nan])
                value = popt[0]

            else:
                index_h_sat = np.argwhere(self.h[0] > h_sat)[0][0]
                h_gt_h_sat = self.h[0, index_h_sat:]
                m_gt_h_sat = self.m[:, index_h_sat:]
                average_m = np.nansum(m_gt_h_sat, axis=0)/np.nansum(np.logical_not(np.isnan(m_gt_h_sat)), axis=0)
                popt, _ = so.curve_fit(util.line, h_gt_h_sat, average_m)
                value = popt[0]

        return PMCForc(h=self.h, hr=self.hr, m=self.m - (value*self.h), T=self.temperature, rho=self.rho)

    def get_masked(self, data, mask, coordinates):
        mask = mask is True or mask == 'h<hr'

        if mask:
            masked_data = data.copy()
            if coordinates == 'hhr':
                masked_data[self.h < self.hr-self.step] = np.nan
            elif coordinates == 'hchb':
                masked_data[self.hc < 0] = np.nan
            else:
                raise ValueError('Invalid coordinates: {}'.format(coordinates))
            return masked_data
        else:
            return data

    def get_extent(self, coordinates):
        if coordinates == 'hhr':
            return self.extent_hhr
        elif coordinates == 'hchb':
            return self.extent_hchb
        else:
            raise ValueError('Invalid coordinates: {}'.format(coordinates))

    def get_data(self, data_str, coordinates):
        data_str = data_str.lower()
        if data_str in ['m', 'rho', 'rho_uncertainty', 't']:
            if coordinates == 'hhr':
                return getattr(self, data_str)
            elif coordinates == 'hchb':
                return getattr(self, '{}_hchb'.format(data_str))
            else:
                raise ValueError('Invalid coordinates: {}'.format(coordinates))
        else:
            raise ValueError('Invalid data field: {}'.format(data_str))

    def normalize(self, method='minmax'):
        if method == 'minmax':
            return PMCForc(h=self.h,
                           hr=self.hr,
                           m=1-2*(np.nanmax(self.m)-self.m)/(np.nanmax(self.m)-np.nanmin(self.m)),
                           rho=self.rho,
                           T=self.temperature)
        else:
            raise NotImplementedError


class ForcError(Exception):
    pass


class IOError(ForcError):
    pass


class DataFormatError(ForcError):
    pass
