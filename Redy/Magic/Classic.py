import functools
import types
from inspect import getfullargspec
from collections import namedtuple
from ..Tools.Hash import hash_from_stream

__all__ = ['template', 'singleton_init_by', 'singleton', 'const_return', 'cast', 'execute', 'record', 'discrete_cache',
           'cache']

_undef = object()
_slot_wrapper = type(object.__str__)


def raise_exc(e: Exception):
    raise e


def singleton_init_by(init_fn=None):
    """
    >>> from Redy.Magic.Classic import singleton
    >>> @singleton
    >>> class S:
    >>>     pass
    >>> assert isinstance(S, S)
    """

    if not init_fn:
        def wrap_init(origin_init):
            return origin_init
    else:
        def wrap_init(origin_init):
            def __init__(self):
                origin_init(self)
                init_fn(self)

            return __init__

    def inner(cls_def: type):
        if not hasattr(cls_def, '__instancecheck__') or isinstance(cls_def.__instancecheck__,
                                                                   (types.BuiltinMethodType, _slot_wrapper)):
            def __instancecheck__(self, instance):
                return instance is self

            cls_def.__instancecheck__ = __instancecheck__

        _origin_init = cls_def.__init__
        cls_def.__init__ = wrap_init(_origin_init)

        return cls_def()

    return inner


singleton = singleton_init_by(None)


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
    >>> def f(x = x) -> int:
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


def record(cls_def):
    """
    Namedtuple which could inherit from other types.
    >>> from Redy.Magic.Classic import record
    >>> class Interface: pass
    >>> @record
    >>> class S(Interface):
    >>>     name: str
    >>>     addr: str
    >>>     sex : int

    >>> s = S("sam", "I/O", 1)
    """
    annotations = getattr(cls_def, '__annotations__', {})
    typ: type = namedtuple(cls_def.__name__, list(annotations.keys()))
    return cls_def.__class__(cls_def.__name__, (typ, *cls_def.__bases__), dict(cls_def.__dict__))


def _make_discrete_key_stream(args, kwargs: dict):
    yield from map(id, args)
    if kwargs:
        yield from map(id, sorted(kwargs.items()))


def _make_dense_key_stream(args, kwargs: dict):
    yield from map(hash, args)
    if kwargs:
        yield from map(hash, kwargs.items())


def discrete_cache(func):
    caching = {}

    def inner(*args, **kwargs):
        key = hash_from_stream(len(args) + len(kwargs), _make_discrete_key_stream(args, kwargs))
        res = caching.get(key, _undef)

        if res is _undef:
            res = func(*args, **kwargs)
            caching[key] = res

        return res

    functools.update_wrapper(inner, func)
    return inner


def cache(func):
    caching = {}

    def inner(*args, **kwargs):
        key = hash_from_stream(len(args) + len(kwargs), _make_dense_key_stream(args, kwargs))
        res = caching.get(key, _undef)

        if res is _undef:
            res = func(*args, **kwargs)
            caching[key] = res

        return res

    functools.update_wrapper(inner, func)
    return inner


def template(spec_fn):
    """
    >>> from Redy.Magic.Classic import template
    >>> import operator
    >>> class Point:
    >>>    def __init__(self, p):
    >>>         assert isinstance(p, tuple) and len(p) is 2
    >>>         self.x, self.y = p

    >>> def some_metrics(p: Point):
    >>>     return p.x + 2 * p.y

    >>> @template
    >>> def comp_on_metrics(self: Point, another: Point, op):
    >>>        if not isinstance(another, Point):
    >>>             another = Point(another)
    >>>        return op(*map(some_metrics, (self, another)))

    >>> class Space(Point):
    >>>    @comp_on_metrics(op=operator.lt)
    >>>    def __lt__(self, other):
    >>>        ...

    >>>    @comp_on_metrics(op=operator.eq)
    >>>    def __eq__(self, other):
    >>>        ...

    >>>    @comp_on_metrics(op=operator.gt)
    >>>    def __gt__(self, other):
    >>>        ...

    >>>    @comp_on_metrics(op=operator.le)
    >>>    def __le__(self, other):
    >>>        ...

    >>>    @comp_on_metrics(op=operator.ge)
    >>>    def __ge__(self, other):
    >>>        ...

    >>> p = Space((0, 1))
    >>> p >   (1, 2)
    >>> p <   (3, 4)
    >>> p >=  (5, 6)
    >>> p <=  (7, 8)
    >>> p ==  (9, 10)

    """

    def specify(*spec_args, **spec_kwds):
        def call(_):
            def inner(*args, **kwds):
                return spec_fn(*spec_args, *args, **spec_kwds, **kwds)

            return inner

        return call

    return specify
