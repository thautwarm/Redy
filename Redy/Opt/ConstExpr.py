import warnings

warnings.warn("The module Redy.Opt.ConstExpr is deprecated. Use Redy.Opt.Feature instead.", DeprecationWarning, stacklevel=2)
import ast
import inspect
import opcode
import re
import textwrap
import types
from typing import Mapping
from collections import OrderedDict

__all__ = ['ConstToken', 'constexpr', 'const', 'macro', 'optimize']


class CompilingTimeMapping(Mapping):
    def __len__(self) -> int:
        raise NotImplemented

    def __iter__(self):
        raise NotImplemented

    undef = object()

    def __init__(self, globals: dict, locals: dict):
        self.set = locals.__setitem__
        self.getg = globals.__getitem__
        self.getl = locals.get

    def __getitem__(self, item):
        v = self.getl(item, self.undef)
        if v is self.undef:
            return self.getg(item)
        return v

    def __setitem__(self, key, value):
        self.set(key, value)


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
    def __init__(self, ctx: CompilingTimeMapping, additional_consts: list, constant_symbols: OrderedDict, macros: dict,
                 nonlocal_names: list, filename='<const-expr-eval>'):
        self.names = set()
        self.additional_consts = additional_consts
        self.ctx = ctx
        self.filename = filename
        self.nonlocal_names = nonlocal_names
        self.constant_symbols = constant_symbols
        self.macros = macros
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
        return node

    def visit_Nonlocal(self, node):
        self.nonlocal_names.extend(node.names)
        return []


class ConstExprConstDef(ConstExpr):

    def visit_AnnAssign(self, node: ast.AnnAssign):
        if isinstance(node.target, ast.Name):
            if isinstance(node.annotation, ast.Name):
                name = node.annotation
                if self.is_const(name):
                    value = ast.Expression(node.value)
                    code = compile(value, self.filename, 'eval')
                    result = eval(code, {}, self.ctx)
                    self.additional_consts.append(result)
                    self.ctx[node.target.id] = result
                    self.constant_symbols[node.target.id] = len(self.additional_consts)
                    return []

            elif isinstance(node.annotation, ast.Subscript):
                subsript = node.annotation
                if isinstance(subsript.value, ast.Name) and self.is_const(subsript.value):
                    node.annotation = subsript.slice.value

                    value = ast.Expression(node.value)
                    code = compile(value, self.filename, 'eval')
                    result = eval(code, {}, self.ctx)
                    self.additional_consts.append(result)
                    # self.ctx[node.target.id] = result
                    self.constant_symbols[node.target.id] = len(self.additional_consts)
                    return []

        return self.generic_visit(node)


class ConstExprIf(ConstExpr):

    def visit_If(self, node: ast.If):
        if isinstance(node.test, ast.Subscript):
            subs = node.test
            if isinstance(subs.value, ast.Name) and self.is_constexpr(self.visit(subs.value)):
                value = ast.Expression(subs.slice.value)
                code = compile(value, self.filename, 'eval')
                result = eval(code, {}, self.ctx)
                ret = []
                body = node.body if result else node.orelse
                for each in body:
                    each_ret = self.visit(each)
                    if isinstance(each_ret, list):
                        ret.extend(each_ret)
                    else:
                        ret.append(each_ret)
                return ret

        return self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp):
        if isinstance(node.test, ast.Subscript):
            subs = node.test
            if isinstance(subs.value, ast.Name) and self.is_constexpr(subs.value):
                value = ast.Expression(subs.slice.value)
                code = compile(value, self.filename, 'eval')
                result = eval(code, {}, self.ctx)
                body = node.body if result else node.orelse
                return self.visit(body)

        return self.generic_visit(node)


class ConstExprNameFold(ConstExpr):
    def visit_Subscript(self, node: ast.Subscript):
        if isinstance(node.value, ast.Name) and self.is_constexpr(node.value):
            value = ast.Expression(node.slice.value)
            code = compile(value, self.filename, 'eval')
            result = eval(code, {}, self.ctx)
            self.additional_consts.append(result)
            const_symbol = f'const.{len(self.additional_consts)}'
            self.constant_symbols[const_symbol] = len(self.additional_consts)
            return ast.Name(lineno=node.lineno, col_offset=node.col_offset, id=const_symbol, ctx=ast.Load())

        return self.generic_visit(node)


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
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name):
            macro = self.macros.get(n.func.id)
            if macro:
                lst = macro(n.args)
                return lst

        return self.generic_visit(node)


class MazcroDef(ConstExpr):
    def visit_FunctionDef(self, node):
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
    return cls(from_.ctx, from_.additional_consts, from_.constant_symbols, from_.macros, from_.nonlocal_names,
               from_.filename)


def const_link(code: types.CodeType, constant_symbols: dict, additional_consts, old_code, nonlocals):
    free_vars = old_code.co_freevars
    co_code = code.co_code
    varnames = code.co_varnames
    names = code.co_names

    get_op = opcode.opmap.__getitem__
    LOAD_FAST, LOAD_GLOBAL, LOAD_NAME, LOAD_CONST, LOAD_DEREF, STORE_FAST, STORE_DEREF = map(get_op, (
        'LOAD_FAST', 'LOAD_GLOBAL', 'LOAD_NAME', 'LOAD_CONST', 'LOAD_DEREF', 'STORE_FAST', 'STORE_DEREF'))

    instructions = tuple(map(int, co_code))
    n_consts = len(additional_consts)

    def stream():
        for i in range(len(instructions) // 2):
            idx = i + i
            instruction = instructions[idx]
            if instruction is LOAD_FAST:
                arg = instructions[idx + 1]
                name: str = varnames[arg]
                slot_idx = constant_symbols.get(name, None)
            elif instruction is LOAD_CONST:
                arg = instructions[idx + 1] + n_consts
                yield instruction
                yield arg
                continue
            elif instruction in (LOAD_NAME, LOAD_GLOBAL):
                arg = instructions[idx + 1]
                name: str = names[arg]
                slot_idx = constant_symbols.get(name, None)
            else:
                if instruction is STORE_FAST:
                    name = varnames[instructions[idx + 1]]
                    if name in nonlocals:
                        yield STORE_DEREF
                        yield free_vars.index(name)
                        continue

                yield instruction
                yield instructions[idx + 1]
                continue

            if slot_idx is None:
                if name in free_vars:
                    yield LOAD_DEREF
                    yield free_vars.index(name)
                else:
                    yield instruction
                    yield instructions[idx + 1]
            else:
                yield LOAD_CONST
                arg: int = slot_idx - 1
                yield arg

    co_code = bytes(stream())
    code = types.CodeType(code.co_argcount, code.co_kwonlyargcount, code.co_nlocals, code.co_stacksize, code.co_flags,
                          co_code, tuple(additional_consts) + code.co_consts, code.co_names, code.co_varnames,
                          old_code.co_filename, code.co_name, old_code.co_firstlineno, old_code.co_lnotab, free_vars,
                          code.co_cellvars)

    return code


_s = re.compile('\s')


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

    >>> def g(lst: list):
    >>>    k = 1

    >>>    @optimize
    >>>    def _():
    >>>        nonlocal k
    >>>        f: const = lst.append
    >>>        for i in range(1000):
    >>>            f(i)
    >>>        k += 1
    >>>        f(k)

    >>>    _()

    >>>    return lst


    >>> # dis.dis(g)
    >>> print(g([]))

    """
    code_string = inspect.getsource(fn)
    while _s.match(code_string):
        code_string = textwrap.dedent(code_string)

    module = ast.parse(code_string)
    fn_ast = module.body[0]
    fn: types.FunctionType
    fn_name = fn.__name__

    closure = fn.__closure__
    closure_dict = {v: c.cell_contents for v, c in zip(fn.__code__.co_freevars, closure if closure else ())}
    ctx = CompilingTimeMapping(fn.__globals__, closure_dict)
    ce = ConstExpr(ctx, [], OrderedDict(), {}, [], fn.__code__.co_filename)
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
    fn_code: types.CodeType = next(
            each for each in code.co_consts if isinstance(each, types.CodeType) and each.co_name == fn_name)

    fn_code = const_link(fn_code, ce.constant_symbols, ce.additional_consts, fn.__code__, ce.nonlocal_names)

    new_fn = types.FunctionType(fn_code, fn.__globals__, fn.__name__, fn.__defaults__, fn.__closure__)

    new_fn.__annotations__ = fn.__annotations__
    new_fn.__doc__ = fn.__doc__
    new_fn.__kwdefaults__ = fn.__kwdefaults__
    new_fn.__module__ = fn.__module__
    return new_fn


optimize.fn = _constexpr_transform
