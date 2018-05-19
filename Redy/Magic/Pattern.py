from typing import List
import inspect

__all__ = ["IPattern", "Pattern"]


class IPattern:
    func: 'function'
    templates: dict

    def match(self, case):
        def add(func):
            self.templates[case] = func
            if func.__doc__:
                self.__doc__ += func.__doc__

            return func if hasattr(func, '__name__') and func.__name__ != self.__name__ else self

        return add


_empty = inspect._empty


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
        # noinspection PyUnresolvedReferences
        arg_info = inspect.getfullargspec(func)

        if arg_info.defaults or arg_info.kwonlyargs or arg_info.varkw or arg_info.varargs:

            def new_func(*args, **kwargs):
                case = func(*args, **kwargs)
                f = new_func.templates.get(case)
                if not f:
                    f = new_func.templates.get(any)
                    if not f:
                        raise TypeError(f'Unknown entry for case {case}.')
                return f(*args, **kwargs)
        else:

            args = ",".join(inspect.getargs(func.__code__).args)
            # noinspection PyUnresolvedReferences
            scope = {'func': func, **func.__globals__}
            exec(f"def new_func({args}):\n"
                 f"    case = func({args})\n"
                 f"    f = new_func.templates.get(case)\n"
                 f"    if not f:\n"
                 f"        f = new_func.templates.get(any)\n"
                 f"        if not f:\n"
                 f"            raise TypeError(f'Unknown entry for case {{case}}.')\n"
                 f"    return f({args})\n", scope)
            new_func: IPattern = scope['new_func']

        new_func.templates = {}
        new_func.__name__ = func.__name__
        new_func.case = new_func.match = lambda case: IPattern.match(new_func, case)
        new_func.__doc__ = "Redy pattern matching function. \n{}".format(func.__doc__ if func.__doc__ else '')
        return new_func
