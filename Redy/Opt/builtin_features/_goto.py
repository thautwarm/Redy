from .common import *
from Redy.Collections import Traversal


class _InternalTriMap(AggregateIndexer):
    jump_name: str
    label_name: str
    var_name: str
    label_object: bytecode.Label


class GoToMarker(ASTService):
    """
    x : label
    y : label

    with x:
        ...


    x.jump()

    """

    def __init__(self):
        self._cache_indices = None

    def setup_env(self, feature: 'Feature') -> None:
        pass

    tri_map: _InternalTriMap = Require("goto.label-jump-manager", _InternalTriMap)
    current_ctx: CompilingTimeContext = RequestContext()

    def is_depth_first(self):
        return False

    def notify_define_label(self, node):
        return isinstance(node, ast.Name) and check_service(self.current_ctx.get(node.id), self)

    def notify_found_label_usage(self, node):
        return isinstance(node, ast.Name) and self.tri_map.index_get(None, var_name=node.id)

    def get_dispatch(self, elem: ast.AST):
        if isinstance(elem, ast.AnnAssign) and isinstance(elem.target, ast.Name):
            # define label
            annotation = elem.annotation
            if self.notify_define_label(annotation):
                return self.define_label

        elif isinstance(elem, ast.With):
            items = elem.items
            indices = [idx for idx, some in enumerate(item.context_expr for item in items) if
                       self.notify_found_label_usage(some)]
            if indices:
                self._cache_indices = indices
                return self.mark_block

        elif isinstance(elem, ast.Call) and not elem.args and not elem.keywords:
            attr = elem.func
            if isinstance(attr, ast.Attribute) and isinstance(attr.value, ast.Name):
                if self.notify_found_label_usage(attr.value):
                    if attr.attr == 'jump':
                        return self.jump
                    elif attr.attr == 'mark':
                        return self.mark
                    raise ValueError("Unknown attributes for goto at {}.".format(get_location(attr, self.feature)))

    def define_label(self, elem: ast.AST):
        ann_assign: ast.AnnAssign = elem
        label_id = ann_assign.target.id

        if self.tri_map.index_get(None, label_name=label_id):
            raise ValueError("Redefinition of jumping label at {}".format(get_location(elem, self.feature)))

        label_name = 'label.{}'.format(len(self.tri_map))
        self.tri_map.index_set(var_name=label_id, label_name=label_name, label_object=bytecode.Label())

        return []

    def mark_block(self, elem: ast.AST):
        return_ast_suite = []
        with_: ast.With = elem
        items = with_.items
        for idx in self._cache_indices:
            item = items[idx]
            name = item.context_expr
            index_map = self.tri_map.index_get(None, var_name=name.id)
            name.id = index_map['label_name']
            return_ast_suite.append(
                    ast.Attribute(lineno=name.lineno, col_offset=name.col_offset, value=name, attr='block',
                                  ctx=ast.Load()))
        for idx in reversed(self._cache_indices):
            del items[idx]
        if items:
            return_ast_suite.append(self.feature.ast_transform(elem))
            return return_ast_suite

        return_ast_suite.extend([self.feature.apply_ast_service(each) for each in with_.body])
        return return_ast_suite

    def mark(self, elem):
        call: ast.Call = elem
        attr = call.func
        attr.value.id = self.tri_map.index_get(None, var_name=attr.value.id)['label_name']
        return attr

    def jump(self, elem):
        call: ast.Call = elem
        attr = call.func
        var_name = attr.value.id
        jump_name = 'jump.{}'.format(len(self.tri_map))
        self.tri_map.index_set(var_name=var_name, jump_name=jump_name)
        attr.value.id = jump_name
        return attr


_const_place = opcode.opmap['LOAD_NAME'], opcode.opmap['LOAD_GLOBAL']


class GoToCodeGenRewriter(BCService):
    tri_map: _InternalTriMap = Require("goto.label-jump-manager", _InternalTriMap)

    def __init__(self):
        self._index_map = None
        self._activated = []

    def is_depth_first(self):
        return False

    def get_dispatch(self, bc: bytecode.Instr):
        if not self._activated:
            if hasattr(bc, 'opcode') and bc.opcode in _const_place:
                index_map = self.tri_map.index_get(None, label_name=bc.arg)
                if index_map is None:
                    index_map = self.tri_map.index_get(None, jump_name=bc.arg)
                    if index_map is not None:
                        self._index_map = index_map
                        return self.linking_jump

                    return
                self._index_map = index_map
                return self.linking_label
        else:
            return self.cleanup

    def linking_label(self, bc: bytecode.Instr):
        label_object = self._index_map['label_object']
        yield label_object
        self._activated = [0, 0, 0]

    def linking_jump(self, bc: bytecode.Instr):
        label_object = self._index_map['label_object']
        yield bytecode.Instr('JUMP_ABSOLUTE', label_object)
        self._activated = [0, 0, 0]

    def cleanup(self, _):
        self._activated.pop()
        yield from ()
