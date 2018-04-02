import builtins
from ..Types import *
import functools

__all__ = ['map_by', 'reduce_by', 'fold_by', 'sum_from', 'each_do', 'filter_by', 'flatten_to']

ActualIterable = Union[Iterable, Iterable, Sequence, Collection]


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
            return builtins.sum(collection, next(collection))

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


def flatten_to(atom: Type[T]):
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
