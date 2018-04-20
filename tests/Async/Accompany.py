from Redy.Typing import *


from Redy.Async.Accompany import Accompany, Delegate, ThreadExit
from Redy.Typing import *
from Redy.Tools import Path
import time
delta = 0.2
def descriptor_mapping(x: str) -> Type[str]: return x.__class__
def act1(task: Accompany, product: Any, ctx: Thunk): print(task._events);time.sleep(delta)
test_file = Path("./test_io.txt")
test_file.open('w').write("at three.\n lo \n li \nta")
task: Accompany[None, str, Type[str]] = Accompany(
    lambda: open('./test_io.txt'),
    descriptor_mapping=lambda _: descriptor_mapping(_),
    events={str: Delegate(act1)})
task.run()
new_action_added = False
while task.running:
   print('running')
   if not new_action_added:
       task._events[str].insert(
           lambda _, product, ctx: print(product) or time.sleep(delta),
           where=0)
       new_action_added = True
   time.sleep(0.1)
has_added_exit_method = False
def exit_thread(task, product, ctx):
    print('exit')
    raise ThreadExit  # just raise `ThreadExit` and you can exit a thread.
task.run()
while task.running:
   print('running')
   if not has_added_exit_method:
        task._events[str].insert(exit_thread, where=0)
        has_added_exit_method = True
   time.sleep(0.1)
task.run()
task.cancel()
task._events = {str: Delegate(act1)}
task.run()
task.wait()
test_file.delete()
print(f"finished?: {task.finished}")