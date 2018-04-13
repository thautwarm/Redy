from Redy.Types import *


from Redy.Collections.LinkedList import LinkedList
x = LinkedList(1)
x.next = [1, 2, 3]
print(x.next)
def inf_stream():
   i = 0
   while True:
       yield i
       i += 1
x.next = inf_stream()
for i in zip(range(10), x):
   print(i)
x.next = None
x.__repr__()
try:
   x.next = 1
except TypeError:
   print('expected error')
except Exception as e:
   raise e
z = LinkedList(2)
z.next = x
print(z)

from Redy.Collections.LinkedList import zero_list, ZeroList
print(zero_list)
if not zero_list:
    print('test as false')
try:
    zero_list.next
except StopIteration:
    print('expected exception')
except Exception as e:
    raise e
try:
    zero_list.any = 1
except ValueError:
    print('expected error')
except Exception as e:
    raise e
zero_list_ = ZeroList()
assert zero_list is zero_list_

from Redy.Collections.LinkedList import zero_list, ZeroList
print(zero_list)
if not zero_list:
    print('test as false')
try:
    zero_list.next
except StopIteration:
    print('expected exception')
except Exception as e:
    raise e
try:
    zero_list.any = 1
except ValueError:
    print('expected error')
except Exception as e:
    raise e
zero_list_ = ZeroList()
assert zero_list is zero_list_