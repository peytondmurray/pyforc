import matplotlib.cm as cm
import matplotlib.lines as ml
import matplotlib.collections as mc
import matplotlib.ticker as mti
import mpl_toolkits.axes_grid1 as mpltkag1
import matplotlib.tri as mtri
import matplotlib.pyplot as plt
import matplotlib.transforms as mtra
import numpy as np
import util


def h_vs_m(ax, forc, mask='h<hr', points='none', cmap='viridis', alpha=1.0):

    mask = mask.lower()
    points = points.lower()
    cmap = cmap.lower()

    if cmap == 'none':
        colors = ['k' for _ in range(forc.shape[0])]
    else:
        cmap = cm.get_cmap(cmap)
        colors = [cmap(x) for x in np.linspace(0, 0.4, forc.shape[0])]

    if points in ['none', 'reversal']:

        if mask.lower() == 'h<hr':
            for i in range(forc.shape[0]):
                h = forc.h[i]
                m = forc.m[i]
                ax.add_line(ml.Line2D(xdata=h[h >= forc.hr[i, 0]],
                                      ydata=m[h >= forc.hr[i, 0]],
                                      color=colors[i],
                                      alpha=alpha))
        elif mask in ['outline', 'none']:
            for i in range(forc.shape[0]):
                ax.add_line(ml.Line2D(xdata=forc.h[i],
                                      ydata=forc.m[i],
                                      color=colors[i],
                                      alpha=alpha))

            if mask == 'outline':
                h, hr, m = forc.major_loop()
                ax.add_line(ml.Line2D(xdata=h,
                                      ydata=m,
                                      linestyle=':',
                                      color='r',
                                      linewidth=2,
                                      alpha=alpha))
        else:
            raise ValueError('Invalid mask argument: {}'.format(mask))

        if points == 'reversal':
            hr = forc.hr[:, 0]
            m = np.zeros_like(forc.hr[:, 0])
            for i in range(forc.shape[0]):
                m[i] = forc.m[i, forc.h[i] >= forc.hr[i, 0]][0]

            ax.add_line(ml.Line2D(xdata=hr,
                                  ydata=m,
                                  marker='o',
                                  linestyle='',
                                  color='grey',
                                  markersize=4,
                                  alpha=alpha))

        elif points == 'all':
            ax.add_line(ml.Line2D(xdata=forc.h,
                                  ydata=forc.m,
                                  marker='o',
                                  linestyle='',
                                  color='grey',
                                  markersize=4,
                                  alpha=alpha))

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
    data = forc.get_masked(forc.get_data(data_str), mask)
    vmin, vmax = symmetrize_bounds(np.nanmin(data), np.nanmax(data))
    im = ax.imshow(data,
                   extent=forc.get_extent('hhr'),
                   cmap=cmap,
                   origin='lower',
                   interpolation=interpolation,
                   vmin=vmin,
                   vmax=vmax)
    if coordinates == 'hchb':
        im.set_transform(hhr_to_hchb_transform() + ax.transData)
    colorbar(ax, im)
    set_map_limits(ax, mask, coordinates)
    ax.figure.canvas.draw()
    return


def contour_map(ax, forc, data_str, mask, coordinates, interpolation='nearest', cmap='RdBu_r', levels=None):
    ax.clear()
    data = forc.get_masked(forc.get_data(data_str), mask)
    vmin, vmax = symmetrize_bounds(np.nanmin(data), np.nanmax(data))
    im = ax.contourf(data,
                     extent=forc.get_extent('hhr'),
                     cmap=cmap,
                     origin='lower',
                     levels=levels,
                     vmin=vmin,
                     vmax=vmax)
    if coordinates == 'hchb':
        im.set_transform(hhr_to_hchb_transform() + ax.transData)
    colorbar(ax, im)
    set_map_limits(ax, mask, coordinates)
    ax.figure.canvas.draw()
    return


def contour_levels(ax, forc, data_str, mask, coordinates, levels=None):

    # TODO this might not work with 'transform' keyword

    if coordinates == 'hhr':
        transform = ax.transData
    elif coordinates == 'hchb':
        transform = hhr_to_hchb_transform() + ax.transData
    else:
        raise ValueError('Invalid coordinates type.')

    ax.contour(forc.get_masked(forc.get_data(data_str), mask),
               extent=forc.get_extent('hhr'),
               origin='lower',
               levels=levels,
               colors='k',
               transform=transform)
    set_map_limits(ax, mask, coordinates)
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
    cbar.locator = mti.MaxNLocator(nbins=6)
    cbar.formatter.set_powerlimits((0, 0))
    cbar.update_ticks()
    return


def map_into_curves(ax, forc, data_str, mask, interpolation=None, cmap='RdBu_r'):
    """Plots a quantity into the reversal curves in (H, M) space.

    Parameters
    ----------
    ax : Axes
        Axes to plot the map on
    forc : Forc
        Forc instance containing relevant data
    data_str : str
        One of ['m', 'rho', 'rho_uncertainty', 'temperature']
    mask : str or bool
        True or 'H<Hr' will mask any values for which H<Hr. False shows all data, including dataset extension.
    interpolation : str, optional
        Interpolates the map in the paths to make the map smooth. Not currently implemented.
        (the default is None, which doesn't interpolate.)
    cmap : str, optional
        Colormap to use. Choose from anything in matplotlib or colorcet.
        (the default is 'RdBu_r', which is a perceptually uniform diverging colormap good for M and rho values.)

    Raises
    ------
    NotImplementedError
        If interpolation is anything but the default None.
    """

    ax.clear()
    _h = forc.h.ravel()
    _m = forc.get_masked(forc.m, mask=mask).ravel()
    _z = forc.get_masked(forc.get_data(data_str), mask=mask).ravel()

    # The sum of a nan and anything is a nan. This masks all nan elements across all three arrays.
    indices_non_nan = np.logical_not(np.isnan(_h+_m+_z))

    _h = _h[indices_non_nan]
    _m = _m[indices_non_nan]
    _z = _z[indices_non_nan]

    triang = mtri.Triangulation(_h, _m)
    tri_mask = triangulation_mask(_h, triang.triangles, max_edge_length=1.5*forc.step)
    triang.set_mask(tri_mask)

    if interpolation is None:
        pass
    elif interpolation == 'linear':
        # triang = mtri.LinearTriInterpolator(triang, z)
        raise NotImplementedError
        # TODO generate H-M meshgrid, remove anything outside the concave hull of the loop. Then feed into a
        # mtri.LinearTriInterpolator?
    elif interpolation in ['cubic', 'geom', 'min_E']:
        raise NotImplementedError

    vmin, vmax = symmetrize_bounds(np.nanmin(_z), np.nanmax(_z))
    im = ax.tripcolor(triang, _z, shading="gouraud", cmap=cmap, vmin=vmin, vmax=vmax)
    colorbar(ax, im)
    ax.figure.canvas.draw()

    h_vs_m(ax, forc, mask=mask, points='none', cmap='none', alpha=0.3)

    return


def triangulation_mask(h, triangles, max_edge_length):
    """Create a mask to apply to a triangulation. Without this, 2D delaunay triangulation on a (H, M) space Forc
    dataset results in a convex hull, filling in points outside the hysteresis loop (that weren't measured). This
    mask ensures that no triangles created by the delaunay triangulator have an edge length longer than the field
    step in (H, Hr) space, so only points next to each other in the H-direction can be connected.

    Parameters
    ----------
    h : ndarray
        1D array of H-values used to create the triangulation
    triangles : ndarray of 3-tuples
        Array of triangles. Each triangle is a 3-tuple of indices of points in the array used to create the
        triangulation. See matplotlib.tri.Triangulation.triangles
    max_edge_length : float
        This is the max edge length of any triangle in the H-direction. fieldstep < max_edge_length < 2*fieldstep
        for this to work.
    Returns
    -------
    ndarray
        Array of booleans corresponding to the triangles to mask.
    """

    mask = np.zeros(triangles.shape[0])

    for i, (a, b, c) in enumerate(triangles):
        d0 = h[a] - h[b]
        d1 = h[b] - h[c]
        d2 = h[c] - h[a]
        mask[i] = np.max(np.abs([d0, d1, d2])) > max_edge_length

    return mask


def symmetrize_bounds(vmin, vmax):
    """Takes a pair of floats, the min and max z-values of a 2D map. Returns a pair of floats centered about 0.
    If vmin is not negative and vmax is not positive, then no symmetrization is done.

    Parameters
    ----------
    vmin : float
        Min z value
    vmax : float
        Max z value
    Returns
    -------
    2-tuple of floats
        New (vmin, vmax) values for plotting.
    """

    if vmin < 0 and vmax > 0:
        largest_bound = np.nanmax(np.abs([vmin, vmax]))
        return (-largest_bound, largest_bound)
    else:
        return (vmin, vmax)


def hhr_to_hchb_transform():
    return mtra.Affine2D(matrix=np.array([[0.5, -0.5, 0], [0.5, 0.5, 0], [0, 0, 1]]))


def set_map_limits(ax, mask, coordinates):

    if mask is True or mask.lower() == 'h<hr':
        if coordinates == 'hhr':
            return
        if coordinates == 'hchb':
            ax.set_xlim([0, ax.get_xlim()[1]])

    return