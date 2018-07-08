import typing, abc
import ast
from astpretty import pprint as show_ast

try:
    from .Feature import Feature
except:
    pass

T = typing.TypeVar('T')


class Service(typing.Generic[T]):
    @abc.abstractmethod
    def get_dispatch(self, feature: 'Feature', elem: T) -> typing.Optional[typing.Callable[['Feature', T], T]]:
        raise NotImplemented

    def __call__(self, feature: 'Feature', elem: T):
        return self.get_dispatch(feature, elem)

    @abc.abstractmethod
    def initialize_env(self, feature: 'Feature') -> None:
        raise NotImplemented


class CompilingTimeContext(typing.Mapping):
    def __len__(self) -> int:
        raise NotImplemented

    def __iter__(self):
        raise NotImplemented

    def __init__(self, globals: dict, locals: dict):
        """
        :param locals: a dictionary made from outside closure.
        """
        self.locals = locals
        self.globals = globals

    def __contains__(self, item):
        return item in self.locals or item in self.globals

    def __getitem__(self, item):
        res = self.locals.get(item)
        if res is None:
            return self.globals[item]
        return res.cell_contents

    def __setitem__(self, key, value):
        cell = self.locals.get(key)

        if cell:
            cell.cell_contents = value
        else:
            self.globals[key] = value


def build_local_from_closure(closure: tuple, free_vars, globals):
    return CompilingTimeContext(globals, {v: c for v, c in zip(free_vars, closure if closure else ())})


def compiling_time_eval(expr: ast.AST, ctx: CompilingTimeContext, filename=""):
    return eval(compile(ast.Expression(expr), filename, "eval"), ctx.globals, ctx)


def compiling_time_exec(stmt: ast.stmt, ctx: CompilingTimeContext, filename=""):
    return eval(compile(ast.Module(lineno=stmt.lineno, col_offset=stmt.col_offset, body=[stmt]), filename, "exec"),
                ctx.globals, ctx)


def initialize_state(state: dict, name: str, constructor):
    if name not in state:
        this = state[name] = constructor()
    else:
        this = state[name]
    return this
