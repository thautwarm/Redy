"""
This module is for the support of graph engine service.
"""

from ..Types import *


class Graph(Generic[TE]):
    __slots__ = ['data', 'neighbors']

    def __init__(self, data: TE, neighbors: 'List[Graph]') -> None:
        self.data = data
        self.neighbors = neighbors
