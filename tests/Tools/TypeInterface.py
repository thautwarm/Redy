from Redy.Typing import *




from Redy.Tools.TypeInterface import Module
import math
assert isinstance(math, Module)

from Redy.Tools.TypeInterface import BuiltinMethod
class S: ...
assert isinstance(S.__init__, BuiltinMethod)