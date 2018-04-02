from ..Types import *

__all__ = ['Flow', 'Monadic']


class Flow(Generic[T]):
    __slots__ = ['within']

    def __init__(self, within: T):
        self.within: T = within

    def __getitem__(self, fn: Callable[[T], TR]) -> 'Flow[TR]':
        return Flow(fn(self.within))

    @property
    def unbox(self):
        return self.within


class Monadic(Iterable, Generic[T, TR]):
    """
    >>> from Redy.Collections.Core import *
    >>> def i2f(x: int) -> float: return x * 1.0
    >>> def f2s(x: float) -> str: return str(x)
    >>> def s2f(x: str) -> float: return float(x)
    >>> def f2i(x: float) -> int: return int(x)
    >>> def i2s(x: int) -> str:   return str(x)
    >>> z = Monadic(i2f)
    >>> d = z[
    >>>     f2s
    >>> ][
    >>>     s2f
    >>> ][
    >>>     f2i
    >>> ][
    >>>     i2s
    >>> ]
    >>> _ = d.call(1)
    >>> print(_, _.__class__)
    """
    __slots__ = ['_fns']

    def __iter__(self):
        # is there any way to destruct function sequence with type info?
        yield from self._fns

    def __init__(self, fn: Union[Callable[[T], TR], Tuple[Callable[[T], TR], ...]]):
        self._fns: Tuple[Callable] = fn if isinstance(fn, tuple) else (fn,)

    def __call__(self, arg: T) -> TR:
        """
        The type inference of __call__ in pycharm is not powerful enough currently,
        so I use `call` method as an alternative temporarily.
        """
        if not self._fns:
            return None
        fns = iter(self._fns)
        head = next(fns)
        result = head(arg)
        for each in fns:
            result = each(result)
        return result

    def call(self, arg):
        """
        This method is expedient because of pycharm's inference error,
        and it will be replace by __call__ in the future.
        """
        return self.__call__(arg)

    def __getitem__(self, other: Callable[[TR], TE]) -> 'Monadic[T, TE]':
        """
        The type inference of __call__ in pycharm is not powerful enough currently,
        so I use `then` method as an alternative temporarily.
        """
        return Monadic(self._fns + (other,))
