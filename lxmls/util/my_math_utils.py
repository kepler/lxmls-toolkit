import numpy as np

import operator
from builtins import range
from scipy.sparse.base import issparse


def sort_dic_by_value(dic, reverse=False):
    return sorted(iter(list(dic.items())), key=operator.itemgetter(1), reverse=reverse)


# Maximum value of a dictionary
def dict_max(dic):
    aux = dict([(item[1], item[0]) for item in list(dic.items())])
    if not list(aux.keys()):
        return 0
    max_value = max(aux.keys())
    return max_value, aux[max_value]


def spdot(A, B):
    """
    The same as np.dot(A, B), except it works even if A or B or both might be sparse.

    Dot products that works for sparse matrix as well
    Taken from:
    http:// old.nabble.com/Sparse-matrices-and-dot-product-td30315992.html
    """
    if issparse(A) and issparse(B):
        return A * B
    elif issparse(A) and not issparse(B):
        return (A * B).view(type=B.__class__)
    elif not issparse(A) and issparse(B):
        return (B.T * A.T).T.view(type=A.__class__)
    else:
        return np.dot(A, B)


def perp_2d(a):
    """Gets a perpendicular line in 2D."""
    res = 1. / a
    res = res[:, ] * [-1, 1]
    return res


def l2norm(a):
    value = 0
    for i in range(a.shape[1]):
        value += np.dot(a[:, i], a[:, i])
    return np.sqrt(value)


def l2norm_squared(a):
    value = 0
    for i in range(a.shape[1]):
        value += np.dot(a[:, i], a[:, i])
    return value


def normalize_array(a, direction="column"):
    """
    Normalizes an array to sum to one, either column wize, or row wize or the full array.
    Column wize - 0 default
    Rown wize - 1 default
    All - 2 default
    """
    b = a.copy()
    if direction == "column":
        sums = np.sum(b, 0)
        return np.nan_to_num(b / sums)
    elif direction == "row":
        sums = np.sum(b, 1)
        return np.nan_to_num((b.transpose() / sums).transpose())
    elif direction == "all":
        sums = np.sum(b)
        return np.nan_to_num(b / sums)
    else:
        print("Error non existing normalization")
        return b
