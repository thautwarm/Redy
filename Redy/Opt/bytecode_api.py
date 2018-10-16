"""

Bytecode.from_code is awesome!
"""
import typing
import opcode
import dis
import abc
import sys
import bytecode
from bytecode import concrete
from collections import Mapping, Hashable
from .basic import Service

Bytecode = bytecode.Bytecode

_undef = object()  # for people might save None object sometimes.


class _GeneralMapping(Mapping):
    def __init__(self):
        self._asoc_lst = []
        self._dct = {}

    def __len__(self) -> int:
        return len(self._asoc_lst) + len(self._dct)

    def __iter__(self):
        yield from self._dct
        yield from (kv[0] for kv in self._asoc_lst)

    def __getitem__(self, k):
        if isinstance(k, Hashable):
            try:
                return self._dct[k]
            except TypeError:
                # Actually we should ensure all the nested structure in the object `k` should be hashable,
                # but it does cost.
                # `dict.__getitem__` invokes the builtin hashing method, which
                # failed if and only if this object isn't really hashable.
                # In the definition of `_GeneralMapping.__setitem__` there is a similar case.
                pass
        undef = _undef

        looked_up = next((snd for fst, snd in self._asoc_lst if fst == k),
                         undef)

        if looked_up is undef:
            raise KeyError(k)
        return looked_up

    def __setitem__(self, key, value):
        if isinstance(key, Hashable):
            try:
                self._dct[key] = value
                return
            except TypeError:
                pass

        asoc_lst = self._asoc_lst
        idx = next(
            (idx for idx, [fst, _] in enumerate(asoc_lst) if fst == key), None)
        if idx is None:
            asoc_lst.append([key, value])
            return
        asoc_lst[idx][1] = value


def _ConvertBytecodeToConcrete(self, code):
    assert isinstance(code, Bytecode)
    self.bytecode = code

    # temporary variables
    self.instructions = []
    self.jumps = []
    self.labels = {}

    # used to build ConcreteBytecode() object
    self.consts = _GeneralMapping()
    self.names = []
    self.varnames = []


if bytecode.__version__ < '0.8':
    concrete._ConvertBytecodeToConcrete.__init__ = _ConvertBytecodeToConcrete
    _stack_effects_use_opargs = {
        opcode.opmap.get(op_name, None)
        for op_name in ('UNPACK_SEQUENCE', 'UNPACK_EX', 'BUILD_STRING',
                        'BUILD_MAP_UNPACK_WITH_CALL', 'BUILD_MAP',
                        'BUILD_CONST_KEY_MAP', 'RAISE_VARARGS',
                        'CALL_FUNCTION', 'CALL_METHOD', 'CALL_FUNCTION_KW',
                        'CALL_FUNCTION_EX', 'MAKE_FUNCTION', 'BUILD_SLICE',
                        'FORMAT_VALUE')
    }

    _stack_effects = {
        # NOTE: the entries are all 2-tuples.  Entry[0/False] is non-taken jumps.
        # Entry[1/True] is for taken jumps.

        # opcodes not in dis.stack_effect
        opcode.opmap['EXTENDED_ARG']: (0, 0),
        opcode.opmap['NOP']: (0, 0),

        # Jump taken/not-taken are different:
        opcode.opmap['JUMP_IF_TRUE_OR_POP']: (-1, 0),
        opcode.opmap['JUMP_IF_FALSE_OR_POP']: (-1, 0),
        opcode.opmap['FOR_ITER']: (1, -1),
        opcode.opmap['SETUP_WITH']: (1, 6),
        opcode.opmap['SETUP_ASYNC_WITH']: (0, 5),
        opcode.opmap['SETUP_EXCEPT']: (0, 6),  # as of 3.7, below for <=3.6
        opcode.opmap['SETUP_FINALLY']: (0, 6),  # as of 3.7, below for <=3.6
    }

    # More stack effect values that are unique to the version of Python.
    if sys.version_info < (3, 7):
        _stack_effects.update({
            opcode.opmap['SETUP_WITH']: (7, 7),
            opcode.opmap['SETUP_EXCEPT']: (6, 9),
            opcode.opmap['SETUP_FINALLY']: (6, 9),
        })

    _stack_effects_use_opargs = {
        opcode.opmap.get(op_name, None)
        for op_name in ('UNPACK_SEQUENCE', 'UNPACK_EX', 'BUILD_STRING',
                        'BUILD_MAP_UNPACK_WITH_CALL', 'BUILD_MAP',
                        'BUILD_CONST_KEY_MAP', 'RAISE_VARARGS',
                        'CALL_FUNCTION', 'CALL_METHOD', 'CALL_FUNCTION_KW',
                        'CALL_FUNCTION_EX', 'MAKE_FUNCTION', 'BUILD_SLICE',
                        'FORMAT_VALUE')
    }

    def stack_effect(self, jump=None):
        effect = _stack_effects.get(self.opcode, None)
        if effect is not None:
            return max(effect) if jump is None else effect[jump]

        # TODO: if dis.stack_effect ever expands to take the 'jump' parameter
        # then we should pass that through, and perhaps remove some of the
        # overrides that are set up in _init_stack_effects()

        # Each of following opcodes has a stack_effect indepent of its
        # argument:
        # 1. Whose argument is not represented by an integer.
        # 2. Whose stack effect can be calculated without using oparg
        #    from this link:
        # https://github.com/python/cpython/blob/master/Python/compile.c#L859

        use_oparg = self.opcode in _stack_effects_use_opargs
        arg = (self._arg if use_oparg and isinstance(self._arg, int) else
               0 if self.opcode >= opcode.HAVE_ARGUMENT else None)
        return dis.stack_effect(self.opcode, arg)


class BCService(Service):
    pass
