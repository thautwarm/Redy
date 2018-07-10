from ._constant_link import *
from ._constexpr import *
from ._goto import *

const_decl = ConstDecl()
const_eval = ConstEval()
const_link = ConstLink()

const = (const_decl, const_link)
constexpr = (const_eval, const_link)
label = GoToMarker()
goto = (label, GoToCodeGenRewriter())
