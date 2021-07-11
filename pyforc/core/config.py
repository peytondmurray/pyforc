"""Class to hold configuration details for creating and analyzing FORC data."""
from __future__ import annotations

import dataclasses
from typing import Callable, Optional

from .forcdata import ForcData


@dataclasses.dataclass
class Config:
    """Configuration class for analyzing FORC data.

    Parameters
    ----------
    file_name: str
        Name of the file containing FORC data
    step: Optional[float]
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
    """

    file_name: Optional[str] = None
    step: Optional[float] = None
    interpolation: str = 'cubic'
    drift_correction: bool = True
    drift_kernel_size: int = 4
    drift_density: int = 3
    pipeline: Optional[list[Callable[[ForcData, Config], ForcData]]] = None
    h_sat: float = 0
