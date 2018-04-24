import functools
import operator
from itertools import zip_longest
from typing import Iterable, Union, Tuple

__all__ = ['Version']
_const_default_version_numbers = (0,)


def _instance(fn):
    def inner(_):
        def func(self: 'Version', other):
            if isinstance(other, Version):
                # noinspection PyProtectedMember
                return fn(self._numbers, other._numbers)
            return fn(str(self), other)

        func.__doc__ = _.__doc__
        func.__name__ = _.__name__
        functools.update_wrapper(func, _)

        return func

    return inner


class Version:
    _numbers: Tuple[int]

    def __init__(self, numbers: Union[str, Iterable] = _const_default_version_numbers):
        if _const_default_version_numbers is numbers:
            self._numbers = _const_default_version_numbers
            return

        elif not isinstance(numbers, str):
            self._numbers = list(numbers)
            return

        self._numbers = list(map(int, numbers.split('.')))
        if any(map(lambda _: _ < 0, self._numbers)):
            raise ValueError('Input an illegal version number!')

    def increment(self, version_number_idx: int, increment: int):
        """
        increment the version number with `n` at index `i`.
        >>> from Redy.Tools.Version import Version
        >>> a = Version('1.0.0.2')
        >>> a.increment(version_number_idx=2, increment=1)
        >>> assert a == ('1.0.1.0')
        >>> print(a[0])
        >>> a[0] = 2
        """
        _numbers = list(self._numbers)
        _numbers[version_number_idx] += increment
        for each in range(version_number_idx + 1, len(_numbers)):
            _numbers[each] = 0
        self._numbers = tuple(_numbers)

    def copy_to(self, another: 'Version'):
        """
        copy its version info to another version object.
        >>> from Redy.Tools.Version import Version
        >>> a = Version()
        >>> b = Version('1.0.0')
        >>> b.copy_to(a)
        >>> assert a == '1.0.0'
        """
        another._numbers = self._numbers

    def copy(self, another: 'Version'):
        """
        copy version info from another version object.
        >>> from Redy.Tools.Version import Version
        >>> a = Version()
        >>> b = Version('1.0.0')
        >>> a.copy(b)
        >>> assert a == '1.0.0'
        """
        self._numbers = another._numbers

    @_instance(operator.eq)
    def __eq__(self, other: Union[str, 'Version']) -> bool:
        """
        >>> from Redy.Tools.Version import Version
        >>> a = Version("1.0")
        >>> assert a == '1.0'
        """

    @_instance(operator.ge)
    def __ge__(self, other: Union[str, 'Version']) -> bool:
        """
        >>> from Redy.Tools.Version import Version
        >>> a = Version('1.0')
        >>> assert a >= '0.8'
        """

    @_instance(operator.le)
    def __le__(self, other: Union[str, 'Version']) -> bool:
        """
        >>> from Redy.Tools.Version import Version
        >>> a = Version('1.0')
        >>> assert a <= '1.1'
        """

    @_instance(operator.gt)
    def __gt__(self, other: Union[str, 'Version']) -> bool:
        """
        >>> from Redy.Tools.Version import Version
        >>> a = Version('1.0')
        >>> assert a > '0.8'
        """

    @_instance(operator.lt)
    def __lt__(self, other: Union[str, 'Version']) -> bool:
        """
        >>> from Redy.Tools.Version import Version
        >>> a = Version('1.0')
        >>> assert a < '1.1'
        """

    def __getitem__(self, item):
        return self._numbers.__getitem__(item)

    def __setitem__(self, key, value):
        _numbers = list(self._numbers)
        _numbers.__setitem__(key, value)
        self._numbers = tuple(_numbers)

    def __add__(self, other: Union[str, Iterable, 'Version']):
        if isinstance(other, Version):
            return Version(_1 + _2 for _1, _2 in zip_longest(other, self._numbers, fillvalue=0))
        other = Version(other)
        return self + other

    def __iadd__(self, other):
        """
        >>> from Redy.Tools.Version import Version
        >>> a = Version('1.0.0')
        >>> a += '0.0.1'
        >>> assert a == '1.0.1'
        """
        self.copy(self + other)
        return self

    def __sub__(self, other):
        """
        >>> from Redy.Tools.Version import Version
        >>> a = Version('1.1.0')
        >>> assert a - '0.1' == '1.0.0'
        >>> assert a - Version('0.1') == '1.0.0'
        """

        if isinstance(other, Version):
            return Version(max(_1 - _2, 0) if _1 else 0 for _1, _2 in zip_longest(self._numbers, other._numbers))
        other = Version(other)
        return self - other

    def __isub__(self, other):
        """
        >>> from Redy.Tools.Version import Version
        >>> a = Version('1.1.1')
        >>> a -= '0.0.1'
        >>> assert a == '1.1.0'
        """
        self.copy(self - other)
        return self

    def __str__(self):
        return '.'.join(map(str, self._numbers))

    def __repr__(self):
        return self.__str__()
