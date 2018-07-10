import ast
import types
import typing
from Redy.Opt.Feature import *
from Redy.Opt.basic import *
import collections
import opcode

try:
    from Redy.Opt.bytecode_api import *
except:
    pass


def check_service(service: typing.Union[Service, typing.Tuple[Service]], target: Service):
    if isinstance(service, Service):
        return target is service
    elif isinstance(service, collections.Iterable):
        return any(sub_service is target for sub_service in service)


def get_location(ast_: ast.AST, feature: 'Feature'):
    code = feature.func.__code__
    filename = code.co_filename
    first_lineno = code.co_firstlineno
    if hasattr(ast_, 'lineno'):
        return '  File "{}" line {} column {}'.format((filename.replace("/", '\\')), ast_.lineno + first_lineno,
                                                      ast_.col_offset)

    return ' File {} line {}'.format((filename.replace("/", '\\')), first_lineno)


class NameSupervisor(ASTService):
    names_to_supervise: typing.Dict[str, typing.Callable[[ast.Name], None]] = Require("supervise.names", dict)

    def is_depth_first(self):
        return False

    def register(self, feature: 'Feature'):
        services = feature.services
        if self in services:
            if not services[-1] is self:
                services.remove(self)
                services.append(self)
        else:
            services.append(self)

    def get_dispatch(self, elem):
        if isinstance(elem, ast.Name):
            handler = self.names_to_supervise.get(elem.id)
            if handler:
                handler(elem)


_undef = object()


class AggregateIndexer:
    _fields: typing.Dict[str, typing.Dict[object, dict]]

    def __init__(self):
        self._fields = {}
        for each in self.__annotations__:
            self._fields[each] = {}

    def index_get(self, default, **kwargs):
        (key, value), *_ = kwargs.items()
        if _:
            raise ValueError

        part = self._fields[key]
        index_map = part.get(value, _undef)
        if index_map is _undef:
            return default
        return index_map

    def index_set(self, *args, **kwargs):
        (key_main, value_main), *others = *args, *kwargs.items()

        index_map = self.index_get(_undef, **{key_main: value_main})
        fields = self._fields
        if index_map is _undef:
            index_map = dict(others)
            index_map[key_main] = value_main
            fields[key_main][value_main] = index_map
            for k, v in others:
                fields[k][v] = index_map
        else:
            for k, v in others:
                index_map[k] = v
                fields[k][v] = index_map

    def __len__(self):
        return max(map(len, self._fields.values()))
