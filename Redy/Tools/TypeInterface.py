"""
Type objects of Python
"""
from ..Magic.Classic import singleton
import types

__all__ = ['II', 'Module', 'BuiltinMethod']


class _Template:
    pass


class II:
    """
    Interface of Interface.
    """
    this: type

    def __instancecheck__(self, instance):
        return isinstance(instance, self.this)


@singleton
class Module(II):
    """
    >>> from Redy.Tools.TypeInterface import Module
    >>> import math
    >>> assert isinstance(math, Module)
    """
    this = getattr(types, 'ModuleType')


@singleton
class BuiltinMethod(II):
    """
    union of types.BuiltinMethodType and method-wrapper
    >>> from Redy.Tools.TypeInterface import BuiltinMethod
    >>> class S: ...
    >>> assert isinstance(S.__init__, BuiltinMethod)
    """
    this = (types.BuiltinMethodType, type(_Template.__str__))
