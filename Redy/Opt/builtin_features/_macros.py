from .common import *
import toolz

_MacroControlTy = typing.Callable[[ast.AST], bool]

_RewriterTy = typing.Callable[[ast.AST], ast.AST]


class Macro(ASTService):
    current_ctx: CompilingTimeContext
    activated_macros: list
    macro_services: dict

    def __hash__(self):
        return hash('macro')

    def __eq__(self, other):
        return isinstance(self, Macro)

    def initialize_env(self, feature: 'Feature'):
        state = feature.state

        def constructor():
            return build_local_from_closure(feature.func.__closure__, feature.func.__code__.co_freevars,
                                            feature.func.__globals__)

        self.macro_services = initialize_state(state, 'macro.services', dict)
        self.activated_macros = initialize_state(state, 'macro.activated', list)
        self.current_ctx = initialize_state(state, 'context.current', constructor)

    def get_dispatch(self, feature: 'Feature', elem: T):
        if isinstance(elem, ast.With) and len(elem.items) is 1:
            item = elem.items[0].context_expr
            if (isinstance(item, ast.Attribute) and isinstance(item.value,
                                                               ast.Name) and item.attr == 'setting' and self.current_ctx.get(
                    item.value.id) is macro):
                # macro settings
                return self.setting_macros

            elif isinstance(item, ast.Subscript) and isinstance(item.value, ast.Name) and self.current_ctx.get(
                    item.value.id) is macro:
                # macro using
                return self.apply_macros

    def setting_macros(self, feature: 'Feature', elem: ast.AST):
        """
        with macro.setting:
            S = define(a + b, len(a) * len(b))
        """
        if feature.state['macro.define.switch']:
            raise ValueError("Nested macro definition.")

        feature.state['macro.define.switch'] = True
        for each in elem.body:
            feature.apply_ast_service(each)
        feature.state['macro.define.switch'] = False

    def apply_macros(self, feature: 'Feature', elem: ast.AST):
        item: ast.Subscript = elem.items[0].context_expr
        subscr = item.slice.value
        if isinstance(item, ast.Tuple):
            elts = item.elts
            if not all(map(lambda e: isinstance(e, ast.Name), elts)):
                return ValueError("Must be Name ASTs.")

            getter = self.macro_services.__getitem__
            self.activated_macros.extend([getter(elt.id) for elt in elts])
        else:
            name = subscr.id
            self.activated_macros.append(self.macro_services[name])

        result = [feature.apply_ast_service(each) for each in elem.body]
        self.activated_macros.clear()
        return result


class MacroDefinition(ASTService):
    current_ctx: CompilingTimeContext
    macro_services: dict

    def initialize_env(self, feature: 'Feature'):
        state = feature.state

        def constructor():
            return build_local_from_closure(feature.func.__closure__, feature.func.__code__.co_freevars,
                                            feature.func.__globals__)

        self.current_ctx = initialize_state(state, 'context.current', constructor)
        self.macro_services = initialize_state(state, 'macro.services', dict)
        initialize_state(state, 'macro.define.switch', lambda: False)

    def get_dispatch(self, feature: 'Feature', elem: T):
        if feature.state['macro.define.switch']:
            if isinstance(elem, ast.FunctionDef):
                return self.define_macro_function

            elif isinstance(elem, (ast.AnnAssign, ast.Assign)):
                return self.define_pattern

    def define_pattern(self, feature: 'Feature', elem: ast.AST):
        if hasattr(elem, 'targets') and len(elem.targets) is 1:
            target = elem.targets[0]
        else:
            target = elem.target

        if isinstance(target, ast.Name):
            macro_name = target.id
            call = elem.value

            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and self.current_ctx.get(
                    call.func.id) is define:
                if len(call.args) is not 2:
                    raise ValueError("Macro pattern definition should take 2 arguments!")
                pattern, transformation = call.args
                micro_service = Feature(ReplaceName())
                if isinstance(pattern, ast.BinOp):
                    if isinstance(pattern.left, ast.Name) or isinstance(pattern.right, ast.Name):
                        macro_ty = pattern.op.__class__
                        left_name = pattern.left.id
                        right_name = pattern.right.id

                        def matcher(occur: ast.BinOp):
                            if isinstance(occur, ast.BinOp) and isinstance(occur.op, macro_ty):
                                micro_service.state['macro.name-map'] = {left_name: occur.left, right_name: occur.right}
                                micro_service.initialize_env()
                                return micro_service.ast_transform(transformation)

                        self.macro_services[macro_name] = matcher
                        return []

                elif isinstance(pattern, ast.Call) and isinstance(pattern.func, ast.Name):
                    macro_fn_name = pattern.func.id
                    args_to_capture = pattern.args
                    if not all(map(lambda _: isinstance(_, ast.Name), args_to_capture)):
                        raise ValueError("Macro function arguments should be Name ASTs.")

                    args_to_capture = [arg.id for arg in pattern.args]

                    def matcher(occur: ast.Call):
                        show_ast(occur)
                        if isinstance(occur, ast.Call) and isinstance(occur.func,
                                                                      ast.Name) and occur.func.id == macro_fn_name:
                            occur_args = occur.args
                            if len(occur_args) != len(args_to_capture):
                                return None
                            micro_service.state['macro.name-map'] = dict(zip(args_to_capture, occur_args))
                            micro_service.initialize_env()
                            return micro_service.ast_transform(transformation)

                    self.macro_services[macro_name] = matcher
                    return []

        compiling_time_exec(elem, self.current_ctx, feature.func.__code__.co_filename)
        return []

    def define_macro_function(self, feature: 'Feature', elem: ast.AST):
        macro_fn_name = elem.name
        args = elem.args
        if args.vararg or args.kwonlyargs or args.kw_defaults or args.kwargs or args.defaults:
            raise NotImplemented

        args_to_capture = [e.id for e in args.args]
        micro_service = Feature(ReplaceName())
        transformation = elem.body

        def matcher(occur):
            if isinstance(occur, ast.Call) and isinstance(occur.func, ast.Name) and occur.func.id == macro_fn_name:
                occur_args = occur.args
                if len(occur_args) != len(args_to_capture):
                    return None
                micro_service.state['macro.name-map'] = dict(zip(args_to_capture, occur_args))
                micro_service.initialize_env()
                return micro_service.ast_transform(transformation)

        self.macro_services[macro_fn_name] = matcher
        return []


class ReplaceName(ASTService):
    name_map: typing.Dict[str, ast.AST]

    def initialize_env(self, feature: 'Feature'):
        self.name_map = initialize_state(feature.state, 'macro.name-map', dict)

    def get_dispatch(self, feature: 'Feature', elem: ast.AST):
        if isinstance(elem, ast.Name) and isinstance(elem.ctx, ast.Load) and elem.id in self.name_map:
            return self.replace

    def replace(self, feature: 'Feature', elem: ast.AST):
        return self.name_map[elem.id]


class PatternRewrite(ASTService):
    activated_macros: list

    def initialize_env(self, feature: 'Feature'):
        self.activated_macros = initialize_state(feature.state, 'macro.activated', list)

    def get_dispatch(self, feature: 'Feature', elem: T):
        done = False
        for each in self.activated_macros:
            mid = each(elem)
            if mid is not None:
                if not done:
                    done = True
                elem = mid

        if done:
            return lambda _1, _2: elem


define = MacroDefinition()
macro = (Macro(), define, PatternRewrite())
