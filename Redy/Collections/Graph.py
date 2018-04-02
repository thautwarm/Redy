"""
This module is for loading graph engine services.
"""

from ..Types import *

__all__ = ['Node']


class Node(Generic[TE]):
    """
    >>> from Redy.Collections.Graph import Node
    >>> a = Node(1)
    >>> b = Node(2)
    >>> a.connect(b)
    >>> b.connect(a, both=True)
    """
    __slots__ = ['data', 'neighbors']

    def __init__(self, data: TE, neighbors: 'Set[Node]' = None) -> None:
        self.data = data
        self.neighbors = neighbors if neighbors else set()

    def connect(self, other: 'Node', both=False):
        self.neighbors.add(other)
        if both:
            other.connect(self)
