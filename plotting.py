import matplotlib.cm as cm
import matplotlib.lines as ml
import matplotlib.collections as mc
import numpy as np


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
                ax.add_line(ml.Line2D(xdata=h[h >= forc.hr[i, 0]],
                                      ydata=m[h >= forc.hr[i, 0]],
                                      color=colors[i]))
        elif mask in ['outline', 'none']:
            for i in range(forc.shape[0]):
                h = forc.h[i]
                m = forc.m[i]
                ax.add_line(ml.Line2D(xdata=h,
                                      ydata=m,
                                      color=colors[i]))

            if mask == 'outline':
                h, hr, m = forc.major_loop()
                ax.plot(h, m, ':', color='r', linewidth=2, alpha=1.0)
        else:
            raise ValueError('Invalid mask argument: {}'.format(mask))

        if points == 'reversal':
            hr = forc.hr[:, 0]
            m = np.zeros_like(forc.hr[:, 0])
            for i in range(forc.shape[0]):
                m[i] = forc.m[i, forc.h[i] >= forc.hr[i, 0]][0]

            ax.plot(hr, m, marker='o', linestyle='', color='grey', markersize=4)

        elif points == 'all':
            ax.plot(forc.h, forc.m, marker='o', linestyle='', color='grey', markersize=4)

        ax.autoscale_view()
    else:
        raise ValueError('Invalid points argument: {}'.format(points))
    ax.figure.canvas.draw()
    return


def major_loop(ax, forc, color='k'):
    h, _, m = forc.major_loop()
    ax.plot(h, m, linestyle='-', color=color, marker='o')
    ax.figure.canvas.draw()
    return


def hhr_space_h_vs_m(ax, forc):
    h, hr, _ = forc.major_loop()
    ax.plot(h, hr, marker='.', linestyle='', color='k', markersize=12, alpha=0.3)
    ax.figure.canvas.draw()
    return


def hhr_points(ax, forc):
    ax.plot(forc.h, forc.hr, marker='.', linestyle='', color='k', alpha=0.3)
    ax.figure.canvas.draw()
    return


def hchb_points(ax, forc):
    ax.plot(forc.hc, forc.hb, marker='.', linestyle='', color='k', alpha=0.3)
    ax.figure.canvas.draw()
    return


def map_points(ax, forc, coordinates='hhr'):
    if coordinates == 'hhr':
        hhr_points(ax, forc)
    elif coordinates == 'hchb':
        hchb_points(ax, forc)
    else:
        raise ValueError('Invalid coordinates argument: {}'.format(coordinates))

    return


def rho_hhr(ax, forc, mask=True, cmap='RdBu_r', interpolation='nearest'):

    if mask:
        rho = forc.rho.copy()
        rho[forc.h <= forc.hr] = np.nan
    else:
        rho = forc.rho

    ax.imshow(rho,
              extent=forc.extent,
              cmap=cmap,
              origin='lower',
              interpolation=interpolation)
    ax.figure.canvas.draw()
    return


def m_hhr(ax, forc, mask=True, cmap='RdBu_r', interpolation='nearest'):

    if mask:
        m = forc.m.copy()
        m[forc.h <= forc.hr] = np.nan
    else:
        m = forc.m

    ax.imshow(m,
              extent=forc.extent,
              cmap=cmap,
              origin='lower',
              interpolation=interpolation)

    ax.figure.canvas.draw()
    return


def hhr_line(ax, forc):
    ax.plot(forc.hr_range(), forc.hr_range(), linestyle='-', color='k')
    ax.draw(ax.get_figure().canvas.renderer)
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
