import functools
import types
from inspect import getfullargspec

__all__ = ['singleton_init_by', 'singleton', 'const_return', 'cast', 'data', 'execute']

_undef = object()
_slot_wrapper = type(object.__str__)


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
    >>>    c: lambda x, y : ...


    >>> assert isinstance(S.a, S)
    >>> assert isinstance(S.b('2'), S)
    >>> assert S.b('2').__str__() == '2'
    >>> assert S.c(1, 2)[1] == 2
    """
    __annotations__ = cls_def.__annotations__
    cls_def.__slots__ = ['__inst_str__', '__structure__']

    if not hasattr(cls_def, '__str__') or isinstance(cls_def.__str__, (types.BuiltinMethodType, _slot_wrapper)):
        def __str__(self):
            return self.__inst_str__

        cls_def.__str__ = __str__

    def __destruct__(self):
        return self.__structure__

    def __getitem__(self, i: int):
        return self.__structure__[i]

    cls_def.__destruct__ = __destruct__
    cls_def.__getitem__ = __getitem__

    def make_type(str_value: str, default: str):
        entity = cls_def()
        entity.__inst_str__ = str_value if isinstance(str_value, str) else default
        entity.__structure__ = entity

        return entity

    def make_callable_type(f: 'function', default: str):
        def call(*adt_cons_args):
            entity = cls_def()
            str_value = f(*adt_cons_args)

            entity.__inst_str__ = str_value if isinstance(str_value, str) else default
            entity.__structure__ = adt_cons_args
            return entity

        return call

    for each, annotation in __annotations__.items():

        if callable(annotation):
            spec = getfullargspec(annotation)
            if spec.defaults or spec.kwonlyargs or spec.varkw:
                raise TypeError('A GADT constructor must be a lambda without varargs, default args or keyword args.')
            singleton_inst = make_callable_type(annotation, each)
        else:
            singleton_inst = make_type(annotation, each)

        setattr(cls_def,
                each,
                singleton_inst)

    return cls_def
