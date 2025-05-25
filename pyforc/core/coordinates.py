"""Coordinate transformations for FORC data."""

import matplotlib.transforms as transforms


class Coordinates(transforms.Affine2D):
    """Base class for coordinates."""

    name: str | None = None

    @staticmethod
    def from_str(name: str) -> "Coordinates":
        """Get the appropriate Coordinates class instance by name.

        Parameters
        ----------
        name : str
            Name of the coordinates to return.

        Returns
        -------
        Coordinates
            The coordinates instance with the requested name.

        Raises
        ------
        ValueError
            Raised if `name` is not a valid Coordinate type
        """
        for subc in Coordinates.__subclasses__():
            if subc.name == name:
                return subc()

        raise ValueError(f"Invalid coordinate type {name}")


class CoordinatesHcHb(Coordinates):
    """Hc-Hb coordinates.

    Hc = (H - Hr)/2
    Hb = (H + Hr)/2

    H  = (Hb + Hc)
    Hr = (Hb - Hc)
    """

    name = "hchb"

    def __init__(self):
        super().__init__(
            matrix=[
                [0.5, -0.5, 0],
                [0.5, 0.5, 0],
                [0, 0, 1],
            ]
        )


class CoordinatesHHr(Coordinates):
    """H-Hr coordinates.

    These are the default coordinates, the coordinates in which the data is measured.
    """

    name = "hhr"

    def __init__(self):
        super().__init__(
            matrix=[
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, 1],
            ]
        )
