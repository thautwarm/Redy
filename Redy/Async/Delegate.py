from enum import Enum
from ..Typing import *

_Action = Callable[[T, TE, TR], None]

__all__ = ['Delegate']


class Delegate:
    """
    `delegate` represents a series of actions sharing the same context.
    >>> from Redy.Async.Delegate import Delegate
    >>> action = lambda task, product, globals: print(task.__name__)
    >>> delegate = Delegate(action)
    >>> def action2(task, product, globals):
    >>>     print(product)
    # insert at the end
    >>> delegate.insert(action2, Delegate.Where.after(lambda _: False))
    >>> delegate.insert(action, Delegate.Where.before(lambda _: _.__name__ == 'action2'))
    >>> delegate += (lambda task, product, ctx: print("current product: {}".format(product)))
    >>> delegate.add(lambda task, product, ctx: print("current product: {}".format(product)))
    >>> fake_task = lambda : None
    >>> delegate(fake_task, "out", None)
    """

    def __init__(self,
                 actions: Union[Iterable[_Action], _Action] = ()) -> None:
        self.actions = list(actions) if isinstance(actions,
                                                   Iterable) else [actions]

    def __call__(self, task, product, globals: Thunk[Ctx]):
        for each in self.actions:
            each(task, product, globals)

    def __len__(self):
        return len(self.actions)

    def __iadd__(self, other):
        """
        add a new action with the lowest priority.
        >>> delegate: Delegate
        >>> delegate += (lambda task, product, ctx: print("current product: {}".format(product)))
        """
        self.actions.append(other)
        return self

    def add(self, other):
        """
        add a new action with the lowest priority.
        >>> delegate: Delegate
        >>> delegate.add(lambda task, product, ctx: print("current product: {}".format(product)))
        """
        self.actions.append(other)

    def insert(self, action: Action, where: 'Union[int, Delegate.Where]'):
        """
        add a new action with specific priority

        >>> delegate: Delegate
        >>> delegate.insert(lambda task, product, ctx: print(product), where=Delegate.Where.after(lambda action: action.__name__ == 'myfunc'))
        the codes above inserts an action after the specific action whose name is 'myfunc'.
        """
        if isinstance(where, int):
            self.actions.insert(where, action)
            return

        here = where(self.actions)
        self.actions.insert(here, action)

    class _WhereDescriptor(Enum):
        before = 0
        after = 1

    class Where:
        def __init__(self, cond: Callable[[Action], bool],
                     option: 'Delegate._WhereDescriptor') -> None:
            self.cond = cond
            self.before_or_after = option

        @classmethod
        def after(cls, cond):
            return cls(cond, Delegate._WhereDescriptor.after)

        @classmethod
        def before(cls, cond):
            return cls(cond, Delegate._WhereDescriptor.before)

        def __call__(self, actions: List[Action]):
            i = 0
            for i, action in enumerate(actions):
                if self.cond(action):
                    break

            if self.before_or_after == Delegate._WhereDescriptor.before:
                return i
            return i + 1

    def __str__(self):
        return str([e.__name__ for e in self.actions])

    def __repr__(self):
        return self.__str__()
