"""Class to hold configuration details for creating and analyzing FORC data."""


class Config:
    """Configuration class for analyzing FORC data.

    Parameters
    ----------
    file_name: str
        Name of the file containing FORC data
    step: float
        Step size of the interpolated dataset
    interpolation: str
        Interpolation method to use
    """

    def __init__(self, file_name: str, step: float = None, interpolation: str = 'cubic'):
        self.file_name = file_name
        self.step = step
        self.interpolation = interpolation
