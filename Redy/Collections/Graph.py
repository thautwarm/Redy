"""
This module is for loading graph engine services.
"""

from ..Types import *


class Graph(Generic[TE]):
    __slots__ = ['data', 'neighbors']

    def __init__(self, data: TE, neighbors: 'List[Graph]') -> None:
        self.data = data
        self.neighbors = neighbors
