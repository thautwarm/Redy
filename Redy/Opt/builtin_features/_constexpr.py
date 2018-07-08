from .common import *
from ._constant_link import ConstLink


class ConstEval(ASTService):
    current_ctx: CompilingTimeContext
    const_link_table: typing.Dict[str, object]

    def initialize_env(self, feature: 'Feature'):
        state = feature.state

        cons = lambda: build_local_from_closure(feature.func.__closure__, feature.func.__code__.co_freevars,
                                                feature.func.__globals__)
        self.current_ctx = initialize_state(state, 'context.current', cons)

        self.const_link_table = initialize_state(state, 'const.link_table', dict)

    def get_dispatch(self, feature: 'Feature', elem: ast.AST):
        if isinstance(elem, ast.Subscript) and isinstance(elem.value, ast.Name):
            if self.current_ctx.get(elem.value.id) is constexpr:
                # constexpr = (ConstEval(), ConstLink())
                return self.const_eval

    def const_eval(self, feature: 'Feature', elem: ast.AST):
        expr = elem.slice.value
        result = compiling_time_eval(expr, self.current_ctx, feature.func.__code__.co_filename)
        idx = len(self.const_link_table)
        var_name = 'const.{}'.format(idx)
        self.const_link_table[var_name] = result
        return ast.Name(lineno=elem.lineno, col_offset=elem.col_offset, id=var_name, ctx=ast.Load())


constexpr = (ConstLink(), ConstEval())
