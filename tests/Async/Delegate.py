from Redy.Typing import *

import unittest
import pytest
class Test_Redy_Async_Delegate(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def test_2170718397688(self):
        from Redy.Async.Delegate import Delegate
        action = lambda task, product, globals: print(task.__name__)
        delegate = Delegate(action)
        def action2(task, product, globals):
            print(product)
        delegate.insert(action2, Delegate.Where.after(lambda _: False))
        delegate.insert(action, Delegate.Where.before(lambda _: _.__name__ == 'action2'))
        delegate += (lambda task, product, ctx: print("current product: {}".format(product)))
        delegate.add(lambda task, product, ctx: print("current product: {}".format(product)))
        fake_task = lambda : None
        delegate(fake_task, "out", None)
        delegate: Delegate
        delegate += (lambda task, product, ctx: print("current product: {}".format(product)))
        delegate: Delegate
        delegate.add(lambda task, product, ctx: print("current product: {}".format(product)))
        delegate: Delegate
        delegate.insert(lambda task, product, ctx: print(product), where=Delegate.Where.after(lambda action: action.__name__ == 'myfunc'))