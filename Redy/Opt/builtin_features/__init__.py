from ._constant_link import *
from ._constexpr import *
from ._goto import *
from ._macro import *
from ._as_store import AsStore

const_decl = ConstDecl()
const_eval = ConstEval()
const_link = ConstLink()
name_supervisor = NameSupervisor()
as_store = AsStore()

const = (const_decl, const_link, name_supervisor)
constexpr = (const_eval, const_link, name_supervisor)
label = GoToMarker()
goto = (label, GoToCodeGenRewriter(), name_supervisor)
