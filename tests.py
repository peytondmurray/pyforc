# Tests for PyFORC

import pytest
import sys
import main
import Forc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.collections as mc


@pytest.mark.skip
def test_gui():
    sys.argv = ['main.py',
                'gui']
    main.parse_arguments()
    return


@pytest.mark.skip
def test_Forc():
    Forc.PMCForc('./test_data/test_forc')
    return


def test_PMCForc_import():
    data = Forc.PMCForc('./test_data/test_forc')
    n_forcs = len(data.h)
    colors = [cm.viridis(x) for x in np.linspace(0.6, 0, n_forcs)]

    fig = plt.figure()
    ax = fig.add_subplot(111)

    lines = mc.LineCollection([list(zip(data.h[i], data.m[i])) for i in range(len(data.h))], colors=colors)

    ax.add_collection(lines)
    ax.autoscale()
    ax.margins(0.1)
    # for i in range(n_forcs):
    #     lines.append([data.h[i], data.m[i], {'linestyle': '-', 'color': colors[i]}])

    # plt.plot(*lines)

    plt.show()


if __name__ == '__main__':
    # test_gui()
    test_PMCForc_import()
