from .common import *


class ConstDecl(ASTService):

    def __hash__(self):
        return hash('const.decl')

    def __eq__(self, other):
        return isinstance(other, ConstDecl)

    const_symbols: typing.Dict[str, str]
    current_ctx: CompilingTimeContext
    const_link_table: typing.Dict[str, object]

    # noinspection PyUnresolvedReferences
    def initialize_env(self, feature: 'Feature') -> None:
        state = feature.state

        cons = lambda: build_local_from_closure(feature.func.__closure__, feature.func.__code__.co_freevars,
                                                feature.func.__globals__)
        self.current_ctx = initialize_state(state, 'context.current', cons)

        self.const_symbols = initialize_state(state, 'const.symbols', dict)

        self.const_link_table = initialize_state(state, 'const.link_table', dict)

    def get_dispatch(self, feature: 'Feature', elem: T) -> typing.Optional[typing.Callable[['Feature', T], T]]:
        if isinstance(elem, ast.AnnAssign) and isinstance(elem.annotation, ast.Name) and isinstance(elem.target,
                                                                                                    ast.Name):
            if self.current_ctx.get(elem.annotation.id) is const_token:
                # noinspection PyTypeChecker
                return self.register_const_symbols
        elif isinstance(elem, ast.Name) and elem.id in self.const_symbols:
            return self.replace_symbol

    def register_const_symbols(self, feature: Feature, elem: ast.AST):
        feature.func.__code__: types.CodeType
        code = feature.func.__code__

        idx = len(self.const_link_table)
        var_name = 'const.{}'.format(idx)
        self.const_symbols[elem.target.id] = var_name
        self.const_link_table[var_name] = compiling_time_eval(elem.value, self.current_ctx, code.co_filename)

        return []

    def replace_symbol(self, feature: Feature, elem):
        feature.func: types.FunctionType

        if isinstance(elem.ctx, ast.Store):
            raise ValueError("Assign constant symbol `{}` at "
                             "lineno {}, column {} in file {}".format(elem.id, elem.lineno, elem.col_offset,
                                                                      feature.func.__code__.co_filename))

        name = self.const_symbols[elem.id]
        elem.id = name
        return elem


_const_place = opcode.opmap['LOAD_NAME'], opcode.opmap['LOAD_GLOBAL']


class ConstLink(BCService):

    def __hash__(self):
        return hash('const.link')

    def __eq__(self, other):
        return isinstance(other, ConstLink)

    const_link_table: dict

    def initialize_env(self, feature: 'Feature'):
        state = feature.state
        self.const_link_table = initialize_state(state, 'const.link_table', dict)

    def get_dispatch(self, feature: 'Feature', bc: 'bytecode.Instr'):
        if bc.opcode in _const_place and bc.arg in self.const_link_table:
            return self.link_const

    def link_const(self, feature: 'Feature', bc: 'bytecode.Instr'):
        return bytecode.Instr('LOAD_CONST', self.const_link_table[bc.arg], lineno=bc.lineno)


const_token = const = (ConstDecl(), ConstLink())
