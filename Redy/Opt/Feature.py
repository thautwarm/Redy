import ast
import inspect
import types
import collections
import opcode
import abc
import textwrap
import typing
import re

from .basic import Service, show_ast

try:
    from .bytecode_api import BCService, Bytecode
    import bytecode
except:
    pass

_whitespace = re.compile('[ \t]+')


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

        self._services = list(_flatten(services, set()))
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

    def just_apply_ast_transformation(self, ast_: ast.AST):
        self.setup_env()
        for each in self._services:
            if isinstance(each, ASTService):
                self._current_service = each
                ast_ = self.apply_ast_service(ast_)
                each.exit_env()
                if not isinstance(ast_, ast.AST):
                    return ast_

        return ast_

    @property
    def state(self):
        return self._state

    def apply_ast_service(self, elem):
        transform_inner_ast = self.ast_transform
        service = self._current_service
        if service.is_depth_first:
            elem = transform_inner_ast(elem)

            application = service(elem)
            if application:
                return application(elem)
            else:  # use `else` for building clear layer
                return elem
        else:
            application = service(elem)

            if not application:
                return transform_inner_ast(elem)
            else:  # use `else` for building clear layer
                return application(elem)

    def apply_bc_service(self, bc):
        def transform_inner_code(_bc, _self) -> typing.NoReturn:
            if hasattr(_bc, 'opcode') and _bc.opcode in opcode.hasconst and isinstance(_bc.arg, types.CodeType):
                _bc.arg = _self.bc_transform(Bytecode.from_code(_bc.arg)).to_code()

        service = self._current_service
        if service.is_depth_first:
            transform_inner_code(bc, self)

            application = service(bc)
            if not application:
                yield bc
            else:  # use `else` for building clear layer
                yield from application(bc)
        else:
            application = service(bc)
            if not application:
                transform_inner_code(bc, self)

                yield bc
            else:  # use `else` for building clear layer
                yield from application(bc)

    def ast_transform(self, node):
        apply = self.apply_ast_service
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

        apply = self.apply_bc_service

        transformed = tuple(bc_trans_stream(apply, bc))
        bc.clear()
        bc.extend(transformed)
        bc.flags |= bytecode.CompilerFlags.OPTIMIZED
        return bc

    def __call__(self, target_function: types.FunctionType):
        self.func = target_function
        ast_services, bc_services = self.setup_env()

        if ast_services:
            apply = self.apply_ast_service

            # fix col_offset if `func` not in the top level of module.
            src_code: str = inspect.getsource(target_function)
            _space = _whitespace.match(src_code)
            col_offset = 0
            if _space:  # the source code's column offset is not 0.
                col_offset = _space.span()[1]  # get indentation of source code
                # perform dedentation
                src_code = '\n'.join(each[col_offset:] for each in src_code.splitlines())

            node = ast.parse(src_code)
            if col_offset:
                # visit the ast and fix the col_offset.
                self._current_service = _ColOffsetFix(col_offset)  # set current service as col_offset_fix
                node = self.ast_transform(node)

            for self._current_service in ast_services:
                node = apply(node)

                if not isinstance(node, ast.AST):
                    # Some one might prefer to transform ast into other sorts.
                    # e.g: Interpreter, IR/Bytecode Generation
                    return node
            code_object = compile(node, self.func.__code__.co_filename, 'exec')
            # for `compile` with mode 'exec' yields code objects of some statements instead of functions.
            # So, I try to get the corresponding code object of target function in the following way.
            code_object = next(each for each in code_object.co_consts if
                               isinstance(each, types.CodeType) and each.co_name == target_function.__name__)

        else:
            # if no ast service, we needn't do any thing than take the code object of target function.
            code_object = target_function.__code__

        if bc_services:
            try:
                bc = Bytecode.from_code(code_object)

                for self._current_service in bc_services:
                    bc = self.bc_transform(bc)
                # bytecode can only be transformed to bytecode.

                def display_blocks(blocks):
                    for block in blocks:
                        print("Block #%s" % (1 + blocks.get_block_index(block)))
                        for instr in block:
                            if isinstance(instr.arg, bytecode.BasicBlock):
                                arg = "<block #%s>" % (1 + blocks.get_block_index(instr.arg))
                            elif instr.arg is not bytecode.UNSET:
                                arg = repr(instr.arg)
                            else:
                                arg = ''
                            print("    %s %s" % (instr.name, arg))

                        if block.next_block is not None:
                            print("    => <block #%s>" % (1 + blocks.get_block_index(block.next_block)))

                        print()
                display_blocks(bytecode.ControlFlowGraph.from_bytecode(bc))
                code_object = bc.to_code()

            except NameError:
                import warnings
                warnings.warn('You have register some bytecode services but the library `bytecode` is required.\n'
                              'See `https://github.com/vstinner/bytecode` and you can get it by'
                              '`pip install bytecode`.')

        # noinspection PyArgumentList
        # laji pycharm xjb reports argument info.
        f = types.FunctionType(code_object, target_function.__globals__, target_function.__name__,
                               target_function.__defaults__, target_function.__closure__)
        return f


class ASTService(Service):

    @property
    @abc.abstractmethod
    def is_depth_first(self):
        raise NotImplementedError


class _ColOffsetFix(ASTService):

    def setup_env(self, feature: 'Feature') -> None:
        pass

    def __init__(self, col_offset: int):
        self.col_offset = col_offset

    @property
    def is_depth_first(self):
        return True

    def get_dispatch(self, elem: ast.AST):
        return self.fix

    def fix(self, elem: ast.AST):
        if hasattr(elem, 'lineno'):  # oh, lineno is shorter than col_offset!
            elem.col_offset += self.col_offset

        return elem


class _ConstClosure(BCService):

    def setup_env(self, feature: 'Feature') -> None:
        pass

    def __init__(self, mapping: typing.Dict[str, object]):
        self.trans_rule = mapping

    def is_depth_first(self):
        return False

    def get_dispatch(self, elem: bytecode.Instr):
        if hasattr(elem, 'name') and elem.name == 'LOAD_DEREF' and elem.arg.name in self.trans_rule:
            return self.replace

    def replace(self, elem: bytecode.Instr):
        yield bytecode.Instr('LOAD_CONST', self.trans_rule[elem.arg.name])
