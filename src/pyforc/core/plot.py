"""Plotting utilities for the FORC data."""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import axes
from matplotlib.collections import LineCollection
from mpl_toolkits.axes_grid1 import make_axes_locatable

from . import coordinates, forc
from .ingester import ForcData


def imshow(
    fc: forc.Forc,
    attr: str = "m",
    interpolation: str = "nearest",
    ax: axes.Axes = None,
    coords: str | coordinates.Coordinates = "hhr",
    mask: bool = True,
) -> axes.Axes:
    """Show the FORC data as a colormap.

    Parameters
    ----------
    fc : forc.Forc
        Forc instance to be plotted
    attr : str
        Data attribute to plot. Valid choices are {h, hr, m, t, rho}.
    interpolation : str
        Interpolation to use.
    ax : axes.Axes
        Axes on which the image is to be drawn
    coords : str | coordinates.Coordinates
        Coordinates in which the data is to be drawn
    mask : bool
        If True, data for which H < Hr will be included in the calculation of the extent

    Returns
    -------
    axes.Axes
        Axes on which the image is drawn
    """
    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(15, 10))
    else:
        fig = ax.figure
    ax.set_aspect("equal")

    if isinstance(coords, coordinates.Coordinates):
        transform = coords
    else:
        transform = coordinates.Coordinates.from_str(coords)

    im = ax.imshow(
        getattr(fc.data, attr),
        interpolation=interpolation,
        origin="lower",
        extent=fc.data.get_extent(mask),
        transform=transform + ax.transData,
    )
    cax = make_axes_locatable(ax).append_axes("right", size="5%", pad=0.05)
    fig.colorbar(im, cax=cax)

    xlim, ylim = fc.data.get_limits(coords=transform, mask=mask)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)

    return ax


def curves(fc: forc.Forc | ForcData, ax: axes.Axes = None, **lc_kwargs) -> axes.Axes:
    """Plot the reversal curves in H-M space.

    Parameters
    ----------
    fc : forc.Forc
        Forc instance to be plotted
    ax : axes.Axes
        Axes on which the data is to be plotted
    **lc_kwargs
        Extra args to pass to the LineCollection instance

    Returns
    -------
    axes.Axes
        Axes on which the image is drawn
    """
    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(15, 10))

    if isinstance(fc, ForcData):
        data = fc
    else:
        data = fc.data

    lc_kwargs = {"linestyles": "solid", "color": "k", "alpha": 0.3, **lc_kwargs}
    ax.add_collection(LineCollection(data.curves(), **lc_kwargs))
    ax.set_xlim(np.nanmin(data.h), np.nanmax(data.h))
    ax.set_ylim(np.nanmin(data.m), np.nanmax(data.m))
    return ax
