from Redy.Opt import *
from dis import dis
import pytest
import unittest


class TestMacro(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def test_macro(self):
        macro = Macro()

        @feature(macro)
        def macro_example(x):
            @macro.stmt
            def just_return(v):
                return v

            just_return(1)

        def test_macro():
            @macro.stmt
            def print_some_and_return_1(s):
                print(s)
                return 1

            @feature(macro)
            def macro_example2():
                print_some_and_return_1("abcdefg")

            dis(macro_example)
            dis(macro_example2)

            print(macro_example(1))
            macro_example2()

        test_macro()


if __name__ == '__main__':
    unittest.main()
