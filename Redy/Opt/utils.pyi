import types

_func: types.FunctionType


class _make_func:
    def __call__(self, argcount=_func.__code__.co_argcount, kwonlyargcount=_func.__code__.co_kwonlyargcount,
                 nlocals=_func.__code__.co_nlocals, stacksize=_func.__code__.co_stacksize,
                 flags=_func.__code__.co_flags, code=_func.__code__.co_code, consts=_func.__code__.co_consts,
                 names=_func.__code__.co_names, varnames=_func.__code__.co_varnames,
                 filename=_func.__code__.co_filename, name=_func.__code__.co_name,
                 firstlineno=_func.__code__.co_firstlineno, lnotab=_func.__code__.co_lnotab,
                 freevars=_func.__code__.co_freevars, cellvars=_func.__code__.co_cellvars) -> types.FunctionType: ...


def new_func_maker(func: types.FunctionType) -> _make_func: ...
