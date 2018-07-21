from Redy.Typing import *

import unittest
import pytest
class Test_Redy_ADT_Core(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def test_2427484236440(self):
        from Redy.ADT.Core import data
        from Redy.Magic.Classic import cast
        from Redy.ADT.traits import ConsInd, Discrete
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



        from Redy.ADT.Core import match, data, P
        from Redy.ADT.traits import ConsInd, Discrete
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

        from Redy.ADT.Core import RDT
        from Redy.ADT.traits import ConsInd
        @data
        class MyDT(ConsInd):
            P: RDT[lambda raw_input: ((1, raw_input), str(raw_input))]
        p = MyDT.P("42")
        assert p[1] is 1
        assert p[2] == "42"