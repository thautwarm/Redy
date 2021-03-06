import types
import inspect
import re


def new_func_maker(func: types.FunctionType):
    def call(argcount=func.__code__.co_argcount,
             kwonlyargcount=func.__code__.co_kwonlyargcount,
             nlocals=func.__code__.co_nlocals,
             stacksize=func.__code__.co_stacksize,
             flags=func.__code__.co_flags,
             code=func.__code__.co_code,
             consts=func.__code__.co_consts,
             names=func.__code__.co_names,
             varnames=func.__code__.co_varnames,
             filename=func.__code__.co_filename,
             name=func.__code__.co_name,
             firstlineno=func.__code__.co_firstlineno,
             lnotab=func.__code__.co_lnotab,
             freevars=func.__code__.co_freevars,
             cellvars=func.__code__.co_cellvars):
        code = types.CodeType(argcount,
                              kwonlyargcount,
                              nlocals,
                              stacksize,
                              flags,
                              code,
                              consts,
                              names,
                              varnames,
                              filename,
                              name,
                              firstlineno,
                              lnotab,
                              freevars,
                              cellvars)
        # noinspection PyArgumentList
        new_func = types.FunctionType(code, func.__globals__, name, func.__defaults__, func.__closure__)
        return new_func

    return call



_path_capture = re.compile("\<module[\s\S]*from '(?P<it>[\s\S]*)'\>")
def get_cls_path(cls):
    try:
        module_str = str(inspect.getmodule(cls))
        m = _path_capture.match(module_str)
        if m:
            g = m.groups()
            if not g:
                return module_str
            return g[0]
        return module_str
    except:
        return "<unknown>"
