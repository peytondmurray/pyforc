import numpy as np
import numba as nb

import hypothesis


@nb.jit(nb.float64[:, :](nb.float64[:, :], nb.float64[:, :]), nopython=True, nogil=True)
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


# @nb.jit(nb.float64(nb.float64, nb.float64, nb.float64), nopython=True, nogil=True)
@nb.jit(nopython=True, nogil=True)
def line(x, a, b):
    return a*x+b


# @nb.jit(nb.int64(nb.float64[:]), nopython=True, nogil=True)
# @nb.jit(nopython=True, nogil=True)
def arg_first_not_nan(arr):
    i = np.argwhere(np.logical_not(np.isnan(arr)))
    print(type(i))
    if i.shape[0] == 0:
        raise ValueError("Array is only filled with nan values")
    else:
        return i[0][0]


# @nb.jit(nb.int64(nb.float64[:]), nopython=True, nogil=True)
# @nb.jit(nopython=True, nogil=True)
def arg_last_non_nan(arr):
    return arr.shape[0] - 1 - arg_first_not_nan(np.flip(arr, 0))


# nb_argwhere and nb_where are potentially faster than numpy's equivalent functions, but have not been validated.
# Use with caution.
@nb.jit(nopython=True, nogil=True)
def nb_argwhere(arr):
    is_nonzero = nb_where(arr)
    ret = np.empty((1, np.sum(is_nonzero)))
    j = 0
    for i in range(arr.shape[0]):
        if is_nonzero[i]:
            ret[j] = i
            j += 1
    return ret


@nb.jit(nopython=True, nogil=True)
def nb_where(arr):
    ret = np.empty_like(arr)
    for i in range(arr.shape[0]):
        ret[i] = True if arr[i] != 0 else False
    return ret
