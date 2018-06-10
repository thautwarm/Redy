from Redy.Typing import *


from Redy.Opt.ConstExpr import constexpr, const, optimize
import dis
a = 1; b = ""; c = object()
x = 1
@optimize
def f(y):
    val1: const[int] = a
    val2: const = b
    if constexpr[x is c]:
        return val1, y
    elif constexpr[x is 1]:
        return None, y
    else:
        return val2, y
assert f(1) == (None, 1)
dis.dis(f)