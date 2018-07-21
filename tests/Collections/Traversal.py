from Redy.Typing import *

import unittest
import pytest
class Test_Redy_Collections_Traversal(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def test_1802752396328(self):
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
        x = Flow(lst)[Traversal.sum_from()].unbox
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

        from Redy.Collections import Traversal, Flow
        lst: Iterable[int] = [[1, 2, 3]]
        x = Flow(lst)[Traversal.flatten_if(lambda _: isinstance(_, list))]
        assert isinstance(x.unbox, Generator) and list(x.unbox) == [1, 2, 3]

        from Redy.Collections import Traversal, Flow
        lst: Iterable[int] = [0, 1, 2, 3, 4, 5, 6]
        x = Flow(lst)[Traversal.chunk_by(lambda x: x // 3)]
        assert list(x.unbox) == [[0, 1, 2], [3, 4, 5], [6]]
        x = Flow([])[Traversal.chunk_by(lambda x: x)]
        assert list(x.unbox) == []

        from Redy.Collections import Traversal, Flow
        x = [1, 1, 2]
        assert Flow(x)[Traversal.chunk][list].unbox == [[1, 1], [2]]
        assert Flow([])[Traversal.chunk][list].unbox == []

        from Redy.Collections import Flow, Traversal
        x = [1, 1, 2]
        Flow(x)[Traversal.group].unbox

        from Redy.Collections import Flow, Traversal
        x = [1, '1', 1.0]
        Flow(x)[Traversal.group_by(type)]