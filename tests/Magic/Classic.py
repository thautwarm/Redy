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

from Redy.Magic.Classic import data, cast
@data
class S:
   a: '1'
   b: lambda x: x
   c: lambda x, y : ...
assert isinstance(S.a, S)
assert isinstance(S.b('2'), S)
assert S.b('2').__str__() == 'S[2]'
assert S.c(1, 2)[:] == (S.c, 1, 2)
@data
class Nat:
    Zero : ...
    Succ : lambda o: ...
    def _to_nat(self):
        if self is Nat.Zero:
            return 0
        return 1 + self[1]._to_nat()
    @cast(str)
    def __str__(self):
        return f'Nat[{self._to_nat()}]'
print (Nat.Succ((Nat.Succ(Nat.Zero))))
assert Nat.Zero == Nat.Zero
assert len({Nat.Zero, Nat.Succ(Nat.Zero), Nat.Succ(Nat.Zero)}) is 2

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

from Redy.Magic.Classic import match, data, P
@data
class List:
    Nil : ...
    Cons: lambda head, tail: ...
lst = List.Cons(2, List.Cons(1, List.Nil))
mode_lst = P[List.Cons, P, P[List.Cons, 1]]
if match(mode_lst,  lst):
    assert mode_lst == [List.Cons, 2, [List.Cons, 1]]

