ADT
=======================


Preview
-----------------

* Natural Number

.. code :: python

    from Redy.ADT.Core import data
    from Redy.ADT.traits import Ord, Discrete, ConsInd


    @data
    class Nat(Discrete, Ord, ConsInd):
        Zero: ...
        Succ: lambda o: ...

        def __eq__(self, other):
            assert isinstance(other, Nat)
            if self is Nat.Zero:
                return other is Nat.Zero
            if other is Nat.Zero:
                return False
            return other[1] == self[1]

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

    assert _3 != _2


* LinkedList


.. code :: python

    from Redy.ADT.Core import data
    from Redy.ADT import traits

    @data
    class List(traits.ConsInd, traits.Dense, traits.Im):
        Nil : ...
        Cons: lambda head, tail: f'{head}, {tail}'

        def __lshift__(self, value):
            return List.Cons(value, self)

    print(List.Nil)
    print(isinstance(List.Nil, List))
    print(List.Nil << 1 << 2 << 3)

Output:

.. code :: shell


    (Nil)
    True
    (3, (2, (1, (Nil))))


You might notice that :code:`traits` here are unfamiliar and kind of strange, however it's significant to design
datatypes without detailed features and describe them.

For example, :code:`traits.ConsInd`, which is short for "constructing indexing"
and enables accessing patterns of data structures by indexing.

.. code :: python


    lst = List.Cons(1, (List.Cons(2, List.Nil)))
    assert lst[0] is List.Cons  # pass
    assert lst[1] is 1  # pass
    assert lst[2] == List.Cons(2, List.Nil)  # pass


And trait :code:`Im` is short for "Immutable", just as this trait suggested,
the immutable data could not be updated in place,
on the other hand, immutable data is hashable and could be used as the key of hashdict.


