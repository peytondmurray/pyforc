# Tests for PyFORC

import pytest
import sys
import main
import Forc
import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.cm as cm
# import matplotlib.collections as mc
import bokeh.plotting as bp
import bokeh.models.mappers as bmm


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
    data = Forc.PMCForc('./test_data/test_forc',
                        step=35,
                        drift=False)

    bp.output_file("test_fig.html")
    # plot = bp.figure(title="FORCs",
    #                  x_axis_label='H',
    #                  y_axis_label='M')

    # for i in range(data.shape[0]):
    #     plot.line(data.h[i], data.m[i], line_width=2)

    # bp.show(plot)

    plot = bp.figure(x_range=data.h_range(),
                     y_range=data.hr_range(),
                     toolbar_location=None)

    color_mapper = bmm.LinearColorMapper(palette='Viridis256',
                                         low=data.m_range()[0],
                                         high=data.m_range()[1])

    plot.image(image=[data.m],
               color_mapper=color_mapper,
               dh=[1],
               dw=[1],
               x=[0],
               y=[0])

    bp.show(plot)

    return


if __name__ == '__main__':
    # test_gui()
    test_PMCForc_import()
