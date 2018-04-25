import functools
import types
from inspect import getfullargspec
from collections import namedtuple
from ..Collections.Traversal import flatten_if

__all__ = ['singleton_init_by', 'singleton', 'const_return', 'cast', 'data', 'execute', 'record', 'match',
           'PatternList', 'P']

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
    >>> from Redy.Magic.Classic import data, cast
    >>> @data
    >>> class S:
    >>>    a: '1'
    >>>    b: lambda x: x
    >>>    c: lambda x, y : ...


    >>> assert isinstance(S.a, S)
    >>> assert isinstance(S.b('2'), S)
    >>> assert S.b('2').__str__() == 'S[2]'
    >>> assert S.c(1, 2)[:] == (S.c, 1, 2)

    # Nat
    >>> @data
    >>> class Nat:
    >>>     Zero : ...
    >>>     Succ : lambda o: ...
    >>>     def _to_nat(self):
    >>>         if self is Nat.Zero:
    >>>             return 0
    >>>         return 1 + self[1]._to_nat()
    >>>     @cast(str)
    >>>     def __str__(self):
    >>>         return f'Nat[{self._to_nat()}]'
    >>> print (Nat.Succ((Nat.Succ(Nat.Zero))))
    >>> assert Nat.Zero == Nat.Zero
    >>> assert len({Nat.Zero, Nat.Succ(Nat.Zero), Nat.Succ(Nat.Zero)}) is 2
    """
    __annotations__ = cls_def.__annotations__
    cls_def.__slots__ = ['__inst_str__', '__structure__']

    if not hasattr(cls_def, '__str__') or isinstance(cls_def.__str__, (types.BuiltinMethodType, _slot_wrapper)):
        def __str__(self):
            return f'{cls_def.__name__}[{self.__inst_str__}]'

        cls_def.__str__ = __str__

    cls_def.__repr__ = cls_def.__str__

    def __hash__(self):
        return hash((cls_def, self.__structure__))

    def __eq__(self, other):
        # noinspection PyUnresolvedReferences

        return isinstance(other, cls_def) and (
            self.__structure__ == other.__structure__ if self.__structure__ else self is other)

    def __destruct__(self):
        return self.__structure__

    def __getitem__(self, i):
        return self.__structure__[i]

    def __iter__(self):
        yield from self.__structure__

    cls_def.__hash__ = __hash__
    cls_def.__destruct__ = __destruct__
    cls_def.__getitem__ = __getitem__
    cls_def.__eq__ = __eq__
    cls_def.__iter__ = __iter__

    def make_type(str_value: object, default: str):
        entity = cls_def()
        entity.__inst_str__ = default if str_value is ... else str_value
        entity.__structure__ = None

        return entity

    def make_callable_type(f: 'function', default: str):
        def call(*adt_cons_args):
            entity = cls_def()
            str_value = f(*adt_cons_args)

            entity.__inst_str__ = (default, *adt_cons_args) if str_value is ... else str_value
            entity.__structure__ = (call, *adt_cons_args)
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


class PatternList(list):
    pass


@singleton
class P:
    """
    Pattern Prefix
    """

    def __getitem__(self, item):
        return PatternList(item if isinstance(item, tuple) else (item,))


def match(mode_lst: list, obj: 'object that has __destruct__ method'):
    """
    >>> from Redy.Magic.Classic import match, data, P
    >>> @data
    >>> class List:
    >>>     Nil : ...
    >>>     Cons: lambda head, tail: ...
    >>> lst = List.Cons(2, List.Cons(1, List.Nil))
    >>> mode_lst = P[List.Cons, P, P[List.Cons, 1]]
    >>> if match(mode_lst,  lst):
    >>>     assert mode_lst == [List.Cons, 2, [List.Cons, 1]]
    """
    # noinspection PyUnresolvedReferences
    structure = obj.__structure__
    n = len(mode_lst)
    if n > len(structure):
        return False

    for i in range(n):
        mode = mode_lst[i]
        # noinspection PyUnresolvedReferences
        elem = obj[i]
        if isinstance(mode, PatternList):
            if not match(mode, elem):
                return False
        elif mode is P:
            # noinspection PyUnresolvedReferences
            mode_lst[i] = elem
        elif mode is any:
            pass
        elif mode != elem:
            return False

    return True


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
    typ: type = namedtuple(cls_def.__name__, list(cls_def.__annotations__.keys()))
    return type(cls_def.__name__,
                (typ, *cls_def.__bases__),
                dict(cls_def.__dict__))
