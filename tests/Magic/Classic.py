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

from Redy.Magic.Classic import cast
@cast(list)
def f(x):
    for each in x:
        if each % 2:
            continue
        yield each

from Redy.Magic.Classic import execute
x = 1
@execute
def f(x) -> int:
    return x + 1
assert f is 2

from Redy.Magic.Classic import record
class Interface: pass
@record
class S(Interface):
    name: str
    addr: str
    sex : int
s = S("sam", "I/O", 1)