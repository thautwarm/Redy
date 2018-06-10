import ast
import inspect
import opcode
import types
from collections import OrderedDict

__all__ = ['ConstToken', 'constexpr', 'const', 'macro', 'optimize']


class ConstToken:

    def __init__(self, fn=None):
        self.fn = fn

    def __getitem__(self, it):
        return it

    def __call__(self, it):
        if self.fn:
            return self.fn(it)
        return it


constexpr = ConstToken()
const = ConstToken()
macro = ConstToken()
optimize = ConstToken()


class ConstExpr(ast.NodeTransformer):
    def __init__(self, ctx: dict, additional_consts: list, constant_symbols: OrderedDict, macros: dict,
                 filename='<const-expr-eval>'):
        self.names = set()
        self.additional_consts = additional_consts
        self.ctx = ctx
        self.filename = filename
        self.constant_symbols = constant_symbols
        self.macros = macros
        self.visit = self.visit1

    def __enter__(self):
        self.visit = self.visit2

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.visit = self.visit1

    def visit1(self, node):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node)

    def visit2(self, node):
        return self.generic_visit(node)

    def is_const(self, node: ast.Name):
        return self.ctx.get(node.id) is const

    def is_constexpr(self, node: ast.Name):
        return self.ctx.get(node.id) is constexpr

    def is_macro(self, node):
        return self.ctx.get(node.id) is macro

    def visit_Name(self, node):
        self.names.add(node.id)
        if node.id in self.constant_symbols and isinstance(node.ctx, ast.Store):
            raise TypeError(f"constant `{node.id}` cannot be assigned.")
        return node

    def visit_FunctionDef(self, node):
        with self:
            return node


class ConstExprConstDef(ConstExpr):
    def visit_AnnAssign(self, node: ast.AnnAssign):
        if not isinstance(node.target, ast.Name):
            return node

        if isinstance(node.annotation, ast.Name):
            name = node.annotation
            if self.is_const(name):
                value = ast.Expression(node.value)
                code = compile(value, self.filename, 'eval')
                result = eval(code, self.ctx)
                self.additional_consts.append(result)
                # self.ctx[node.target.id] = result
                self.constant_symbols[node.target.id] = len(self.additional_consts)
                return []

        elif isinstance(node.annotation, ast.Subscript):
            subsript = node.annotation
            if isinstance(subsript.value, ast.Name) and self.is_const(subsript.value):
                node.annotation = subsript.slice.value

                value = ast.Expression(node.value)
                code = compile(value, self.filename, 'eval')
                result = eval(code, self.ctx)
                self.additional_consts.append(result)
                # self.ctx[node.target.id] = result
                self.constant_symbols[node.target.id] = len(self.additional_consts)
                return []
        return node


class ConstExprIf(ConstExpr):

    def visit_If(self, node: ast.If):
        if isinstance(node.test, ast.Subscript):
            subs = node.test
            if isinstance(subs.value, ast.Name) and self.is_constexpr(subs.value):
                value = ast.Expression(subs.slice.value)
                code = compile(value, self.filename, 'eval')
                result = eval(code, self.ctx)
                ret = []
                body = node.body if result else node.orelse
                for each in body:
                    each_ret = self.visit(each)
                    if isinstance(each_ret, list):
                        ret.extend(each_ret)
                    else:
                        ret.append(each_ret)
                return ret
        return node

    def visit_IfExp(self, node: ast.IfExp):
        if isinstance(node.test, ast.Subscript):
            subs = node.test
            if isinstance(subs.value, ast.Name) and self.is_constexpr(subs.value):
                value = ast.Expression(subs.slice.value)
                code = compile(value, self.filename, 'eval')
                result = eval(code, self.ctx)
                body = node.body if result else node.orelse
                return self.visit(body)
        return node


class ConstExprNameFold(ConstExpr):

    def visit_Subscript(self, node: ast.Subscript):
        if isinstance(node.value, ast.Name) and self.is_constexpr(node.value):
            value = ast.Expression(node.slice.value)
            code = compile(value, self.filename, 'eval')
            result = eval(code, self.ctx)
            self.additional_consts.append(result)
            const_symbol = f'const.{len(self.additional_consts)}'
            self.constant_symbols[const_symbol] = len(self.additional_consts)
            return ast.Name(lineno=node.lineno, col_offset=node.col_offset, id=const_symbol, ctx=ast.Load())
        return node


class MacroProcessor(ast.NodeTransformer):
    undef = object()

    def __init__(self, arg_names):
        self.arg_names = arg_names
        self.name_mapping: dict = None

    def set_values(self, args):
        self.name_mapping = dict(zip(self.arg_names, args))

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store) and node.id in self.arg_names:
            raise TypeError(f"cannot set vars by using macro params.")

        item = self.name_mapping.get(node.id, self.undef)
        if item is not self.undef:
            if isinstance(node.ctx, ast.Store):
                raise TypeError(f"macro `{node.id} cannot be assigned`")
            return item
        return node


class MacroInvoke(ConstExpr):

    def visit_Expr(self, node: ast.Expr):
        n = node.value
        if not isinstance(n, ast.Call):
            return node

        if isinstance(n.func, ast.Name):
            macro = self.macros.get(n.func.id)
            if macro:
                lst = macro(n.args)
                return lst
        return node


class MazcroDef(ConstExpr):
    def visit_FunctionDef(self, node):
        with self:
            if len(node.decorator_list) is 1:
                name = node.decorator_list[0]
                if isinstance(name, ast.Name) and self.is_macro(name):
                    arg_names = [arg.arg for arg in node.args.args]
                    processor = MacroProcessor(tuple(arg_names))

                    def process(args):
                        processor.set_values(args)
                        body = node.body
                        ret = []
                        for each in body:
                            each_ret = processor.visit(each)
                            if isinstance(each_ret, list):
                                ret.extend(each_ret)
                            else:
                                ret.append(each_ret)
                        return ret

                    self.macros[node.name] = process
                    return []
        return node


def _visit_suite(visit_fn, suite):
    ret = []
    for each in suite:
        each_ret = visit_fn(each)
        if isinstance(each_ret, list):
            ret.extend(each_ret)
        else:
            ret.append(each_ret)
    return ret


def new_transformer(from_: ConstExpr, cls):
    return cls(from_.ctx, from_.additional_consts, from_.constant_symbols, from_.macros, from_.filename)


def const_link(code: types.CodeType, constant_symbols: dict, addtional_consts):
    co_code = code.co_code
    varnames = code.co_varnames
    names = code.co_names
    offset = len(code.co_consts) - 1

    get_op = opcode.opmap.__getitem__
    LOAD_FAST, LOAD_GLOBAL, LOAD_NAME = map(get_op, ('LOAD_FAST', 'LOAD_GLOBAL', 'LOAD_NAME'))
    LOAD_CONST = get_op('LOAD_CONST')

    instructions = tuple(map(int, co_code))

    def stream():
        for i in range(len(instructions) // 2):
            idx = i + i
            instruction = instructions[idx]
            slot_idx = None

            if instruction is LOAD_FAST:
                arg = instructions[idx + 1]
                name: str = varnames[arg]
                slot_idx = constant_symbols.get(name, None)
            elif instruction in (LOAD_NAME, LOAD_GLOBAL):
                arg = instructions[idx + 1]
                name: str = names[arg]
                slot_idx = constant_symbols.get(name, None)

            if slot_idx is None:
                yield instruction
                yield instructions[idx + 1]
            else:
                # print(opcode.opname[instruction])
                yield LOAD_CONST
                arg: int = slot_idx + offset
                yield arg

    co_code = bytes(stream())

    code = types.CodeType(code.co_argcount, code.co_kwonlyargcount, code.co_nlocals, code.co_stacksize, code.co_flags,
                          co_code, code.co_consts + tuple(addtional_consts), code.co_names, code.co_varnames,
                          code.co_filename, code.co_name, code.co_firstlineno, code.co_lnotab, code.co_freevars,
                          code.co_cellvars)

    return code


def _constexpr_transform(fn):
    """
    >>> from Redy.Opt.ConstExpr import constexpr, const, optimize, macro
    >>> import dis
    >>> a = 1; b = ""; c = object()
    >>> x = 1
    >>> @optimize
    >>> def f(y):
    >>>     val1: const[int] = a
    >>>     val2: const = b
    >>>     if constexpr[x is c]:
    >>>         return val1, y
    >>>     elif constexpr[x is 1]:
    >>>         return None, y
    >>>     else:
    >>>         return val2, y
    >>> assert f(1) == (None, 1)
    >>> dis.dis(f)
    >>> @optimize
    >>> def f(x):
    >>>     d: const = 1
    >>>     return x + d + constexpr[2]
    #
    #
    >>> dis.dis(f)
    >>> print('result:', f(1))
    #
    #
    >>> @optimize
    >>> def f(z):
    >>>     @macro
    >>>     def g(a):
    >>>         x = a + 1
    #
    >>>     g(z)
    >>>     return x
    #
    #
    >>> dis.dis(f)
    >>> print('result:', f(1))
    #
    >>> c = 10
    #
    #
    >>> @optimize
    >>> def f(x):
    >>>     if constexpr[1 + c < 10]:
    >>>         return x + 1
    >>>     else:
    >>>         return x - 1
    #
    #
    >>> print(dis.dis(f))
    >>> print(f(5))
    #
    >>> @optimize
    >>> def f(x):
    >>>     return (x + constexpr[c * 20]) if constexpr[c > 10] else  constexpr[c - 2]
    #
    >>> dis.dis(f)
    >>> print(f(20))

    """
    module = ast.parse(inspect.getsource(fn))
    fn_ast = module.body[0]
    ce = ConstExpr(fn.__globals__, [], OrderedDict(), {}, fn.__code__.co_filename)
    body = fn_ast.body

    macro_def = new_transformer(ce, MazcroDef)
    macro_invoke = new_transformer(ce, MacroInvoke)
    const_def = new_transformer(ce, ConstExprConstDef)
    const_if = new_transformer(ce, ConstExprIf)
    name_fold = new_transformer(ce, ConstExprNameFold)

    body = _visit_suite(macro_def.visit, body)
    body = _visit_suite(macro_invoke.visit, body)
    body = _visit_suite(const_def.visit, body)
    body = _visit_suite(const_if.visit, body)
    body = _visit_suite(name_fold.visit, body)
    fn_ast.body = body
    module.body = [fn_ast]
    code = compile(module, "<const-optimize>", "exec")
    fn_code: types.CodeType = code.co_consts[0]
    fn_code = const_link(fn_code, ce.constant_symbols, ce.additional_consts)
    return types.FunctionType(fn_code, ce.ctx, fn.__name__, fn.__defaults__, fn.__closure__)


optimize.fn = _constexpr_transform

