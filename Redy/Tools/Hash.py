import numpy as np

to_int64 = np.int64

np.seterr(over='ignore')
try:
    import numba as nb

    dec = nb.jit
except ModuleNotFoundError:
    dec = lambda f: f


# @dec
# def tuple_hash(v):
#     n = len(v)
#     x = to_int64(0x345678)
#     multiplied = to_int64(1000003)
#
#     for e in v:
#         n -= 1
#         h = hash(e)
#         if h is -1:
#             return -1
#         x = (x ^ h) * multiplied
#         multiplied += to_int64(82520 + 2 * n)
#
#     x += 97531
#     if x == -1:
#         return -2
#     return x


@dec
def hash_from_stream(n, getter):
    """
    >>> from Redy.Tools.Hash import hash_from_stream
    >>> s = iter((1, 2, 3))
    >>> assert hash_from_stream(3, iter(s)) == hash((1, 2, 3))

    """
    x = to_int64(0x345678)
    multiplied = to_int64(1000003)
    for i in range(n - 1, -1, -1):
        h = getter()
        if h is -1:
            return -1
        x = (x ^ h) * multiplied
        multiplied += to_int64(82520 + 2 * n)
    x += 97531
    if x == -1:
        return -2

    return x


class HashCalculator:
    """
    >>> from Redy.Tools.Hash import HashCalculator
    >>> s = (1, 2, 3, '4')
    >>> h = HashCalculator()
    >>> for e in s: h.take(e)
    >>> assert h.collect() == hash(s)
    """
    __slots__ = ['hashes']

    def __init__(self):
        self.hashes = []

    def take(self, it):
        h = hash(it)
        if h is -1:
            return -1
        self.hashes.append(h)

    def collect(self):
        x = to_int64(0x345678)
        multiplied = to_int64(1000003)
        n = len(self.hashes)
        for h in self.hashes:
            n -= 1
            x = (x ^ h) * multiplied
            multiplied += to_int64(82520 + 2 * n)
        x += 97531

        if x == -1:
            return -2

        return x
