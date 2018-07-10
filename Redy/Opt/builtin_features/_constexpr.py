from .common import *


class _InternalCell:
    def __init__(self, value):
        self.cell_contents = value


class ConstEval(ASTService):

    current_ctx: CompilingTimeContext = RequestContext()
    const_symbols: typing.Dict[str, str] = Require("const.symbols", dict)

    def setup_env(self, feature: 'Feature'):
        pass

    def get_dispatch(self, elem: ast.AST):
        if isinstance(elem, ast.Subscript) and isinstance(elem.value, ast.Name):
            if check_service(self.current_ctx.get(elem.value.id), self):
                return self.const_eval

    def const_eval(self, elem: ast.AST):
        subscr: ast.Subscript = elem
        expr = subscr.slice.value
        result = compiling_time_eval(expr, self.current_ctx, self.feature.func.__code__.co_filename)

        var_name = next((k for k, v in self.current_ctx.locals.items() if v == result), None)

        if var_name is None:
            idx = len(self.const_symbols)
            var_name = 'const.{}'.format(idx)
            self.const_symbols[var_name] = var_name
            self.current_ctx.closure[var_name] = _InternalCell(result)

        return ast.Name(lineno=subscr.lineno, col_offset=subscr.col_offset, id=var_name, ctx=ast.Load())
