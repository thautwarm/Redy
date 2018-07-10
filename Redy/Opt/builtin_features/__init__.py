from ._constant_link import *
from ._constexpr import *
from ._goto import *
from ._macro import *

const_decl = ConstDecl()
const_eval = ConstEval()
const_link = ConstLink()
name_supervisor = NameSupervisor()

const = (const_decl, const_link, name_supervisor)
constexpr = (const_eval, const_link, name_supervisor)
label = GoToMarker()
goto = (label, GoToCodeGenRewriter(), name_supervisor)
