from Redy.Typing import *


from Redy.GADT.Core import data
from Redy.Magic.Classic import cast
from Redy.GADT.traits import *
@data
class S(ConsInd):  # ConsInd class makes it available to index from this data as from a tuple.
   a: '1'
   b: lambda x: x
   c: lambda x, y : ...
assert isinstance(S.a, S)
assert isinstance(S.b('2'), S)
assert S.b('2').__str__() == '(2)'
assert S.c(1, 2)[:] == (S.c, 1, 2)  # here `ConsInd` works!
@data
class Nat(Discrete, ConsInd):
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



from Redy.GADT.Core import match, data, P
@data
class List(ConsInd, Discrete):
    # ConsInd(index following constructing)
    #    |-> Ind;
    # Discrete
    #    |-> Im(Immutable), Eq
    Nil : ...
    Cons: lambda head, tail: ...
lst = List.Cons(2, List.Cons(1, List.Nil))
mode_lst = P[List.Cons, P, P[List.Cons, 1]]
if match(mode_lst,  lst):
    assert mode_lst == [List.Cons, 2, [List.Cons, 1]]