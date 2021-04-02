"""Classes for ingesting FORC data."""
import re

import numpy as np
import scipy.interpolate as si

from .config import Config


class IngesterBase:
    """Base class for all ingester types.

    Parameters
    ----------
    config : Config
        Ingester configuration to use for ingesting the raw data.
    """

    def __init__(self, config: Config):
        self.config = config
        self.h_raw: list[np.ndarray] = []
        self.m_raw: list[np.ndarray] = []
        self.t_raw: list[np.ndarray] = []

        self.ingest()

        self.h, self.hr, self.m, self.t = interpolate(
            self.h_raw,
            self.m_raw,
            self.t_raw,
            step=self.config.step,
            interpolation=self.config.interpolation
        )

    def ingest(self):
        """Ingest the raw data."""
        raise NotImplementedError


class PMCIngester(IngesterBase):
    """Ingester for data measured by Princeton Measurements Corporation (now Lakeshore) VSMs."""

    pattern = (
        r'(?P<h>([+-]\d+\.\d+(E[+-]\d+)?)),'
        r'(?P<m>([+-]\d+\.\d+(E[+-]\d+)?))'
        r'(,(?P<t>([+-]\d+\.\d+(E[+-]\d+)?)))?'
    )

    def ingest(self) -> None:
        """Ingest the raw data."""
        with open(self.config.file_name, 'r') as f:
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


def interpolate(
    h_raw: list[np.ndarray],
    m_raw: list[np.ndarray],
    t_raw: list[np.ndarray],
    step: float = None,
    interpolation: str = 'cubic',
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Interpolate the raw dataset.

    Parameters
    ----------
    h_raw : list[np.ndarray]
        Ragged list of raw h-datapoints
    m_raw : list[np.ndarray]
        Ragged list of raw m-datapoints
    t_raw : list[np.ndarray]
        Ragged list of raw t-datapoints (if any)
    step : float
        Step size along the h and hr directions to use for the interpolated dataset. Uses the same
        units given by the raw data. If None, the step will be determined from the median of the
        steps in the h-direction.
    interpolation : str
        interpolation

    Returns
    -------
    tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
        Interpolated h, hr, m, and t arrays. If t is not measured, this array will be empty
    """
    if not step:
        step = np.median(np.concatenate([np.diff(curve) for curve in h_raw]))

    h_vals = np.concatenate(h_raw)
    hr_vals = np.concatenate(hr_vals_from_h(h_raw))
    m_vals = np.concatenate(m_raw)
    t_vals = np.concatenate(t_raw)

    h_min = np.min(h_vals)
    h_max = np.max(h_vals)
    hr_min = np.min(hr_vals)
    hr_max = np.max(hr_vals)

    h, hr = np.meshgrid(
        np.linspace(h_min, h_max, int((h_max - h_min) // step) + 1),
        np.linspace(hr_min, hr_max, int((hr_max - hr_min) // step) + 1),
    )

    hhr_vals = np.concatenate(
        (np.reshape(h_vals, (-1, 1)), np.reshape(hr_vals, (-1, 1))),
        axis=1
    ),

    m = si.griddata(hhr_vals, m_vals, (h, hr), method=interpolation)

    # Mask off the portion of the interpolated data that wasn't measured
    m[h < hr] = np.nan

    if np.isnan(t_vals).any():
        t = np.full_like(m, fill_value=np.nan)
    else:
        t = si.griddata(hhr_vals, t_vals, (h, hr), method=interpolation)
        t[h < hr] = np.nan

    return h, hr, m, t


def hr_vals_from_h(h: list[np.ndarray]) -> list[np.ndarray]:
    """Generate an hr dataset from a ragged set of h curves.

    Parameters
    ----------
    h: list[np.ndarray]
        Ragged list of h-values for each reversal curve

    Returns
    -------
    list[np.ndarray]
        Ragged list of hr-values for each reversal curve. Each datapoint has an hr-value equal to
        the h-value of the first datapoint in the curve.
    """
    return [np.full_like(curve, fill_value=curve[0]) for curve in h]
