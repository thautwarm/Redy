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