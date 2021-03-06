from Redy.Typing import *

import unittest
import pytest
class Test_Redy_Magic_Pattern(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def test_2309575515096(self):
        from Redy.Magic.Pattern import Pattern
        @Pattern
        def f(x):
            return type(x)
        @f.match(int)
        def f(x):
            return 1 + x
        @f.match(any)
        def f(x):
            return '1' + str(x)
        print(f(1), f('1'))
        from Redy.Magic.Pattern import Pattern
        equal = lambda x: 2 * x - x ** 2 - 1
        @Pattern
        def f(x):
            return -10e-3 < equal(x) <= 10e-3
        @f.match(False)
        def f(x):
            print("Not the solution.")
        @f.match(True)
        def f(x):
            return x
        print(f(1))
        from Redy.Magic.Pattern import Pattern
        @Pattern
        def f(x):
          return str
        @f.match(int)
        def f(x):
            return  x
        try:
            print(f(1))
        except TypeError:
            pass