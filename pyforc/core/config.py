"""Class to hold configuration details for creating and analyzing FORC data."""

from typing import Optional


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
        interpolation methods.
    drift_correction: bool
        If True, drift correction will be applied before interpolation.
    """

    def __init__(
        self,
        file_name: str,
        step: Optional[float] = None,
        interpolation: str = 'cubic',
        drift_correction: bool = True,
    ):
        self.file_name = file_name
        self.step = step
        self.interpolation = interpolation
        self.drift_correction = drift_correction
