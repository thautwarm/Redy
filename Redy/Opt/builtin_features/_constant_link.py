from .common import *


class _InternalCell:
    def __init__(self, value):
        self.cell_contents = value


class ConstDecl(ASTService):

    def __getitem__(self, item):
        return item

    @property
    def is_depth_first(self):
        return False

    const_symbols: typing.Dict[str, str] = Require("const.symbols", dict)
    current_ctx: CompilingTimeContext = RequestContext()

    # noinspection PyUnresolvedReferences
    def setup_env(self, feature: 'Feature') -> None:
        pass

    def get_dispatch(self, elem: ast.AST) -> typing.Optional[typing.Callable[[ast.AST], ast.AST]]:
        if isinstance(elem, ast.Name) and elem.id in self.const_symbols:
            return self.replace_symbol
        elif isinstance(elem, ast.AnnAssign) and isinstance(elem.annotation, ast.Name) and isinstance(elem.target,
                                                                                                      ast.Name):
            if check_service(self.current_ctx.get(elem.annotation.id), self):
                # noinspection PyTypeChecker
                return self.register_const_symbols

    def register_const_symbols(self, elem: ast.AST):
        code = self.feature.func.__code__
        symbol_id = elem.target.id
        if symbol_id in self.const_symbols:
            raise ValueError(
                    "Reassign values to constant `{}` at \n{}.".format(symbol_id, get_location(elem, self.feature)))
        idx = len(self.const_symbols)
        var_name = 'const.{}'.format(idx)
        self.const_symbols[var_name] = symbol_id
        self.const_symbols[symbol_id] = var_name
        closure = self.current_ctx.closure
        # implement cell for possible consistency problems.
        closure[symbol_id] = closure[var_name] = _InternalCell(compiling_time_eval(elem.value, self.current_ctx, code.co_filename))
        return []

    def replace_symbol(self, elem: ast.AST):
        if isinstance(elem.ctx, ast.Store):
            raise ValueError("Reassign constant symbol `{}` at \n"
                             "{}".format(elem.id, get_location(elem, self.feature)))

        name = self.const_symbols[elem.id]
        elem.id = name
        return elem


_const_place = opcode.opmap['LOAD_NAME'], opcode.opmap['LOAD_GLOBAL']


class ConstLink(BCService):

    @property
    def is_depth_first(self):
        return False

    current_ctx: CompilingTimeContext = RequestContext()
    const_symbols: typing.Dict[str, str] = Require("const.symbols", dict)

    def setup_env(self, feature: 'Feature'):
        pass

    def get_dispatch(self, bc: 'bytecode.Instr'):
        if hasattr(bc, 'opcode') and bc.opcode in _const_place and bc.arg in self.const_symbols:
            return self.link_const

    def link_const(self, bc: 'bytecode.Instr'):
        yield bytecode.Instr('LOAD_CONST', self.current_ctx[self.const_symbols[bc.arg]], lineno=bc.lineno)
