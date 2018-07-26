import ast
import inspect
import types
import collections
import opcode
import abc
import textwrap
import typing
import re

from .basic import Service

try:
    from .bytecode_api import BCService, Bytecode
    import bytecode
except:
    pass

_whitespace = re.compile('[ \t]+')


class FeatureWith:
    def __init__(self, feature, service):
        self.feature: Feature = feature
        self.service: Service = service

    def __enter__(self):
        self.feature.add_service(self.service)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.feature.rem_service(self.service)


class Feature:
    func: types.FunctionType

    def __init__(self, *services: Service, state: dict = None):
        def _flatten(it, found):
            for each in it:
                if not isinstance(each, Service):
                    yield from _flatten(each, found)
                else:
                    if each not in found:
                        found.add(each)
                        yield each

        self._state = state if state else {}

        self._services = []
        for each in _flatten(services, set()):
            each.register(self)

        self._current_service: typing.Union[ASTService, BCService] = None

        # function essential factors
        self.func: types.FunctionType = None

    def setup_env(self):
        services = self._services
        ast_services = []
        bc_services = []
        ast_services_add = ast_services.append
        bc_services_add = bc_services.append

        for each in services:
            if isinstance(each, ASTService):
                ast_services_add(each)

            elif isinstance(each, BCService):
                bc_services_add(each)
            else:
                raise TypeError("Requires a ASTService or BCService, got {}.".format(type(each)))
            each.setup_env(self)
            each.feature = self

        return ast_services, bc_services

    def add_service(self, service: Service):
        self._services.append(service)

    def rem_service(self, service):
        self._services.remove(service)

    def just_apply_ast_transformation(self, ast_: ast.AST, setup_env=True):
        if setup_env:
            self.setup_env()
        for each in tuple(self._services):
            if isinstance(each, ASTService):
                self._current_service = each
                ast_ = self.apply_current_ast_service(ast_)
                each.exit_env()
                if not isinstance(ast_, ast.AST):
                    return ast_

        return ast_

    def use_service(self, service: Service):
        return FeatureWith(self, service)

    @property
    def state(self):
        return self._state

    @property
    def services(self):
        return self._services

    def apply_external_ast_service(self, elem, service: 'ASTService'):
        self._current_service = service
        service.setup_env(self)
        service.feature = self
        result = self.apply_current_ast_service(elem)
        service.exit_env()
        return result

    def apply_external_bc_service(self, bc: bytecode.Bytecode, service: 'BCService'):
        self._current_service = service
        service.setup_env(self)
        service.feature = self
        result = self.bc_transform(bc)
        service.exit_env()
        return result

    def apply_current_ast_service(self, elem):
        transform_inner_ast = self.ast_transform
        service = self._current_service

        application = service(elem)

        if not application:
            return transform_inner_ast(elem)
        else:  # use `else` for building clear layer
            return application(elem)

    def apply_current_bc_service(self, bc):
        def transform_inner_code(_bc, _self) -> typing.NoReturn:
            if hasattr(_bc, 'opcode') and _bc.opcode in opcode.hasconst and isinstance(_bc.arg, types.CodeType):
                _bc.arg = _self.bc_transform(Bytecode.from_code(_bc.arg)).to_code()

        service = self._current_service
        application = service(bc)
        if not application:
            transform_inner_code(bc, self)

            yield bc
        else:  # use `else` for building clear layer
            yield from application(bc)

    def ast_transform(self, node):
        apply = self.apply_current_ast_service
        for field, old_value in ast.iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, ast.AST):
                        value = apply(value)
                        if value is None:
                            continue
                        elif not isinstance(value, ast.AST):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, ast.AST):
                new_node = apply(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node

    def bc_transform(self, bc: 'Bytecode'):
        def bc_trans_stream(_app, _bc):
            for each in map(_app, bc):
                yield from each

        apply = self.apply_current_bc_service

        transformed = tuple(bc_trans_stream(apply, bc))
        bc.clear()
        bc.extend(transformed)
        # bc.flags |= bytecode.CompilerFlags.OPTIMIZED
        return bc

    def __call__(self, target_function: types.FunctionType):
        self.func = target_function
        original_code = target_function.__code__
        ast_services, bc_services = self.setup_env()

        original_closure = target_function.__closure__
        if original_closure is None:
            original_closure = ()

        if ast_services:
            apply = self.apply_current_ast_service
            node = get_ast(original_code)

            for self._current_service in ast_services:
                node = apply(node)

                if not isinstance(node, ast.AST):
                    # Some one might prefer to transform ast into other sorts.
                    # e.g: Interpreter, IR/Bytecode Generation
                    return node

            code_object = compile(node, original_code.co_filename, 'exec')
            # for `compile` with mode 'exec' yields code objects of some statements instead of functions.
            # So, I try to get the corresponding code object of target function in the following way.
            code_object = next(each for each in code_object.co_consts if
                               isinstance(each, types.CodeType) and each.co_name == target_function.__name__)

        else:
            # if no ast service, we needn't do any thing than take the code object of target function.
            code_object = original_code

        new_free_vars = code_object.co_freevars

        if bc_services:
            bc = Bytecode.from_code(code_object)
            for self._current_service in bc_services:
                bc = self.bc_transform(bc)
            # bytecode can only be transformed to bytecode.

            code_object = bc.to_code()
            new_free_vars = code_object.co_freevars

        closure = tuple(var for name, var in zip(original_code.co_freevars, original_closure) if name in new_free_vars)

        # noinspection PyArgumentList
        # laji pycharm xjb reports argument info.

        return types.FunctionType(code_object, target_function.__globals__, target_function.__name__,
                                  target_function.__defaults__, closure)


class ASTService(Service):
    pass


class _LocationFix(ASTService):

    def setup_env(self, feature: 'Feature') -> None:
        pass

    def __init__(self, first_lineno: int, col_offset: int):
        self.first_lineno = first_lineno
        self.col_offset = col_offset

    def get_dispatch(self, elem: ast.AST):
        return self.fix

    def fix(self, elem: ast.AST):
        if hasattr(elem, 'lineno'):  # oh, lineno is shorter than col_offset!
            # noinspection PyUnresolvedReferences
            elem.col_offset += self.col_offset
            elem.lineno += self.first_lineno

        return self.feature.ast_transform(elem)


class _ConstClosure(BCService):

    def setup_env(self, feature: 'Feature') -> None:
        pass

    def __init__(self, mapping: typing.Dict[str, object]):
        self.trans_rule = mapping

    def get_dispatch(self, elem: bytecode.Instr):
        if hasattr(elem, 'name') and elem.name == 'LOAD_DEREF' and elem.arg.name in self.trans_rule:
            return self.replace

    def replace(self, elem: bytecode.Instr):
        yield bytecode.Instr('LOAD_CONST', self.trans_rule[elem.arg.name])


_internal_feature = Feature()


def get_ast(code, col_offset=None, first_lineno=None):
    # fix col_offset if `func` not in the top level of module.
    if isinstance(code, ast.AST):
        node = code
    else:
        if isinstance(code, str):
            src_code = code
        else:
            src_code: str = inspect.getsource(code)

        _space = _whitespace.match(src_code)

        col_offset = 0
        if _space:  # the source code's column offset is not 0.
            col_offset = _space.span()[1]  # get indentation of source code
            # perform dedentation
            src_code = '\n'.join(each[col_offset:] for each in src_code.splitlines())

        node = ast.parse(src_code)

        if isinstance(code, types.CodeType):
            first_lineno = code.co_firstlineno

    if first_lineno is None:
        first_lineno = 0
    if col_offset is None:
        col_offset = 0
    # visit the ast and fix the lineno and col_offset.
    return _internal_feature.apply_external_ast_service(node, _LocationFix(first_lineno, col_offset))
