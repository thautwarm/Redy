from .common import *


class _InternalCell:
    def __init__(self, value):
        self.cell_contents = value


class AsStore(ASTService):
    names_to_supervise: typing.Dict[str, typing.Callable[[ast.Name], None]] = Require("supervise.names", dict)
    current_ctx: CompilingTimeContext = RequestContext()

    def get_dispatch(self, elem) -> typing.Optional[typing.Callable]:
        if isinstance(elem, ast.Subscript) and isinstance(elem.value, ast.Name):
            if check_service(self.current_ctx.get(elem.value.id), self):
                return self._ctx_to_store

    def _ctx_to_store(self, elem: ast.Subscript):
        value = elem.slice.value
        if not isinstance(value, ast.Name):
            raise TypeError("`AsStore[Arg]` the `Arg` must be of type `ast.Name` at \n{}.".format(
                    get_location(elem, self.feature)))

        return ast.Name(lineno=value.lineno, col_offset=value.col_offset, id=value.id, ctx=ast.Store())
