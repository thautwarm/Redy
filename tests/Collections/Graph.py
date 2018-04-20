from Redy.Typing import *


from Redy.Collections.Graph import Node
a = Node(1)
b = Node(2)
a.connect(b)
b.connect(a, both=True)