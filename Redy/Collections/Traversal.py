import builtins
from ..Typing import *
import functools
from collections import defaultdict

__all__ = ['map_by', 'reduce_by', 'fold_by', 'sum_from', 'each_do', 'filter_by', 'flatten_to', 'flatten_if', 'chunk_by',
           'chunk', 'group', 'group_by']

ActualIterable = Iterable


def map_by(fn: Callable[[T1], T2]) -> Callable[[ActualIterable[T1]], Iterable[T2]]:
    """
    when pycharm supports type hinting for any implementation of currying,
    map_with and map_on would be deprecated.
    >>> from Redy.Collections import Traversal, Flow
    >>> def double(x: int) -> int: return x * 2
    >>> lst: Iterable[int] = [1, 2, 3]
    >>> x = Flow(lst)[Traversal.map_by(double)][Traversal.sum_from(0)].unbox
    >>> assert x is 12
    now you can get the hinting that `x` is of type `int`
    """
    return lambda collection: builtins.map(fn, collection)


def reduce_by(fn: Callable[[T1, T1], T1]) -> Callable[[ActualIterable[T1]], T1]:
    """
    >>> from Redy.Collections import Traversal, Flow
    >>> def mul(a: int, b: int): return a * b
    >>> lst: Iterable[int] = [1, 2, 3]
    >>> x = Flow(lst)[Traversal.reduce_by(mul)].unbox
    >>> assert x is 6
    """
    return lambda collection: functools.reduce(fn, collection)


def fold_by(fn: Callable[[T1, T2], T1], start: T1) -> Callable[[ActualIterable[T2]], T1]:
    """
    >>> from Redy.Collections import Traversal, Flow
    >>> def mul(a: int, b: int): return a * b
    >>> lst: Iterable[int] = [1, 2, 3]
    >>> x = Flow(lst)[Traversal.fold_by(mul, 1)].unbox
    >>> assert x is 6
    """
    return lambda collection: functools.reduce(fn, collection, start)


def filter_by(fn: Callable[[T], bool]) -> Callable[[ActualIterable[T]], Iterable[T]]:
    """
    >>> from Redy.Collections import Traversal, Flow
    >>> def even(a: int) -> bool: return a % 2 == 0
    >>> lst: Iterable[int] = [1, 2, 3]
    >>> x = Flow(lst)[Traversal.filter_by(even)].unbox
    >>> assert list(x) == [2]
    """
    return lambda collection: builtins.filter(fn, collection)


def sum_from(zero: T1 = None) -> Callable[[ActualIterable[T1]], T1]:
    """
    >>> from Redy.Collections import Traversal, Flow
    >>> lst: Iterable[int] = [1, 2, 3]
    >>> x = Flow(lst)[Traversal.sum_from(0)].unbox
    >>> assert x is 6

    >>> x = Flow(lst)[Traversal.sum_from()].unbox
    >>> assert x is 6
    """

    def _(collection: Iterable[T1]) -> T1:
        if zero is None:
            collection = iter(collection)
            _zero = next(collection)
            return builtins.sum(collection, _zero)

        return builtins.sum(collection, zero)

    return _


def each_do(action: Callable[[T], None]):
    """
    >>> from Redy.Collections import Traversal, Flow
    >>> lst: Iterable[int] = [1, 2, 3]
    >>> def action(x: int) -> None: print(x)
    >>> x = Flow(lst)[Traversal.each_do(action)]
    >>> assert x.unbox is None
    """

    def inner(collection: ActualIterable[T]):
        for each in collection:
            action(each)

    return inner


def flatten_to(atom: Union[Tuple[Type[T]], Type[T]]):
    """
    >>> from Redy.Collections import Traversal, Flow
    >>> lst: Iterable[int] = [[1, 2, 3]]
    >>> x = Flow(lst)[Traversal.flatten_to(int)]
    >>> assert isinstance(x.unbox, Generator) and list(x.unbox) == [1, 2, 3]
    """

    def inner(nested: ActualIterable[Union[T, ActualIterable[T]]]) -> ActualIterable[T]:
        for each in nested:
            if isinstance(each, atom):
                yield each
            else:
                yield from inner(each)

    return inner


def flatten_if(cond: Callable[[Union[T, ActualIterable[T]]], bool]):
    """
    >>> from Redy.Collections import Traversal, Flow
    >>> lst: Iterable[int] = [[1, 2, 3]]
    >>> x = Flow(lst)[Traversal.flatten_if(lambda _: isinstance(_, list))]
    >>> assert isinstance(x.unbox, Generator) and list(x.unbox) == [1, 2, 3]
    """

    def inner(nested: ActualIterable[Union[T, ActualIterable[T]]]) -> ActualIterable[T]:
        for each in nested:
            if cond(each):
                yield from inner(each)
            else:
                yield each

    return inner


def chunk_by(fn: Callable[[T], object]):
    """
    >>> from Redy.Collections import Traversal, Flow
    >>> lst: Iterable[int] = [0, 1, 2, 3, 4, 5, 6]
    >>> x = Flow(lst)[Traversal.chunk_by(lambda x: x // 3)]
    >>> assert list(x.unbox) == [[0, 1, 2], [3, 4, 5], [6]]
    >>> x = Flow([])[Traversal.chunk_by(lambda x: x)]
    >>> assert list(x.unbox) == []
    """

    def inner(seq: ActualIterable[T]) -> ActualIterable[ActualIterable[T]]:
        seq = iter(seq)
        try:
            head = next(seq)
        except StopIteration:
            return iter(seq)

        current_status = fn(head)
        group = [head]
        for each in seq:
            status = fn(each)
            if status != current_status:
                yield group
                group = [each]
            else:
                group.append(each)
            current_status = status
        if group:
            yield group

    return inner


def chunk(seq: ActualIterable[T]) -> ActualIterable[ActualIterable[T]]:
    """
    >>> from Redy.Collections import Traversal, Flow
    >>> x = [1, 1, 2]
    >>> assert Flow(x)[Traversal.chunk][list].unbox == [[1, 1], [2]]
    >>> assert Flow([])[Traversal.chunk][list].unbox == []
    """
    seq = iter(seq)
    try:
        head = next(seq)
    except StopIteration:
        return iter(seq)

    current_status = head
    group = [head]
    for each in seq:
        status = each
        if status != current_status:
            yield group
            group = [each]
        else:
            group.append(each)
        current_status = status
    if group:
        yield group


def group_by(fn: Callable[[T], TR]):
    """
    >>> from Redy.Collections import Flow, Traversal
    >>> x = [1, '1', 1.0]
    >>> Flow(x)[Traversal.group_by(type)]
    """

    def inner(seq: ActualIterable[T]) -> Dict[TR, List[T]]:
        ret = defaultdict(list)
        for each in seq:
            ret[fn(each)].append(each)

        return ret

    return inner


def group(seq: ActualIterable[T]) -> Dict[TR, List[T]]:
    """
    >>> from Redy.Collections import Flow, Traversal
    >>> x = [1, 1, 2]
    >>> Flow(x)[Traversal.group].unbox
    """
    ret = defaultdict(list)
    for each in seq:
        ret[each].append(each)
    return ret
