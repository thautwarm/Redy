from Redy.Typing import *

import unittest
class Test_Redy_Tools_TypeInterface(unittest.TestCase):
    def test_1722268480200(self):


        from Redy.Tools.TypeInterface import Module
        import math
        assert isinstance(math, Module)

        from Redy.Tools.TypeInterface import BuiltinMethod
        class S: ...
        assert isinstance(S.__init__, BuiltinMethod)