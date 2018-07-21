from Redy.Typing import *

import unittest
import pytest
class Test_Redy_Collections_Graph(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def test_2102660008680(self):
        from Redy.Collections.Graph import Node
        a = Node(1)
        b = Node(2)
        a.connect(b)
        b.connect(a, both=True)