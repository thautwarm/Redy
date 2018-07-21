from ..Typing import *
from ..Magic.Classic import singleton

__all__ = ['LinkedList', 'ZeroList', 'zero_list']


class LinkedList(Iterable[T]):
    """
    Implementation of lazy LinkedList.
    >>> from Redy.Collections.LinkedList import LinkedList
    >>> x = LinkedList(1)

    >>> x.next = [1, 2, 3]

    >>> print(x.next)


    >>> def inf_stream():
    >>>    i = 0
    >>>    while True:
    >>>        yield i
    >>>        i += 1


    >>> x.next = inf_stream()

    >>> for i in zip(range(10), x):
    >>>    print(i)
    >>> x.next = None
    >>> x.__repr__()
    >>> try:
    >>>    x.next = 1
    >>> except TypeError:
    >>>    print('expected error')
    >>> except Exception as e:
    >>>    raise e
    >>> z = LinkedList(2)
    >>> z.next = x
    >>> print(z)
    >>> a1 = LinkedList(1)
    >>> a2 = a1.cons(2)
    >>> a3 = a2.cons(3)
    >>> list(a3) == [3, 2, 1]
    >>> assert a3.count() == 3

    """
    _stop = object()
    __slots__ = ['_next', 'value']

    def __init__(self, value: T, next: 'Optional[Iterable[T]]' = None):
        self.value = value

        if isinstance(next, Iterable):
            self._next = iter(next)
        elif next is None:
            self._next = zero_list
        else:
            raise TypeError

    def __iter__(self) -> Iterator[T]:
        yield self.value
        if not self._next:
            return

        ptr = self.next
        while ptr:
            yield ptr.value
            ptr = ptr.next

    def count(self):
        n = 0
        it = iter(self)
        try:
            while next(it):
                n += 1
        except StopIteration:
            return n

    def cons(self, value: T):
        return LinkedList(value, self)

    @property
    def next(self) -> 'Optional[LinkedList[T]]':
        _next = self._next
        if not _next:
            return zero_list

        if not isinstance(_next, LinkedList):
            _stop = self._stop
            elem = next(_next, _stop)
            self._next = LinkedList(elem, _next) if elem is not _stop else zero_list

        return self._next

    @next.setter
    def next(self, seq):
        if seq is None:
            self._next = None
            return

        elif isinstance(seq, LinkedList):
            self._next = seq
        else:
            self._next = iter(seq)

    def __str__(self):
        return f'[{", ".join(map(str, self))}]'

    def __repr__(self):
        return self.__str__()


@singleton
class ZeroList(LinkedList[T]):
    """
    >>> from Redy.Collections.LinkedList import zero_list, ZeroList
    >>> print(zero_list)
    >>> if not zero_list:
    >>>     print('test as false')
    >>> try:
    >>>     zero_list.next
    >>> except StopIteration:
    >>>     print('expected exception')
    >>> except Exception as e:
    >>>     raise e
    >>> try:
    >>>     zero_list.any = 1
    >>> except AttributeError:
    >>>     print('expected error')
    >>> except Exception as e:
    >>>     raise e
    >>> zero_list_ = ZeroList()
    >>> assert zero_list is zero_list_
    >>> assert isinstance(zero_list, ZeroList)

    """

    __slots__ = []

    # noinspection PyMissingConstructor
    def __init__(self):
        pass

    def __call__(self):
        return self

    def __iter__(self):
        yield from ()

    def __instancecheck__(self, instance):
        return self is instance

    @property
    def next(self):
        raise StopIteration

    def __bool__(self):
        return False

    def __setattr__(self, key, value):
        raise AttributeError('Empty list is readonly.')


zero_list = ZeroList()
