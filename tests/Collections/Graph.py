from Redy.Typing import *

import unittest
class Test_Redy_Collections_Graph(unittest.TestCase):
    def test_1722268482280(self):
        from Redy.Collections.Graph import Node
        a = Node(1)
        b = Node(2)
        a.connect(b)
        b.connect(a, both=True)