from collections import Iterable


def to_int64(x):
    return (x & 0xffffffffffffffff) - ((x & 0x8000000000000000) << 1)


def hash_from_stream(n, hash_stream):
    """
    Not standard hashing algorithm!
    Install NumPy for better hashing service.
    >>> from Redy.Tools._py_hash import hash_from_stream
    >>> s = iter((1, 2, 3))
    >>> assert hash_from_stream(3, map(hash, s)) == hash((1, 2, 3))

    """
    _to_int64 = to_int64
    x = 0x345678
    multiplied = _to_int64(1000003)
    for n in range(n - 1, -1, -1):
        h = next(hash_stream)
        x = _to_int64((x ^ h) * multiplied)
        multiplied += _to_int64(82520 + _to_int64(2 * n))
        multiplied = _to_int64(multiplied)

    x += 97531
    x = _to_int64(x)
    if x == -1:
        return -2

    return x


class HashCalculator:
    """
        >>> from Redy.Tools._py_hash import HashCalculator
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

    def extensive_collect(self, n: int, stream: Iterable):
        return _extensive_collect_from_existed_hashes(self.hashes, n, stream)

    def collect(self):
        return _collect_from_existed_hashes(self.hashes)


def _collect_from_existed_hashes(hashes):
    _to_int64 = to_int64
    x = 0x345678
    multiplied = _to_int64(1000003)
    n = len(hashes)
    for h in hashes:
        n -= 1
        x = _to_int64((x ^ h) * multiplied)
        multiplied += _to_int64(82520 + _to_int64(2 * n))
        multiplied = _to_int64(multiplied)

    x += 97531
    x = _to_int64(x)
    if x == -1:
        return -2

    return x


def _extensive_collect_from_existed_hashes(hashes, n, stream):
    _to_int64 = to_int64
    n += len(hashes)

    x = 0x345678
    multiplied = 1000003
    n = len(hashes)
    for h in hashes:
        n -= 1
        x = _to_int64((x ^ h) * multiplied)
        multiplied += _to_int64(82520 + _to_int64(2 * n))
        multiplied = _to_int64(multiplied)

    for e in stream:
        n -= 1
        h = hash(e)
        if h is -1:
            return -1
        x = _to_int64((x ^ h) * multiplied)
        multiplied += _to_int64(82520 + _to_int64(2 * n))
        multiplied = _to_int64(multiplied)

    x += 97531
    x = _to_int64(x)
    if x == -1:
        return -2
    return x


