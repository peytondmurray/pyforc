"""Containers for holding FORC data as arrays."""
from __future__ import annotations

import numpy as np

from . import coordinates


class ForcData:
    """Container for FORC data.

    Parameters
    ----------
    h_raw : list[np.ndarray]
        Raw h data
    m_raw : list[np.ndarray]
        Raw m data
    t_raw : list[np.ndarray]
        Raw t data
    m_drift : np.ndarray
        Values of the magnetization at the drift points.
    h : np.ndarray
        Processed h data
    hr : np.ndarray
        Processed hr data
    m : np.ndarray
        Processed m data
    t : np.ndarray
        Processed t data
    """

    def __init__(
        self,
        h_raw: list[np.ndarray] = None,
        m_raw: list[np.ndarray] = None,
        t_raw: list[np.ndarray] = None,
        m_drift: np.ndarray = None,
        h: np.ndarray = None,
        hr: np.ndarray = None,
        m: np.ndarray = None,
        t: np.ndarray = None,
    ):
        self.h_raw = [] if h_raw is None else h_raw
        self.m_raw = [] if m_raw is None else m_raw
        self.t_raw = [] if t_raw is None else t_raw
        self.m_drift = np.array([]) if m_drift is None else m_drift
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

    @staticmethod
    def from_existing(data: ForcData, **kwargs) -> ForcData:
        """Generate a new ForcData instance from the input, but override fields with the kwargs.

        Parameters
        ----------
        data : ForcData
            Data which is to be copied over to the new instance
        kwargs :
            Fields which should take precedence over the values in `data`

        Returns
        -------
        ForcData
            A new instance of ForcData containing the old values present in `data`; if any fields
            were specified in the kwargs, those fields replace those from `data`.
        """
        return ForcData(
            kwargs.get('h_raw', data.h_raw),
            kwargs.get('m_raw', data.m_raw),
            kwargs.get('t_raw', data.t_raw),
            kwargs.get('m_drift', data.m_drift),
            kwargs.get('h', data.h),
            kwargs.get('hr', data.hr),
            kwargs.get('m', data.m),
            kwargs.get('t', data.t),
        )

    def curves(self, masked: bool = True) -> list[np.ndarray]:
        """Get the reversal curves in H-M space as a list of arrays of (H, M) pairs.

        Parameters
        ----------
        masked : bool
            If True, the reversal curves returned will not contain any points for which H < Hr.

        Returns
        -------
        list[np.ndarray]
            A list of arrays containing (H, M) points.
        """
        out = []
        for h, hr, m in zip(self.h, self.hr, self.m):
            # hstack two column vectors
            if masked:
                h_vec = h[h >= hr]
                m_vec = m[h >= hr]
            else:
                h_vec = h
                m_vec = m

            out.append(np.array([h_vec, m_vec]).T)

        return out

    def get_extent(self, coords: coordinates.Coordinates, mask: bool = True) -> tuple[float, ...]:
        """Get the extent of the dataset in H-Hr or Hc-Hb space.

        Parameters
        ----------
        coords : coordinates.Coordinates
            Coordinates to use to calculate the extent of the dataset
        mask : bool
            If True, data for which H < Hr will be included in the calculation of the extent

        Returns
        -------
        tuple[float, ...]
            [min x, max x, min y, max y]
        """
        if mask:
            h = self.h[~np.isnan(self.m)]
            hr = self.hr[~np.isnan(self.m)]
        else:
            h = self.h
            hr = self.hr

        transformed = coords.transform(
            np.array(
                [
                    [h.min(), hr.min()],
                    [h.max(), hr.min()],
                    [h.min(), hr.max()],
                    [h.max(), hr.max()],
                ]
            )
        )

        return (
            transformed[:, 0].min(),
            transformed[:, 0].max(),
            transformed[:, 1].min(),
            transformed[:, 1].max()
        )
