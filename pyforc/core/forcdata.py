"""Containers for holding FORC data as arrays."""

import numpy as np

from . import coordinates


class ForcData:
    """Container for FORC data.

    Parameters
    ----------
    h_raw : Optional[list[np.ndarray]]
        Raw h data
    m_raw : Optional[list[np.ndarray]]
        Raw m data
    t_raw : Optional[list[np.ndarray]]
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
    rho : np.ndarray
        FORC distribution
    """

    def __init__(
        self,
        h_raw: list[np.ndarray] | None = None,
        m_raw: list[np.ndarray] | None = None,
        t_raw: list[np.ndarray] | None = None,
        m_drift: np.ndarray = None,
        h: np.ndarray = None,
        hr: np.ndarray = None,
        m: np.ndarray = None,
        t: np.ndarray = None,
        rho: np.ndarray = None,
    ):
        self.h_raw = [] if h_raw is None else h_raw
        self.m_raw = [] if m_raw is None else m_raw
        self.t_raw = [] if t_raw is None else t_raw
        self.m_drift = np.array([]) if m_drift is None else m_drift
        self.h = np.array([]) if h is None else h
        self.hr = np.array([]) if hr is None else hr
        self.m = np.array([]) if m is None else m
        self.t = np.array([]) if t is None else t
        self.rho = np.array([]) if rho is None else rho

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
    def from_existing(
        data: "ForcData",
        h_raw: list[np.ndarray] | None = None,
        m_raw: list[np.ndarray] | None = None,
        t_raw: list[np.ndarray] | None = None,
        m_drift: np.ndarray = None,
        h: np.ndarray = None,
        hr: np.ndarray = None,
        m: np.ndarray = None,
        t: np.ndarray = None,
        rho: np.ndarray = None,
    ) -> "ForcData":
        """Generate a new ForcData instance from the input, but override fields with the kwargs.

        Parameters
        ----------
        data : ForcData
            Data which is to be copied over to the new instance
        h_raw : Optional[list[np.ndarray]]
            Raw magnetization data
        m_raw : Optional[list[np.ndarray]]
            Raw magnetization data
        t_raw : Optional[list[np.ndarray]]
            Raw temperature data
        m_drift : np.ndarray
            Drift magnetization measurements
        h : np.ndarray
            Processed field values
        hr : np.ndarray
            Processed reversal field values
        m : np.ndarray
            Processed magnetization data
        t : np.ndarray
            Processed temperature values
        rho : np.ndarray
            FORC distribution

        Returns
        -------
        ForcData:
            A new instance of ForcData containing the old values present in `data`; if any fields
            were specified in the kwargs, those fields replace those from `data`.
        """
        return ForcData(
            data.h_raw if h_raw is None else h_raw,
            data.m_raw if m_raw is None else m_raw,
            data.t_raw if t_raw is None else t_raw,
            data.m_drift if m_drift is None else m_drift,
            data.h if h is None else h,
            data.hr if hr is None else hr,
            data.m if m is None else m,
            data.t if t is None else t,
            data.rho if rho is None else rho,
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

    def get_extent(self, mask: bool = True) -> tuple[float, ...]:
        """Get the extent of the dataset in H-Hr space.

        Parameters
        ----------
        mask : bool
            If True, data for which H < Hr will be included in the calculation of the extent

        Returns
        -------
        tuple[float, ...]
            [min h, max h, min hr, max hr]
        """
        if mask:
            h = self.h[self.h >= self.hr]
            hr = self.hr[self.h >= self.hr]
        else:
            h = self.h
            hr = self.hr

        return (h.min(), h.max(), hr.min(), hr.max())

    def get_limits(
        self,
        coords: coordinates.Coordinates,
        mask: bool = True,
    ) -> tuple[tuple[float, float], tuple[float, float]]:
        """Get the x and y limits of the dataset.

        Parameters
        ----------
        coords : coordinates.Coordinates
            coords
        mask : bool
            mask

        Returns
        -------
        tuple[tuple[float, float], tuple[float, float]]
            (x_min, x_max), (y_min, y_max)
        """
        if mask:
            data_mask = self.h >= self.hr
            h = self.h[data_mask].flatten()
            hr = self.hr[data_mask].flatten()
        else:
            h = self.h.flatten()
            hr = self.hr.flatten()

        in_coords = coords.transform(np.vstack((h, hr)).T)

        return (
            (in_coords[:, 0].min(), in_coords[:, 0].max()),
            (in_coords[:, 1].min(), in_coords[:, 1].max()),
        )
