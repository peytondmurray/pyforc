"""
Plotting functionality
"""
import matplotlib.axes as axes
import matplotlib.pyplot as plt
import matplotlib.transforms as transforms
import numpy as np
from matplotlib.collections import LineCollection
from mpl_toolkits.axes_grid1 import make_axes_locatable

from . import forc


class Coordinates(transforms.Affine2D):
    @staticmethod
    def from_str(name):
        for subc in Coordinates.__subclasses__():
            if subc.name == name:
                return subc()

        raise ValueError(f"Invalid coordinate type {name}")


class CoordinatesHcHb(Coordinates):
    name = "hchb"

    def __init__(self):
        super().__init__(
            matrix=[
                [0.5, 0.5, 0],
                [0.5, -0.5, 0],
                [0, 0, 1],
            ]
        )


class CoordinatesHHr(Coordinates):
    name = "hhr"

    def __init__(self):
        super().__init__(
            matrix=[
                [1, 0, 0],
                [0, 1, 0],
                [0, 0, 1],
            ]
        )


def imshow(
    fc: forc.Forc,
    interpolation: str = 'bicubic',
    ax: axes.Axes = None,
    coordinates='hhr',
):

    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=(20, 10))
    else:
        fig = ax.figure

    t = transforms.Affine2D(
        matrix=[
            [0.5, 0.5, 0],
            [0.5, -0.5, 0],
            [0, 0, 1],
        ]
    )

    ax.set_transform(
        t + ax.transData  # Coordinates.from_str(coordinates)
    )

    im = ax.imshow(
        fc.data.m,
        interpolation=interpolation,
        origin='lower',
        extent=[fc.data.h.min(), fc.data.h.max(), fc.data.hr.min(), fc.data.hr.max()],
    )
    cax = make_axes_locatable(ax).append_axes("right", size="5%", pad=0.05)
    fig.colorbar(im, cax=cax)

    return ax


def curves(fc: forc.Forc, ax: axes.Axes = None):

    if ax is None:
        _, ax = plt.subplots(1, 1, figsize=(20, 10))

    ax.add_collection(
        LineCollection(
            fc.data.curves(),
            linestyles='solid',
            color='w',
            alpha=0.3,
        )
    )
    ax.set_xlim(np.nanmin(fc.data.h), np.nanmax(fc.data.h))
    ax.set_ylim(np.nanmin(fc.data.m), np.nanmax(fc.data.m))

    return ax
