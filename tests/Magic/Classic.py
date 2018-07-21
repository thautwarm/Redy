from Redy.Typing import *

import unittest
import pytest
class Test_Redy_Magic_Classic(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def test_2170699674952(self):
        from Redy.Magic.Classic import template
        import operator
        class Point:
           def __init__(self, p):
                assert isinstance(p, tuple) and len(p) is 2
                self.x, self.y = p
        def some_metrics(p: Point):
            return p.x + 2 * p.y
        @template
        def comp_on_metrics(self: Point, another: Point, op):
               if not isinstance(another, Point):
                    another = Point(another)
               return op(*map(some_metrics, (self, another)))
        class Space(Point):
           @comp_on_metrics(op=operator.lt)
           def __lt__(self, other):
               ...
           @comp_on_metrics(op=operator.eq)
           def __eq__(self, other):
               ...
           @comp_on_metrics(op=operator.gt)
           def __gt__(self, other):
               ...
           @comp_on_metrics(op=operator.le)
           def __le__(self, other):
               ...
           @comp_on_metrics(op=operator.ge)
           def __ge__(self, other):
               ...
        p = Space((0, 1))
        p >   (1, 2)
        p <   (3, 4)
        p >=  (5, 6)
        p <=  (7, 8)
        p ==  (9, 10)

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
        def f(x = x) -> int:
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