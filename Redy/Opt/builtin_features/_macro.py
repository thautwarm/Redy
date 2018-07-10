from .common import *
import warnings

IsExpr = bool


class Macro(ASTService):
    current_ctx: CompilingTimeContext = RequestContext()
    macro_namespace: typing.Dict[str, typing.Tuple[IsExpr, ast.FunctionDef]]

    def __init__(self, macros=None):
        self.inner_transformer = Feature()
        self.macro_namespace = macros if macros else {}

    def expr(self, func):
        mod: ast.Module = get_ast(func.__code__)
        self._define_expr_macro(mod.body[0])
        return func

    def stmt(self, func):
        mod: ast.Module = get_ast(func.__code__)
        self._define_stmt_macro(mod.body[0])
        return func

    def get_dispatch(self, elem):
        if isinstance(elem, ast.FunctionDef):
            if len(elem.decorator_list) is 1:
                decorator = elem.decorator_list[0]
                if isinstance(decorator, ast.Attribute) and isinstance(decorator.value, ast.Name):
                    name = decorator.value
                    if check_service(self.current_ctx.get(name.id), self):
                        if decorator.attr == 'stmt':
                            return self._define_stmt_macro
                        elif decorator.attr == 'expr':
                            return self._define_expr_macro
                        else:
                            raise AttributeError("Unknown macro definition method `{}`"
                                                 " at {}.".format(name.id, get_location(elem, self.feature)))

        else:
            if isinstance(elem, ast.Expr):
                maybe_call, is_stmt = elem.value, True
            else:
                maybe_call, is_stmt = elem, False

            if isinstance(maybe_call, ast.Call):
                if isinstance(maybe_call.func, ast.Name) and maybe_call.func.id in self.macro_namespace:
                    return self._expand_expr if not is_stmt else self._expand_stmt

    def _define_macro(self, elem: ast.AST, is_expr: bool):
        fn: ast.FunctionDef = elem
        name = fn.name
        self.macro_namespace[name] = (is_expr, fn)
        return []

    def _define_stmt_macro(self, elem):
        return self._define_macro(elem, is_expr=False)

    def _define_expr_macro(self, elem):
        return self._define_macro(elem, is_expr=True)

    def _expand_expr(self, elem: ast.AST):
        call: ast.Call = elem
        terms = call.args
        is_expr, macro = self.macro_namespace[call.func.id]
        if not is_expr:
            raise ValueError("Cannot use a stmt macro `{}` as expr!\n at {}.".format(call.func.id,
                                                                                     get_location(call, self.feature)))
        args = macro.args.args

        if len(args) != len(terms):
            raise ValueError("Macro argument number mismatch \n at {}.".format(get_location(call, self.feature)))

        expand_map: typing.Dict[str, ast.AST] = dict(zip((arg.arg for arg in args), terms))

        transformer = self.inner_transformer
        macro_expanding_application = _MacroExpand(expand_map, self)

        with transformer.use_service(macro_expanding_application):
            transformer.setup_env()
            if is_expr:
                ret: ast.Return = transformer.just_apply_ast_transformation(macro.body[-1], setup_env=False)
                return ret.value
            res = [transformer.just_apply_ast_transformation(each, setup_env=False) for each in macro.body]
            return res

    def _expand_stmt(self, elem: ast.AST):
        expr: ast.Expr = elem
        call: ast.Call = expr.value
        terms = call.args
        is_expr, macro = self.macro_namespace[call.func.id]
        args = macro.args.args
        if len(args) != len(terms):
            raise ValueError("Macro argument number mismatch \n at {}.".format(get_location(call, self.feature)))

        expand_map: typing.Dict[str, ast.AST] = dict(zip((arg.arg for arg in args), terms))

        transformer = self.inner_transformer
        macro_expanding_application = _MacroExpand(expand_map, self)

        with transformer.use_service(macro_expanding_application):
            transformer.setup_env()
            if is_expr:
                ret: ast.Return = transformer.just_apply_ast_transformation(macro.body[-1], setup_env=False)
                expr.value = ret
                return expr
            res = [transformer.just_apply_ast_transformation(each, setup_env=False) for each in macro.body]
            return res


class _MacroExpand(ASTService):
    current_ctx: CompilingTimeContext
    macro_namespace: typing.Dict[str, typing.Tuple[IsExpr, ast.FunctionDef]]

    def __init__(self, expand_map: typing.Dict[str, ast.AST], proxy: Macro):
        self.expand_map = expand_map
        self.proxy = proxy

    def setup_env(self, feature: 'Feature'):
        proxy = self.proxy
        self.current_ctx = proxy.current_ctx
        self.macro_namespace = proxy.macro_namespace

    def get_dispatch(self, elem):
        if isinstance(elem, ast.Name) and elem.id in self.expand_map:
            return self._expand

    def _expand(self, elem: ast.AST):
        name: ast.Name = elem
        return self.expand_map[name.id]
