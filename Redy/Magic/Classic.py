import functools
import threading
from typing import List
import types
from inspect import getfullargspec

__all__ = ['singleton_init_by', 'singleton', 'const_return']

_undef = object()
_slot_wrapper = type(_undef.__str__)


def raise_exc(e: Exception):
    raise e


def __init__(self):
    pass


def singleton_init_by(init_fn):
    """
    >>> from Redy.Magic.Classic import singleton
    >>> @singleton
    >>> class S:
    >>>     pass
    >>> assert isinstance(S, S)
    """

    def inner(cls_def: type):
        if not hasattr(cls_def, '__instancecheck__') or isinstance(cls_def.__instancecheck__,
                                                                   (types.BuiltinMethodType, _slot_wrapper)):
            def __instancecheck__(self, instance):
                return instance is self

            cls_def.__instancecheck__ = __instancecheck__
        cls_def.__init__ = init_fn

        return cls_def()

    return inner


singleton = singleton_init_by(__init__)


def const_return(func):
    """
    >>> from Redy.Magic.Classic import const_return
    >>> @const_return
    >>> def f(x):
    >>>     return x
    >>> r1 = f(1)
    >>> assert r1 is 1 and r1 is f(2)
    """
    result = _undef

    def ret_call(*args, **kwargs):
        nonlocal result
        if result is _undef:
            result = func(*args, **kwargs)
        return result

    return ret_call


def execute(func: types.FunctionType):
    """
    >>> from Redy.Magic.Classic import execute
    >>> x = 1
    >>> @execute
    >>> def f(x) -> int:
    >>>     return x + 1
    >>> assert f is 2
    """
    spec = getfullargspec(func)
    default = spec.defaults
    arg_cursor = 0

    def get_item(name):
        nonlocal arg_cursor
        ctx = func.__globals__
        value = ctx.get(name, _undef)
        if value is _undef:
            try:
                value = default[arg_cursor]
                arg_cursor += 1
            except (TypeError, IndexError):
                raise ValueError(f"Current context has no variable `{name}`")
        return value

    return func(*(get_item(arg_name) for arg_name in spec.args))
