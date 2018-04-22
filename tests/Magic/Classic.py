from Redy.Typing import *


from Redy.Magic.Classic import singleton
@singleton
class S:
    pass
assert isinstance(S, S)

from Redy.Magic.Classic import const_return
@const_return
def f(x):
    return x
r1 = f(1)
assert r1 is 1 and r1 is f(2)