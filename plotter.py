import matplotlib.cm as cm
import matplotlib.lines as ml
import matplotlib.collections as mc
import numpy as np


def h_vs_m(ax, forc, mask='outline', points='none', cmap='viridis'):

    colors = [cm.get_cmap('viridis')(x) for x in np.linspace(0, 0.4, forc.shape[0])]

    if mask is True:
        for i in range(forc.shape[0]):
            h = forc.h[i]
            m = forc.m[i]
            ax.add_line(ml.Line2D(xdata=h[h >= forc.hr[i, 0]],
                                  ydata=m[h >= forc.hr[i, 0]],
                                  color=colors[i]))
    else:
        for i in range(forc.shape[0]):
            h = forc.h[i]
            m = forc.m[i]
            ax.add_line(ml.Line2D(xdata=h,
                                  ydata=m,
                                  color=colors[i]))

        if mask == 'outline':
            h, hr, m = forc.major_loop()
            ax.plot(h, m, ':', color='r', linewidth=2, alpha=1.0)

    if points == 'reversal':
        hr = forc.hr[:, 0]
        m = np.zeros_like(forc.hr[:, 0])
        for i in range(forc.shape[0]):
            m[i] = forc.m[i, forc.h[i] >= forc.hr[i, 0]][0]

        ax.plot(hr, m, marker='o', linestyle='', color='grey', markersize=4)

    ax.autoscale_view()
    ax.set(xlabel=r"$H$",
           ylabel=r"$H_r$")

    return


def hhr_space_h_vs_m(ax, forc):
    h, hr, m = forc.major_loop()
    ax.plot(h, hr, marker='.', linestyle='', color='k', markersize=12, alpha=0.3)
    return


def h_hr_points(ax, forc):
    ax.plot(forc.h, forc.hr, marker='.', linestyle='', color='k', alpha=0.3)
    return