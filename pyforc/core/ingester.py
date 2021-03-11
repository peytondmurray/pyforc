import re

import numpy as np
import scipy.interpolate as si


class IngesterBase:

    def __init__(self, file_name, config):
        self.file_name = file_name
        self.config = config
        self.h_raw, self.m_raw, self.t_raw = [], [], []
        self.ingest(self.file_name)

        self.h, self.hr, self.m, self.t = interpolate(
            self.h_raw,
            self.m_raw,
            self.t_raw,
            step=self.config.step,
            method=self.config.method
        )

    def ingest(self, file_name):
        raise NotImplementedError


class PMCIngester(IngesterBase):

    pattern = (
        r'(?P<h>[+-]\d*\.\d*),'
        r'(?P<m>[+-]\d*\.\d*)'
        r'(,(?P<t>[+-]\d*\.\d*))?'
    )

    def ingest(self, file_name):

        with open(file_name, 'r') as f:
            lines = f.readlines()

        # Find first data line
        i = 0
        while i < len(lines) and lines[i][0] not in '-+':
            i += 1

        # Read the data in line by line
        h_buf, m_buf, t_buf = [], [], []
        while i < len(lines):
            match = re.search(self.pattern, lines[i])
            if match:
                # Line contains data; append to buffers and continue
                groups = match.groupdict()
                h_buf.append(float(groups['h']))
                m_buf.append(float(groups['m']))
                t_buf.append(float(groups['t']) if groups['t'] else np.nan)

            elif h_buf and m_buf:
                # This is the end of a reversal curve; append buffers to raw data
                self.h_raw.append(np.array(h_buf))
                self.m_raw.append(np.array(m_buf))
                self.t_raw.append(np.array(t_buf))
                h_buf, m_buf, t_buf = [], [], []

            i += 1

        return


def interpolate(h_raw, m_raw, t_raw, step=None, method='cubic'):
    """Interpolate the raw dataset.

    Parameters
    ----------
    h_raw: list of np.ndarray
        Ragged list of raw h-datapoints
    m_raw: list of np.ndarray
        Ragged list of raw m-datapoints
    t_raw: list of np.ndarray
        Ragged list of raw t-datapoints (if any)
    step: float
        Target step size of the interpolated data
    method: str
        Interpolation method; see scipy.interpolate.griddata for options

    -------
    Returns
    (np.ndarray, np.ndarray, np.ndarray, np.ndarray)
        Interpolated h, hr, m, and t arrays
    """
    if not step:
        step = np.median([np.diff(curve) for curve in h_raw])

    h_vals = np.concatenate(h_raw)
    hr_vals = np.concatenate(hr_vals_from_h(h_raw))
    m_vals = np.concatenate(m_raw)
    t_vals = np.concatenate(t_raw)

    h, hr = np.meshgrid(
        np.arange(np.min(h_vals), np.max(h_vals), step),
        np.arange(np.min(hr_vals), np.max(hr_vals), step),
    )

    hhr_vals = np.concatenate(
        (np.reshape(h_vals, (-1, 1)), np.reshape(hr_vals, (-1, 1))),
        axis=1
    ),

    m = si.griddata(hhr_vals, m_vals, (h, hr), method=method)
    t = si.griddata(hhr_vals, t_vals, (h, hr), method=method)

    # Mask off the portion of the interpolated data that wasn't measured
    m[h < hr] = np.nan
    t[h < hr] = np.nan

    return h, hr, m, t


def hr_vals_from_h(h):
    return [np.full_like(curve, fill_value=curve[0]) for curve in h]
