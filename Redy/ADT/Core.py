from ..Tools.TypeInterface import BuiltinMethod
from ..Magic.Classic import singleton
from .traits import *
from inspect import getfullargspec
import functools

__all__ = ['data', 'P', 'PatternList', 'match', 'RDT']


def data(cls_def: type):
    """
    >>> from Redy.ADT.Core import data
    >>> from Redy.Magic.Classic import cast
    >>> from Redy.ADT.traits import *
    >>> @data
    >>> class S(ConsInd):  # ConsInd class makes it available to index from this data as from a tuple.
    >>>    a: '1'
    >>>    b: lambda x: x
    >>>    c: lambda x, y : ...


    >>> assert isinstance(S.a, S)
    >>> assert isinstance(S.b('2'), S)
    >>> assert S.b('2').__str__() == '(2)'

    >>> assert S.c(1, 2)[:] == (S.c, 1, 2)  # here `ConsInd` works!

    # Nat
    >>> @data
    >>> class Nat(Discrete, ConsInd):
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

    def constructor_descriptor(f):
        return functools.lru_cache(maxsize=None)(f) if issubclass(cls_def, Discrete) else f

    __dict__ = {}
    for each in reversed(cls_def.__mro__):
        __dict__.update({k: v for k, v in each.__dict__.items() if v})

    new_cls_def = type(cls_def.__name__, cls_def.__bases__, __dict__)

    new_cls_def.__slots__ = ['__inst_str__', '__structure__']

    if not hasattr(new_cls_def, '__str__') or isinstance(new_cls_def.__str__, BuiltinMethod):
        def __str__(self):
            return f'({self.__inst_str__})'

        new_cls_def.__str__ = __str__

    new_cls_def.__repr__ = new_cls_def.__str__

    def __destruct__(self):
        return self.__structure__

    def __iter__(self):
        yield from self.__structure__

    new_cls_def.__destruct__ = __destruct__
    new_cls_def.__iter__ = __iter__

    def make_type(str_value: object, default: str):
        entity = new_cls_def()
        entity.__inst_str__ = default if str_value is ... else str_value
        entity.__structure__ = None

        return entity

    # if Discrete, it means that for a definite input, the return of data constructor is definitely the same object.

    def make_callable_type(f: Union['function', DTTransDescriptor], default: str):
        @constructor_descriptor
        def call(*adt_cons_args):
            entity = new_cls_def()

            if isinstance(f, DTTransDescriptor):
                __structure__, __inst_str__ = f.func(*adt_cons_args)
                entity.__inst_str__ = (default, *__structure__) if __inst_str__  is ... else __inst_str__
                entity.__structure__ = (call, *__structure__)
                return entity

            str_value = f(*adt_cons_args)
            entity.__inst_str__ = (default, *adt_cons_args) if str_value is ... else str_value
            entity.__structure__ = (call, *adt_cons_args)
            return entity

        return call

    for each, annotation in __annotations__.items():
        if callable(annotation):
            spec = getfullargspec(annotation)
            if spec.defaults or spec.kwonlyargs or spec.varkw:
                raise TypeError('A ADT constructor must be a lambda without default args or keyword args.')
            singleton_inst = make_callable_type(annotation, each)
        else:
            singleton_inst = make_type(annotation, each)

        setattr(new_cls_def, each, singleton_inst)

    return new_cls_def


class DTTransDescriptor:
    __slots__ = ['func']

    def __init__(self, func):
        self.func = func

    def __call__(self, *args):
        raise TypeError


@singleton
class RDT:
    """
    rewrite data type
    >>> from Redy.ADT.Core import RDT
    >>> from Redy.ADT.traits import ConsInd
    >>> @data
    >>> class MyDT(ConsInd):
    >>>     P: RDT[lambda raw_input: ((1, raw_input), str(raw_input))]
    >>> p = MyDT.P("42")
    >>> assert p[1] is 1
    >>> assert p[2] == "42"
    """

    def __getitem__(self, item):
        return DTTransDescriptor(item)


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
    >>> from Redy.ADT.Core import match, data, P
    >>> @data
    >>> class List(ConsInd, Discrete):
    >>>     # ConsInd(index following constructing)
    >>>     #    |-> Ind;
    >>>     # Discrete
    >>>     #    |-> Im(Immutable), Eq
    >>>     Nil : ...
    >>>     Cons: lambda head, tail: ...
    >>> lst = List.Cons(2, List.Cons(1, List.Nil))
    >>> mode_lst = P[List.Cons, P, P[List.Cons, 1]]
    >>> if match(mode_lst,  lst):
    >>>     assert mode_lst == [List.Cons, 2, [List.Cons, 1]]
    """
    # noinspection PyUnresolvedReferences
    try:
        # noinspection PyUnresolvedReferences
        structure = obj.__destruct__()
    except AttributeError:
        return False
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

