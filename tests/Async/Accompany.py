from Redy.Types import *


from Redy.Async.Accompany import Accompany, Delegate, ThreadExit
from Redy.Types import *
import time
delta = 0.2
def descriptor_mapping(x: str) -> Type[str]: return x.__class__
def act1(task: Accompany, product: Any, ctx: Thunk): print(task.events);time.sleep(delta)
task: Accompany[None, str, Type[str]] = Accompany(
    lambda: open('b.txt'),
    descriptor_mapping=lambda _: descriptor_mapping(_),
    events={str: Delegate(act1)})
task.run()
added = False
def exit_thread(task, product, ctx): print('exit'); raise ThreadExit
while task.running:
   print('running')
   if not added:
       task.events[str].insert(
           lambda _, product, ctx: print(product) or time.sleep(delta),
           where=0)
       added = True
   else:
       task.events[str].insert(exit_thread, 0)
task.run()
task.cancel()
task.run()
# task.cancel()
task.wait()
print(f"finished?: {task.finished}")