from Redy.Types import *


from Redy.Collections.Core import *
def i2f(x: int) -> float: return x * 1.0
def f2s(x: float) -> str: return str(x)
def s2f(x: str) -> float: return float(x)
def f2i(x: float) -> int: return int(x)
def i2s(x: int) -> str:   return str(x)
z = Monad(i2f)
d = z[
    f2s
][
    s2f
][
    f2i
][
    i2s
]
_ = d.call(1)
print(_)
assert _.__class__ is str
assert Monad(())(...) is None
print('__call__', Monad(())(...))