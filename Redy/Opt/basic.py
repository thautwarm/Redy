import typing
import abc
import ast
import opcode
import collections
from .utils import *
import inspect
from Redy.Magic.Classic import const_return
import bytecode


try:
    from .Feature import Feature
except:
    pass

T = typing.TypeVar('T')
_Require = collections.namedtuple('Require', ('state_area', 'constructor'))
_undef = object()


class BaseRequire:
    pass


class RequestContext(BaseRequire):
    pass


class Require(_Require, globals()['BaseRequire']):  # to avoid wrong type hinting
    """
    declare a state area required by your service.
    ----------------------------------------------
    class MyASTService(ASTService):
        my_require = Require("const.symbols", dict)  # initialize state area with calling `dict`

        def get_dispatch(self, elem):
          assert self._feature.state['const.symbols'] is self.my_require
          ...

    """
    state_area: str
    constructor: typing.Callable


@const_return
def _load_future():
    from .Feature import Feature, _ConstClosure
    return Feature, _ConstClosure


class MetaService(type):

    def __new__(mcs, name: str, bases: typing.Tuple[type], namespace: dict):
        cls = super(MetaService, mcs).__new__(mcs, name, bases, namespace)
        if not inspect.isabstract(mcs):
            filename = get_cls_path(cls)
            for property_name, require in namespace.items():
                if not isinstance(require, BaseRequire):
                    continue

                if isinstance(require, Require):
                    Feature, _ConstClosure = _load_future()
                    state_area, constructor = require

                    @new_func_maker
                    @Feature(_ConstClosure(dict(state_area=state_area, constructor=constructor)))
                    def dynamic_property_maker(self):
                        state = self._feature.state
                        if state_area not in state:
                            state[state_area] = constructor()
                        return state[state_area]

                elif isinstance(require, RequestContext):
                    @new_func_maker
                    def dynamic_property_maker(self):
                        state = self._feature.state
                        if 'context.current' not in state:
                            feature = self._feature
                            state['context.current'] = build_local_from_closure(feature.func.__closure__,
                                                                                feature.func.__code__.co_freevars,
                                                                                feature.func.__globals__)
                        return state['context.current']
                else:
                    raise TypeError("Unknown Requirement.")

                _property = property(
                        dynamic_property_maker(filename=filename, name='requirement: {}'.format(property_name)))
                setattr(cls, property_name, _property)

        return cls


class Service(metaclass=MetaService):
    _feature: 'Feature'

    @abc.abstractmethod
    def get_dispatch(self, elem) -> typing.Optional[typing.Callable]:
        raise NotImplemented

    @property
    def feature(self):
        return self._feature

    @feature.setter
    def feature(self, _):
        self._feature = _

    def register(self, feature: 'Feature'):
        feature.services.append(self)

    def setup_env(self, feature: 'Feature') -> None:
        pass

    def exit_env(self):
        pass

    def __call__(self, elem):
        return self.get_dispatch(elem)


class CompilingTimeContext(typing.Mapping):
    def __len__(self) -> int:
        raise NotImplemented

    def __iter__(self):
        raise NotImplemented

    def __init__(self, globals: dict, closure: dict):
        """
        :param locals: a dictionary made from outside closure.
        """
        self.locals = {}
        self.closure = closure
        self.globals = globals

    def __contains__(self, item):
        return item in self.closure or item in self.locals or item in self.globals

    def __getitem__(self, item):
        res = self.closure.get(item)
        if res is not None:
            return res.cell_contents
        res = self.locals.get(item, _undef)
        if res is not _undef:
            return res

        return self.globals[item]

    def __setitem__(self, key, value):
        if key in self.closure:
            self.closure[key].cell_contents = value
            return

        self.locals[key] = value


def build_local_from_closure(closure: tuple, free_vars, globals):
    return CompilingTimeContext(globals, {v: c for v, c in zip(free_vars, closure if closure else ())})


def compiling_time_eval(expr: ast.AST, ctx: CompilingTimeContext, filename=""):
    return eval(compile(ast.Expression(expr), filename, "eval"), ctx.globals, ctx)


def initialize_state(state: dict, name: str, constructor):
    if name not in state:
        this = state[name] = constructor()
    else:
        this = state[name]
    return this

