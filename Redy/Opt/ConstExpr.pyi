from typing import Generic, TypeVar, NoReturn

T = TypeVar('T')


class _ConstExpr(Generic[T]):
    def __getitem__(self, item: T) -> T: ...


constexpr: _ConstExpr


class _Const(Generic[T]):
    def __getitem__(self, item: T) -> T: ...


const: _Const


class _Macro:
    def __new__(cls, f: T) -> NoReturn: ...


macro: _Macro


def optimize(f: T) -> T: ...
