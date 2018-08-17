import sys
if sys.version_info < (3, 6):
    ModuleNotFoundError = ImportError
from ..settings import numba_hash

if numba_hash:
    try:
        import numpy as np
        from ._native_hash import *
    except ModuleNotFoundError as e:
        import warnings
        warnings.warn(
            "No NumPy package found, the standard hashing algorithm wouldn't be used for truncating in Python costs too much.",
            ImportWarning)
        from ._py_hash import *
else:
    from ._py_hash import *

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
