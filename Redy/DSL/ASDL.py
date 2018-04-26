from Redy.ADT.Core import data, P, match


@data
class Atom:
    TRUE: ...
    FALSE: ...
    Nil: ...

    # Num :: str -> Atom
    Num: lambda number_str: ...

    # Symbol :: str -> Atom
    Symbol: lambda number: ...

    # Str :: str -> Atom
    Str: lambda literal_str: ...

    # Lambda :: Arg -> Expr -> Atom
    Lambda: lambda arg_like, body_expr: ...

    # ListLit :: List Expr -> Expr -> Atom
    ListLit: lambda lst: ...

    # Nested :: Expr -> Atom
    Nested: lambda expr: ...


@data
class UOp:
    # FunctionCall :: Context -> Expr -> List Expr -> Operation
    FunctionCall: lambda ctx, fn_expr, arg_lst: ...

    # IndexContainer :: Expr -> Expr -> Operation
    IndexContainer: lambda container, arg: ...


@data
class BOp:
    # Unary :: UOp -> BOp
    Unary: lambda unary: ...

    # Dual :: PrecedenceTable -> Str -> Left -> Right -> BOp
    Dual: lambda p_table, op_name, left_exp, right_exp: ...
