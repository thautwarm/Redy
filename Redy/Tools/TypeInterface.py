"""
Type objects of Python
"""
from Redy.Magic.Classic import singleton
import types


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
