from .common import *


class _InternalCell:
    def __init__(self, value):
        self.cell_contents = value


class ConstDecl(ASTService):
    names_to_supervise: typing.Dict[str, typing.Callable[[ast.Name], None]] = Require("supervise.names", dict)
    const_symbols: typing.Dict[str, str] = Require("const.symbols", dict)
    current_ctx: CompilingTimeContext = RequestContext()

    def __getitem__(self, item):
        return item

    def get_dispatch(self, elem: ast.AST) -> typing.Optional[typing.Callable[[ast.AST], ast.AST]]:
        if isinstance(elem, ast.Name) and elem.id in self.const_symbols:
            return self.replace_symbol
        elif isinstance(elem, ast.AnnAssign) and isinstance(elem.annotation, ast.Name) and isinstance(elem.target,
                                                                                                      ast.Name):
            if check_service(self.current_ctx.get(elem.annotation.id), self):
                # noinspection PyTypeChecker
                return self.register_const_symbols

    def register_const_symbols(self, elem: ast.AST):
        def invalid_use_of_constant_symbol(node: ast.Name):
            raise ValueError(
                    "Reassign values to constant `{}` at \n{}.".format(node.id, get_location(node, self.feature)))

        assign: ast.AnnAssign = elem
        code = self.feature.func.__code__
        symbol_id = assign.target.id
        handler = self.names_to_supervise.get(symbol_id)

        if handler:
            handler(assign.target)

        self.names_to_supervise[symbol_id] = invalid_use_of_constant_symbol

        idx = len(self.const_symbols)
        var_name = 'const.{}'.format(idx)
        self.const_symbols[var_name] = symbol_id
        self.const_symbols[symbol_id] = var_name
        closure = self.current_ctx.closure

        # implement cell for possible consistency problems.
        closure[symbol_id] = closure[var_name] = _InternalCell(
                compiling_time_eval(assign.value, self.current_ctx, code.co_filename))

        return []

    def replace_symbol(self, elem: ast.AST):
        elem: ast.Name = elem

        if isinstance(elem.ctx, ast.Store):
            raise ValueError("Reassign constant symbol `{}` at \n"
                             "{}".format(elem.id, get_location(elem, self.feature)))

        name = self.const_symbols[elem.id]
        elem.id = name
        return elem


_const_place = opcode.opmap['LOAD_NAME'], opcode.opmap['LOAD_GLOBAL']


class ConstLink(BCService):
    current_ctx: CompilingTimeContext = RequestContext()
    const_symbols: typing.Dict[str, str] = Require("const.symbols", dict)

    def setup_env(self, feature: 'Feature'):
        pass

    def get_dispatch(self, bc: 'bytecode.Instr'):
        if hasattr(bc, 'opcode') and bc.opcode in _const_place and bc.arg in self.const_symbols:
            return self.link_const

    def link_const(self, bc: 'bytecode.Instr'):
        yield bytecode.Instr('LOAD_CONST', self.current_ctx[self.const_symbols[bc.arg]], lineno=bc.lineno)
