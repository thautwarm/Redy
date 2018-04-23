import functools
import types
from inspect import getfullargspec

__all__ = ['singleton_init_by', 'singleton', 'const_return', 'cast', 'data', 'execute']

_undef = object()
_slot_wrapper = type(_undef.__str__)


def _compose2(f1, f2):
    n = '\n'

    def call(*args, **kwargs):
        return f1(f2(*args, **kwargs))

    functools.update_wrapper(call, f2)
    call.__doc__ = f"""{(f2.__doc__ if f2.__doc__ else n)}{f1.__doc__ if f1 else ""}"""
    return call


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


def cast(cast_fn):
    """
    >>> from Redy.Magic.Classic import cast
    >>> @cast(list)
    >>> def f(x):
    >>>     for each in x:
    >>>         if each % 2:
    >>>             continue
    >>>         yield each
    """

    def inner(func):
        def call(*args, **kwargs):
            return cast_fn(func(*args, **kwargs))

        functools.update_wrapper(call, func)
        return call

    return inner


def data(cls_def: type):
    """
    >>> from Redy.Magic.Classic import data
    >>> @data
    >>> class S:
    >>>    a: '1'
    >>>    b: lambda x: x
    >>>    c: '2'


    >>> assert isinstance(S.a, S)
    >>> assert isinstance(S.b('2'), S)
    >>> assert S.b('2').__str__() == '2'
    """
    __annotations__ = cls_def.__annotations__

    @cast(singleton)
    def make_type(typename, str_value: str):
        return type(typename, (cls_def,), dict(_slots__=[], __str__=lambda self: str_value))

    def make_callable_type(typename, f: 'function'):
        return _compose2(lambda str_value: make_type(typename, str_value), f)

    for each, annotation in __annotations__.items():
        if isinstance(annotation, str):
            singleton_inst = make_type(each, annotation)
        elif callable(annotation):
            singleton_inst = make_callable_type(each, annotation)
        else:
            raise TypeError(f'str or T -> str expected, but get {annotation.__class__.__name__}')
        setattr(cls_def,
                each,
                singleton_inst)

    return cls_def
