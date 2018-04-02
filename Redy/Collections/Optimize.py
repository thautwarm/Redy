# from abc import ABC, abstractmethod
# from collections import defaultdict
# from typing import *
# import functools
#
# # from typing.py
# _type_cache = dict()
#
#
# def _tp_cache(func):
#     def inner(*args):
#         ret_type = func(*args)
#         r = _type_cache.get(ret_type, None)
#         if not r:
#             _type_cache.__setitem__(ret_type, ret_type)
#             return ret_type
#         return r
#
#     return inner
#
#
# class Traits(type):
#     """
#     function traits
#     """
#     traits: Dict[object, Dict[object, Tuple[object]]] = defaultdict(dict)
#
#     @_tp_cache
#     def __getitem__(self, item):
#         params = self.__dict__.get('params')
#         if params is None:
#             raise TypeError('No generic support.')
#
#         if not isinstance(item, tuple):
#             item: Tuple[type] = (item,)
#
#         if not params:
#             # generic initialize
#             params = item
#         else:
#             item = iter(item)
#             params = tuple(next(item) if isinstance(each, TypeVar) else each for each in params)
#         namespace = {k: v for k, v in self.__dict__.items() if k != 'params'}
#         return type(
#             f'{self.__name__}[{", ".join(each.__name__ for each in item)}]',
#             tuple(self.mro()),
#             {**namespace,
#              'params': params}
#         )
#
#     def between(self, *item):
#         return self.__getitem__(item)
#
#     def __instancecheck__(self, instance) -> bool:
#         fn_traits = Traits.traits.get(self)
#         print(fn_traits)
#         print(Traits.traits)
#         if not fn_traits:
#             return False
#
#         return instance in fn_traits
#
#
# class Foldable(metaclass=Traits):
#     params = ()
#
#     def __new__(cls, func):
#         Traits.traits[cls][func] = cls.params
#         return func
#
#
# x = Foldable.between(set)
# y = Foldable[set]
#
# print(x is y)
# print(_type_cache)
#
#
# @x
# def f(x):
#     pass
#
#
# print(isinstance(f, y))
