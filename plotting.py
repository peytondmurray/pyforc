import matplotlib.cm as cm
import matplotlib.lines as ml
import matplotlib.collections as mc
import matplotlib.ticker as mt
import mpl_toolkits.axes_grid1 as mpltkag1
import numpy as np
import util


def h_vs_m(ax, forc, mask='h<hr', points='none', cmap='viridis'):

    mask = mask.lower()
    points = points.lower()
    cmap = cmap.lower()

    cmap = cm.get_cmap(cmap)
    colors = [cmap(x) for x in np.linspace(0, 0.4, forc.shape[0])]

    if points in ['none', 'reversal']:

        if mask.lower() == 'h<hr':
            for i in range(forc.shape[0]):
                h = forc.h[i]
                m = forc.m[i]
                ax.add_line(ml.Line2D(xdata=h[h >= forc.hr[i, 0]], ydata=m[h >= forc.hr[i, 0]], color=colors[i]))
        elif mask in ['outline', 'none']:
            for i in range(forc.shape[0]):
                ax.add_line(ml.Line2D(xdata=forc.h[i], ydata=forc.m[i], color=colors[i]))

            if mask == 'outline':
                h, hr, m = forc.major_loop()
                ax.add_line(ml.Line2D(xdata=h, ydata=m, linestyle=':', color='r', linewidth=2, alpha=1.0))
        else:
            raise ValueError('Invalid mask argument: {}'.format(mask))

        if points == 'reversal':
            hr = forc.hr[:, 0]
            m = np.zeros_like(forc.hr[:, 0])
            for i in range(forc.shape[0]):
                m[i] = forc.m[i, forc.h[i] >= forc.hr[i, 0]][0]

            ax.add_line(ml.Line2D(xdata=hr, ydata=m, marker='o', linestyle='', color='grey', markersize=4))

        elif points == 'all':
            ax.add_line(ml.Line2D(xdata=forc.h, ydata=forc.m, marker='o', linestyle='', color='grey', markersize=4))

        ax.autoscale_view()
    else:
        raise ValueError('Invalid points argument: {}'.format(points))
    ax.figure.canvas.draw()
    return


def major_loop(ax, forc, color='k'):
    h, _, m = forc.major_loop()
    ax.add_line(ml.Line2D(xdata=h, ydata=m, linestyle='-', color=color, marker='o'))
    ax.figure.canvas.draw()
    return


def hhr_space_major_loop(ax, forc):
    h, hr, _ = forc.major_loop()
    ax.add_line(ml.Line2D(xdata=h, ydata=hr, marker='.', linestyle='', color='k', markersize=12, alpha=0.3))
    ax.figure.canvas.draw()
    return


def plot_points(ax, forc, coordinates):
    """Plots the location of the actual data points in the FORC object in (H, Hr) or (Hc, Hb) space. Forc.hc and
    Forc.hb are interpolated from Forc.h and Forc.hr and are inteded to be used only for plotting data in (Hc, Hb)
    space - they don't actually represent the location of actual data points. As a result, they aren't used here
    because this function is intended to show the locations of the data points on the 2D plane.

    Parameters
    ----------
    ax : axes object
        Axes to plot the points on
    forc : Forc
        Dataset to plot
    """

    if coordinates == 'hhr':
        x = forc.h
        y = forc.hr
    elif coordinates == 'hchb':
        x, y = util.hhr_to_hchb(forc.h, forc.hr)
    else:
        raise ValueError('Invalid coordinates: {}'.format(coordinates))

    ax.plot(x, y, marker='.', linestyle='', color='k', alpha=0.3)
    ax.figure.canvas.draw()
    return


def heat_map(ax, forc, data_str, mask, coordinates, interpolation='nearest', cmap='RdBu_r'):
    ax.clear()
    im = ax.imshow(forc.get_masked(forc.get_data(data_str, coordinates), mask, coordinates),
                   extent=forc.get_extent(coordinates),
                   cmap=cmap,
                   origin='lower',
                   interpolation=interpolation)
    colorbar(ax, im)
    ax.figure.canvas.draw()
    return


def contour_map(ax, forc, data_str, mask, coordinates, interpolation='nearest', cmap='RdBu_r', levels=None):
    ax.clear()
    im = ax.contourf(forc.get_masked(forc.get_data(data_str, coordinates), mask, coordinates),
                     extent=forc.get_extent(coordinates),
                     cmap=cmap,
                     origin='lower',
                     levels=levels)
    colorbar(ax, im)
    ax.figure.canvas.draw()
    return


def contour_levels(ax, forc, data_str, mask, coordinates, levels=None):
    ax.contour(forc.get_masked(forc.get_data(data_str, coordinates), mask, coordinates),
               extent=forc.get_extent(coordinates),
               origin='lower',
               levels=levels,
               colors='k')
    ax.figure.canvas.draw()
    return


def decorate_hm(ax, xlabel=r'$H$', ylabel=r'$M$', xlim=None, ylim=None, legend=False, legend_args=None):
    ax.set(xlabel=xlabel,
           ylabel=ylabel,
           xlim=xlim,
           ylim=ylim)

    if legend is not False:
        ax.legend(legend_args or None)

    ax.figure.canvas.draw()
    return


def decorate_hhr(ax, xlabel=r'$H$', ylabel=r'$H_r$', xlim=None, ylim=None):
    ax.set(xlabel=xlabel,
           ylabel=ylabel,
           xlim=xlim,
           ylim=ylim)
    ax.figure.canvas.draw()
    return


def decorate_hchb(ax, xlabel=r'$H_c$', ylabel=r'$H_b$', xlim=None, ylim=None):
    ax.set(xlabel=xlabel,
           ylabel=ylabel,
           xlim=xlim,
           ylim=ylim)
    ax.figure.canvas.draw()
    return


def h_axis(ax, coordinates, color='k', alpha=0.3):
    if coordinates == 'hhr':
        ax.add_line(ml.Line2D(xdata=ax.get_xlim(), ydata=(0, 0), color=color, alpha=alpha))
    elif coordinates == 'hchb':
        ax.add_line(ml.Line2D(xdata=ax.get_xlim(), ydata=-1*np.array(ax.get_xlim()), color=color, alpha=alpha))
    else:
        raise ValueError('Invalid coordinates: {}'.format(coordinates))
    ax.figure.canvas.draw()
    return


def hr_axis(ax, coordinates, color='k', alpha=0.3):
    if coordinates == 'hhr':
        ax.add_line(ml.Line2D(xdata=(0, 0), ydata=ax.get_ylim(), color=color, alpha=alpha))
    elif coordinates == 'hchb':
        ax.add_line(ml.Line2D(xdata=ax.get_xlim(), ydata=ax.get_xlim(), color=color, alpha=alpha))
    else:
        raise ValueError('Invalid coordinates: {}'.format(coordinates))
    ax.figure.canvas.draw()
    return


def hc_axis(ax, coordinates, color='k', alpha=0.3):
    if coordinates == 'hhr':
        ax.add_line(ml.Line2D(xdata=ax.get_xlim(), ydata=-1*np.array(ax.get_xlim()), color=color, alpha=alpha))
    elif coordinates == 'hchb':
        ax.add_line(ml.Line2D(xdata=ax.get_xlim(), ydata=(0, 0), color=color, alpha=alpha))
    else:
        raise ValueError('Invalid coordinates: {}'.format(coordinates))
    ax.figure.canvas.draw()
    return


def hb_axis(ax, coordinates, color='k', alpha=0.3):
    if coordinates == 'hhr':
        ax.add_line(ml.Line2D(xdata=ax.get_xlim(), ydata=ax.get_xlim(), color=color, alpha=alpha))
    elif coordinates == 'hchb':
        ax.add_line(ml.Line2D(xdata=(0, 0), ydata=ax.get_ylim(), color=color, alpha=alpha))
    else:
        raise ValueError('Invalid coordinates: {}'.format(coordinates))
    ax.figure.canvas.draw()
    return


def colorbar(ax, im):
    """Generate a sensible looking colorbar for an image. Removes any colorbars currently drawn by removing
    all but one axes instance from the figure containing ax.

    Parameters
    ----------
    ax : axes
        Axes instance to draw the colorbar on. The colorbar is placed to the right of the axes, and is vertically
        oriented.
    im : mappable
        Image, ContourSet, etc to generate the colorbar for.
    """

    while len(ax.figure.axes) > 1:
        ax.figure.delaxes(ax.figure.axes[-1])

    cax = mpltkag1.make_axes_locatable(ax).append_axes("right", size="5%", pad=0.05)
    cbar = ax.get_figure().colorbar(im, cax=cax)
    cbar.locator = mt.MaxNLocator(nbins=6)
    cbar.formatter.set_powerlimits((0, 0))
    cbar.update_ticks()
    return
