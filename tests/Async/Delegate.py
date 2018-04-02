from Redy.Types import *


from Redy.Async.Delegate import Delegate
action = lambda task, product, globals: print(task.__name__)
delegate = Delegate(action)
def action2(task, product, globals):
    print(product)
delegate.insert(action2, Delegate.Where.after(lambda _: False))
delegate.insert(action, Delegate.Where.before(lambda _: _.__name__ == 'action2'))
delegate += (lambda task, product, ctx: print("current product: {}".format(product)))
delegate.add(lambda task, product, ctx: print("current product: {}".format(product)))