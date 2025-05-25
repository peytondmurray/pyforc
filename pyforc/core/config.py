"""Class to hold configuration details for creating and analyzing FORC data."""

import dataclasses
from collections.abc import Callable

from .forcdata import ForcData


@dataclasses.dataclass
class Config:
    """Configuration class for analyzing FORC data.

    Parameters
    ----------
    file_name: str | None
        Name of the file containing FORC data
    step: float | None
        Step size to be used for the interpolated dataset; if None, step size is determined from the
        step size used for the measurement
    interpolation: str
        Interpolation method to use; see docstring for scipy.interpolate.griddata for valid
        methods.
    drift_correction: bool
        If True, drift correction will be applied before interpolation.
    drift_kernel_size: int
        The size of the window used for the moving average across the drift points is
        (2*drift_kernel_size) + 1. Larger numbers make the drift correction more smooth across the
        saturation magnetization.
    drift_density: int
        Decimation density used in drift correction; larger numbers make drift correction less
        sensitive to fluctuations in the saturation magnetization.
    h_sat: float
        Saturation field beyond which the irreversible component of the magnetization is saturated.
    pipeline: list[Callable[ForcData, Config], ForcData]
        List of operations to run upon ingestion
    smoothing_factor: int
        Smoothing factor to use for calculating the FORC distribution
    """

    file_name: str | None = None
    step: float | None = None
    interpolation: str = "cubic"
    drift_correction: bool = True
    drift_kernel_size: int = 4
    drift_density: int = 3
    pipeline: list[Callable[[ForcData, "Config"], ForcData]] | None = None
    h_sat: float = 0
    smoothing_factor: int = 3
