import ast
import inspect
import types
import collections
from .basic import Service

try:
    from .bytecode_api import BCService, Bytecode
    import bytecode
except:
    pass


class ASTService(Service[ast.AST]):
    pass


class Feature:
    func: types.FunctionType

    def __init__(self, *services: Service, state: dict = None):
        def _flatten(it, found):
            for each in it:
                if isinstance(each, collections.Iterable):
                    yield from _flatten(each, found)
                else:
                    if each not in found:
                        yield each

        self._state = state if state else {}

        self._services = list(_flatten(services, set()))

        self._ast_services = None
        self._bc_services = None

        # function essential factors
        self.func: types.FunctionType = None

    def initialize_env(self):
        services = self._services
        ast_services = []
        bc_services = []
        ast_services_add = ast_services.append
        bc_services_add = bc_services.append

        for each in services:
            if isinstance(each, ASTService):
                ast_services_add(each)

            elif isinstance(each, BCService):
                bc_services_add(each)
            else:
                raise TypeError("Requires a ASTService or BCService, got {}.".format(type(each)))
            each.initialize_env(self)

        self._bc_services = bc_services
        self._ast_services = ast_services

    def add_service(self, service: Service):
        self._services.append(service)

    def rem_service(self, service):
        self._services.remove(service)

    @property
    def state(self):
        return self._state

    def _apply_ast_service(self, elem):
        done = False
        for dispatch_getter in self._ast_services:
            application = dispatch_getter(self, elem)
            if application is not None:
                elem = application(self, elem)
                if not done:
                    done = True

        return elem if done else self.ast_transform(elem)

    def _apply_bc_service(self, bc):
        for dispatch_getter in self._bc_services:
            application = dispatch_getter(self, bc)
            if application is not None:
                bc = application(self, bc)
        return bc

    def ast_transform(self, node):
        for field, old_value in ast.iter_fields(node):
            if isinstance(old_value, list):
                new_values = []
                for value in old_value:
                    if isinstance(value, ast.AST):
                        value = self._apply_ast_service(value)
                        if value is None:
                            continue
                        elif not isinstance(value, ast.AST):
                            new_values.extend(value)
                            continue
                    new_values.append(value)
                old_value[:] = new_values
            elif isinstance(old_value, ast.AST):
                new_node = self._apply_ast_service(old_value)
                if new_node is None:
                    delattr(node, field)
                else:
                    setattr(node, field, new_node)
        return node

    def bc_transform(self, bc: 'Bytecode'):
        apply = self._apply_bc_service
        new_bc = Bytecode([apply(each) for each in bc])
        new_bc.argnames = bc.argnames
        new_bc._copy_attr_from(bc)
        return new_bc

    def __call__(self, func: types.FunctionType):
        self.func = func
        self.initialize_env()

        if self._ast_services:
            src_code: str = inspect.getsource(func)
            node = ast.parse(src_code)
            node = self.ast_transform(node)
            if not isinstance(node, ast.AST):
                return node

            code_object = compile(node, self.func.__code__.co_filename, 'exec')
            code_object = next(each for each in code_object.co_consts if
                               isinstance(each, types.CodeType) and each.co_name == func.__name__)
        else:
            code_object = func.__code__

        if self._bc_services:
            try:
                bc = Bytecode.from_code(code_object)
                bc = self.bc_transform(bc)
                if not isinstance(bc, Bytecode):
                    return bc
                bc.flags |= bytecode.CompilerFlags.OPTIMIZED
                code_object = bc.to_code()
            except NameError:
                import warnings
                warnings.warn('You have register some bytecode services but the library `bytecode` is required.\n'
                              'See `https://github.com/vstinner/bytecode` and you can get it by'
                              '`pip install bytecode`.')
        f = types.FunctionType(code_object, func.__globals__, func.__name__, func.__defaults__, func.__closure__)
        return f


feature = Feature
