import unittest
from tests.test_constexpr import *
from tests.test_goto import *

class TestAll(unittest.TestCase):
    def test_all(self):
        from tests.Collections import Traversal, Core, Graph, LinkedList
        from tests.Async import Accompany, Delegate
        from tests.Tools import PathLib, Version, TypeInterface
        from tests.Magic import Pattern, Classic
        from tests.ADT import Core
        from tests.Opt import ConstExpr
        from tests import test_macro

