import numpy as np
import numba as nb


@nb.jit(nb.float64[:, :](nb.float64[:, :], nb.float64[:, :]), nopython=True)
def fast_symmetric_convolve(input, kernel):
    result = np.empty_like(input, dtype=np.float64)*np.nan
    sf_y, sf_x = (kernel.shape[0]-1)//2, (kernel.shape[1]-1)//2
    for i in range(sf_y, input.shape[0]-sf_y):
        for j in range(sf_x, input.shape[1]-sf_x):
            result[i, j] = 0
            for m in range(-sf_y, sf_y+1):
                for n in range(-sf_x, sf_x+1):
                    result[i, j] += input[i+m, j+n]*kernel[m+sf_y, n+sf_x]

    return result
