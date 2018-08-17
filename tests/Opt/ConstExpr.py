from Redy.Typing import *

import unittest
import pytest
class Test_Redy_Opt_ConstExpr(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def test_2309576264824(self):
        from Redy.Opt.ConstExpr import constexpr, const, optimize, macro
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
        @optimize
        def f(x):
            d: const = 1
            return x + d + constexpr[2]
        dis.dis(f)
        print('result:', f(1))
        @optimize
        def f(z):
            @macro
            def g(a):
                x = a + 1
            g(z)
            return x
        dis.dis(f)
        print('result:', f(1))
        c = 10
        @optimize
        def f(x):
            if constexpr[1 + c < 10]:
                return x + 1
            else:
                return x - 1
        print(dis.dis(f))
        print(f(5))
        @optimize
        def f(x):
            return (x + constexpr[c * 20]) if constexpr[c > 10] else  constexpr[c - 2]
        dis.dis(f)
        print(f(20))
        def g(lst: list):
           k = 1
           @optimize
           def _():
               nonlocal k
               f: const = lst.append
               for i in range(1000):
                   f(i)
               k += 1
               f(k)
           _()
           return lst
        # dis.dis(g)
        print(g([]))