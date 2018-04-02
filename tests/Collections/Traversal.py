from Redy.Types import *


from Redy.Collections import Traversal, Flow
def double(x: int) -> int: return x * 2
lst: Iterable[int] = [1, 2, 3]
x = Flow(lst)[Traversal.map_by(double)][Traversal.sum_from(0)].unbox
assert x is 12

from Redy.Collections import Traversal, Flow
def mul(a: int, b: int): return a * b
lst: Iterable[int] = [1, 2, 3]
x = Flow(lst)[Traversal.reduce_by(mul)].unbox
assert x is 6

from Redy.Collections import Traversal, Flow
def mul(a: int, b: int): return a * b
lst: Iterable[int] = [1, 2, 3]
x = Flow(lst)[Traversal.fold_by(mul, 1)].unbox
assert x is 6

from Redy.Collections import Traversal, Flow
lst: Iterable[int] = [1, 2, 3]
x = Flow(lst)[Traversal.sum_from(0)].unbox
assert x is 6

from Redy.Collections import Traversal, Flow
lst: Iterable[int] = [1, 2, 3]
def action(x: int) -> None: print(x)
x = Flow(lst)[Traversal.each_do(action)]
assert x.unbox is None

from Redy.Collections import Traversal, Flow
def even(a: int) -> bool: return a % 2 == 0
lst: Iterable[int] = [1, 2, 3]
x = Flow(lst)[Traversal.filter_by(even)].unbox
assert list(x) == [2]

from Redy.Collections import Traversal, Flow
lst: Iterable[int] = [[1, 2, 3]]
x = Flow(lst)[Traversal.flatten_to(int)]
assert isinstance(x.unbox, Generator) and list(x.unbox) == [1, 2, 3]