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
    pipeline: list[Callable[ForcData, Config], ForcData]
        List of operations to run upon ingestion
    """

    file_name: Optional[str] = None
    step: Optional[float] = None
    interpolation: str = 'cubic'
    drift_correction: bool = True
    pipeline: Optional[list[Callable[[ForcData, Config], ForcData]]] = None
