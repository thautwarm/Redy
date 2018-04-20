from typing import List

__all__ = ["IPattern", "Pattern"]


class IPattern:
    func: 'function'
    templates: dict

    def match(self, case):
        def add(func):
            self.templates[case] = func
            if func.__doc__:
                self.__doc__ += func.__doc__
            return self

        return add


class Pattern:
    """
    multiple dispatch
    >>> from Redy.Magic.Pattern import Pattern

    >>> @Pattern
    >>> def f(x):
    >>>     return type(x)

    >>> @f.match(int)
    >>> def f(x):
    >>>     return 1 + x

    >>> @f.match(any)
    >>> def f(x):
    >>>     return '1' + str(x)

    >>> print(f(1), f('1'))


    checking
    >>> from Redy.Magic.Pattern import Pattern

    >>> equal = lambda x: 2 * x - x ** 2 - 1
    >>> @Pattern
    >>> def f(x):
    >>>     return -10e-3 < equal(x) <= 10e-3

    >>> @f.match(False)
    >>> def f(x):
    >>>     print("Not the solution.")

    >>> @f.match(True)
    >>> def f(x):
    >>>     return x

    >>> print(f(1))

    :exception
    >>> from Redy.Magic.Pattern import Pattern

    >>> @Pattern
    >>> def f(x):
    >>>   return str

    >>> @f.match(int)
    >>> def f(x):
    >>>     return  x

    >>> try:
    >>>     print(f(1))
    >>> except TypeError:
    >>>     pass


    """

    def __new__(cls, func: 'function') -> IPattern:
        def new_func(*args, **kwargs):
            case = func(*args, **kwargs)

            f = new_func.templates.get(case)
            if not f:
                f = new_func.templates.get(any)
                if not f:
                    raise TypeError(f'Unknown entry for case {case}.')

            return f(*args, **kwargs)

        new_func.templates = {}
        new_func.match = lambda *args, **kwargs: IPattern.match(new_func, *args, **kwargs)
        new_func.__doc__ = "Redy pattern matching function. \n{}".format(func.__doc__ if func.__doc__ else '')
        return new_func
