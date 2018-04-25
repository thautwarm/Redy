GADT
=======================


.. code :: python

    from Redy.GADT.Core import *
    from Redy.GADT.traits import Ord, Discrete, ConsInd


    @data
    class Nat(Discrete, Ord, ConsInd):
        Zero: ...
        Succ: lambda o: ...

        def __eq__(self, other):
            if not isinstance(other, Nat):
                return False

            if self is Nat.Zero:
                return other is Nat.Zero
            if other is Nat.Zero:
                return False
            return other[1] == self[1]

        def __le__(self, other):
            assert isinstance(other, Nat)

            if self is Nat.Zero:
                return True
            elif other is Nat.Zero:
                return True
            else:
                return self[1] <= other[1]

        def __lt__(self, other):
            assert isinstance(other, Nat)

            if self is Nat.Zero:
                return other is not Nat.Zero
            elif other is Nat.Zero:
                return False
            else:
                return self[1] < other[1]


    assert isinstance(Nat.Zero, Nat)  # => True

    _1 = Nat.Succ(Nat.Zero)
    _2 = Nat.Succ(_1)
    _3 = Nat.Succ(_2)

    assert (_3 > _2 > _1)

    assert _3 == _3

    assert _3 != 2

