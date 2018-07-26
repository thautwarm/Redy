from Redy.Opt import *
import unittest
import pytest


class TestAsStore(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def test_as_store(self):
        macro = Macro()

        @macro.stmt
        def assign(k, v):
            k = v

        @feature(macro, as_store)
        def f():
            name = 1
            assign(as_store[name], 2)

            return name

        self.assertEqual(f(), 2)


if __name__ == '__main__':
    unittest.main()
