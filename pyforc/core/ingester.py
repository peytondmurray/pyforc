"""Classes for ingesting FORC data."""
import re
import typing

import numpy as np
import scipy.interpolate as si

from .config import Config


class ForcData:
    """Container for FORC data."""

    def __init__(
        self,
        h_raw: list[np.ndarray] = None,
        m_raw: list[np.ndarray] = None,
        t_raw: typing.Union[list[np.ndarray], None] = None,
        m_drift: typing.Union[list[np.ndarray], None] = None,
        h: np.ndarray = None,
        hr: np.ndarray = None,
        m: np.ndarray = None,
        t: np.ndarray = None,
    ):
        self.h_raw = [] if h_raw is None else h_raw
        self.m_raw = [] if m_raw is None else m_raw
        self.t_raw = [] if t_raw is None else t_raw
        self.m_drift = m_drift
        self.h = np.array([]) if h is None else h
        self.hr = np.array([]) if hr is None else hr
        self.m = np.array([]) if m is None else m
        self.t = np.array([]) if t is None else t

    def get_step(self) -> float:
        """Get the step size of the raw dataset.

        The step will be determined from the median of the steps in the h-direction.

        Returns
        -------
        float
            Size of the field step
        """
        return np.median(np.concatenate([np.diff(curve) for curve in self.h_raw]))

    def interpolate(
        self,
        step: float = None,
        interpolation: str = 'cubic',
    ):
        """Interpolate the raw dataset.

        m and t values for h < hr are set to np.nan.

        Parameters
        ----------
        step : float
            Step size along the h and hr directions to use for the interpolated dataset. Uses the
            same units given by the raw data. If None, the step will be determined from the median
            of the steps in the h-direction.
        interpolation : str
            Interpolation method to use; see docstring for scipy.interpolate.griddata for valid
            interpolation methods.
        """
        if not step:
            step = self.get_step()

        h_vals = np.concatenate(self.h_raw)
        hr_vals = np.concatenate(hr_vals_from_h(self.h_raw))
        m_vals = np.concatenate(self.m_raw)
        t_vals = np.concatenate(self.t_raw)

        h_min = np.min(h_vals)
        h_max = np.max(h_vals)
        hr_min = np.min(hr_vals)
        hr_max = np.max(hr_vals)

        self.h, self.hr = np.meshgrid(
            np.linspace(h_min, h_max, int((h_max - h_min) // step) + 1),
            np.linspace(hr_min, hr_max, int((hr_max - hr_min) // step) + 1),
        )

        hhr_vals = np.concatenate(
            (np.reshape(h_vals, (-1, 1)), np.reshape(hr_vals, (-1, 1))),
            axis=1
        ),

        self.m = si.griddata(hhr_vals, m_vals, (self.h, self.hr), method=interpolation)

        # Mask off the portion of the interpolated data that wasn't measured
        self.m[self.h < self.hr] = np.nan

        # If any temperature values are present in the raw data, interpolate over them; otherwise
        # all temperatures will be np.nan.
        if np.isnan(t_vals).any():
            self.t = np.full_like(self.m, fill_value=np.nan)
        else:
            self.t = si.griddata(hhr_vals, t_vals, (self.h, self.hr), method=interpolation)
            self.t[self.h < self.hr] = np.nan

        return

    def correct_drift(self):
        """Correct the raw magnetization for drift.

        If the measurement space is Hc/Hb, dedicated drift points must have been measured. If the
        measurement is H/Hr, the last datapoint along each curve is used. In either case, the points
        used for drift correction must have been measured above the saturation field.
        """
        mean_m_sat = np.mean(self.m_drift)
        for i, curve in self.m_raw:
            self.m_raw[i] -= (curve[-1] - mean_m_sat)
        return


class IngesterBase:
    """Base class for all ingester types.

    Ingesters are responsible for reading the raw data and generating a ForcData instance containing
    raw and interpolated datasets.

    Parameters
    ----------
    config : Config
        Ingester configuration to use for ingesting the raw data.
    """

    def __init__(self, config: Config):
        data = self.ingest(config)
        if config.drift_correction:
            data.correct_drift()
        data.interpolate(step=config.step, interpolation=config.interpolation)

    def ingest(self, config: Config) -> ForcData:
        """Ingest the raw data.

        Returns
        -------
        ForcData
            Raw field (h), magnetization (m), and temperature (t) (if present) values. No
            interpolation is carried out by default.
        """
        raise NotImplementedError


class PMCIngester(IngesterBase):
    """Ingester for data measured by Princeton Measurements Corporation (now Lakeshore) VSMs."""

    pattern = (
        r'(?P<h>([+-]\d+\.\d+(E[+-]\d+)?)),'
        r'(?P<m>([+-]\d+\.\d+(E[+-]\d+)?))'
        r'(,(?P<t>([+-]\d+\.\d+(E[+-]\d+)?)))?'
    )

    def ingest(self, config: Config) -> ForcData:
        """Ingest the raw data.

        Returns
        -------
        ForcData
            Raw field (h), magnetization (m), and temperature (t) (if present) values. No
            interpolation is carried out by default.
        """
        with open(config.file_name, 'r') as f:
            lines = f.readlines()

        # Find first data line
        i = 0
        while i < len(lines) and lines[i][0] not in '-+':
            i += 1

        data = ForcData()

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
                data.h_raw.append(np.array(h_buf))
                data.m_raw.append(np.array(m_buf))
                data.t_raw.append(np.array(t_buf))
                h_buf, m_buf, t_buf = [], [], []

            i += 1

        return data


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
