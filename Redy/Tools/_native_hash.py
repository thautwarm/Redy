from collections import Iterable
import numpy as np

to_int64 = np.int64

np.seterr(over='ignore')
try:
    import numba as nb

    dec = nb.jit
except ModuleNotFoundError:
    def dec(f):
        return f


def _cast(cast_fn):
    def wrap(func):
        def call(*args):
            return cast_fn(func(*args))

        return call

    return wrap


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


@_cast(int)
@dec
def hash_from_stream(n, hash_stream):
    """
    >>> from Redy.Tools.Hash import hash_from_stream
    >>> s = iter((1, 2, 3))
    >>> assert hash_from_stream(3, iter(s)) == hash((1, 2, 3))

    """
    x = to_int64(0x345678)
    multiplied = to_int64(1000003)
    for i in range(n - 1, -1, -1):
        h = next(hash_stream)
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

    def take(self, *it):
        for each in it:
            h = hash(each)
            if h is -1:
                return -1
            self.hashes.append(h)

    @_cast(int)
    def extensive_collect(self, n: int, stream: Iterable):
        return _extensive_collect_from_existed_hashes(self.hashes, n, stream)

    def collect(self):
        return _collect_from_existed_hashes(self.hashes)


@_cast(int)
@dec
def _collect_from_existed_hashes(hashes):
    x = to_int64(0x345678)
    multiplied = to_int64(1000003)
    n = len(hashes)
    for h in hashes:
        n -= 1
        x = (x ^ h) * multiplied
        multiplied += to_int64(82520 + 2 * n)
    x += 97531

    if x == -1:
        return -2

    return x


@_cast(int)
@dec
def _extensive_collect_from_existed_hashes(hashes, n, stream):
    n += len(hashes)
    x = to_int64(0x345678)
    multiplied = to_int64(1000003)
    n = len(hashes)
    for h in hashes:
        n -= 1
        x = (x ^ h) * multiplied
        multiplied += to_int64(82520 + 2 * n)
    for e in stream:
        n -= 1
        h = hash(e)
        if h is -1:
            return -1
        x = (x ^ h) * multiplied
        multiplied += to_int64(82520 + 2 * n)
    x += 97531

    if x == -1:
        return -2
    return x
