from ..Types import *

__all__ = ['LinkedList']


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

    """
    __slots__ = ['_next', 'value']

    def __init__(self, value: T, next: 'Optional[Iterable[T]]' = None):
        self.value = value

        if isinstance(next, Iterator):
            self._next = next
        elif isinstance(next, Iterable):
            self._next = iter(next)
        elif next is None:
            self._next = None
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

    @property
    def next(self) -> 'Optional[LinkedList[T]]':
        if not self._next:
            return None

        if not isinstance(self._next, LinkedList):
            self._next = LinkedList(next(self._next), self._next)
        return self._next

    @next.setter
    def next(self, seq):
        if seq is None:
            self._next = None
            return

        if not isinstance(seq, Iterable):
            raise TypeError
        elif isinstance(seq, LinkedList):
            self._next = seq
        else:
            self._next = iter(seq)

    def __str__(self):
        return f'[{", ".join(map(str, self))}]'

    def __repr__(self):
        return self.__str__()
