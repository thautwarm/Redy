from .common import *
from ._constant_link import ConstLink


class ConstEval(ASTService):
    current_ctx: CompilingTimeContext
    const_link_table: typing.Dict[str, object]

    def initialize_env(self, feature: 'Feature'):
        state = feature.state

        def constructor():
            return build_local_from_closure(feature.func.__closure__, feature.func.__code__.co_freevars,
                                            feature.func.__globals__)

        self.current_ctx = initialize_state(state, 'context.current', constructor)

        self.const_link_table = initialize_state(state, 'const.link_table', dict)

    def get_dispatch(self, feature: 'Feature', elem: ast.AST):
        if isinstance(elem, ast.Subscript) and isinstance(elem.value, ast.Name):
            if self.current_ctx.get(elem.value.id) is constexpr:
                # constexpr = (ConstEval(), ConstLink())
                return self.const_eval
        elif isinstance(elem, (ast.If, ast.IfExp)):
            test = elem.test
            if isinstance(test, ast.Subscript) and isinstance(test.value, ast.Name):
                subscr_name = test.value.id
                if self.current_ctx.get(subscr_name) is constexpr:
                    if not isinstance(test.slice, ast.Index):
                        code: types.CodeType = feature.func.__code__
                        raise ValueError("Constexpr cannot be applied on a slice at\n"
                                         "  File {file}, "
                                         "lineno {lineno}, "
                                         "column {colno}.".format(file=code.co_filename,
                                                                  lineno=code.co_firstlineno + elem.lineno,
                                                                  colno=elem.col_offset))
                return self.const_if

    def const_if(self, feature: 'Feature', elem: ast.AST):
        test = elem.test
        result = compiling_time_eval(test.slice.value, self.current_ctx, feature.func.__code__.co_filename)

        if isinstance(elem, ast.If):
            return [feature.ast_transform(each) for each in (elem.body if result else elem.orelse)]
        else:
            return feature.ast_transform(elem.body if result else elem.orelse)

    def const_eval(self, feature: 'Feature', elem: ast.AST):
        expr = elem.slice.value
        result = compiling_time_eval(expr, self.current_ctx, feature.func.__code__.co_filename)
        idx = len(self.const_link_table)
        var_name = 'const.{}'.format(idx)
        self.const_link_table[var_name] = result
        return ast.Name(lineno=elem.lineno, col_offset=elem.col_offset, id=var_name, ctx=ast.Load())


constexpr = (ConstLink(), ConstEval())
