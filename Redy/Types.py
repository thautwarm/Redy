"""
Currently, PyCharm doesn't support partial specialization.
So `Action` and `Func` might not get corrent hinting.
However it's certainly that this support will come up sooner.
"""
from typing import *

T = TypeVar('T')

# geeneric type of return
TR = TypeVar('TR')

# generic type of an element in the container.
TE = TypeVar('TE')

T1 = TypeVar('T1')

T2 = TypeVar('T2')

T3 = TypeVar('T3')

Func = Callable[[T], TR]

Thunk = Callable[[], TR]

Action = Func[T, None]

Stream = Iterable[T]

Ctx = Dict[str, Any]

# CtxGetter = Func[]
#
# if __name__ == '__main__':
#     # use mypy to test type constructors
#     def act(x: int) -> None:
#         pass
#
#
#     def test(arg: Action[int]):
#         pass
#
#
#     test(act)
#
#
#     def func2(x: int) -> Stream:
#         pass
#
#
#     Fx = Func[int, Stream]
#
#
#     def test2(f: Fx):
#         pass
#
#
#     test2(func2)
#
#
#     def func3() -> Stream:
#         ...
#
#
#     def test3(x: Thunk[Stream]):
#         pass
#
#
#     test3(func3)
