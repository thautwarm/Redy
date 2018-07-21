from Redy.Typing import *

import unittest
import pytest
class Test_Redy_Tools_TypeInterface(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def test_2170699674312(self):


        from Redy.Tools.TypeInterface import Module
        import math
        assert isinstance(math, Module)

        from Redy.Tools.TypeInterface import BuiltinMethod
        class S: ...
        assert isinstance(S.__init__, BuiltinMethod)