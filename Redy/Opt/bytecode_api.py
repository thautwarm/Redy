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

        looked_up = next((snd for fst, snd in self._asoc_lst if fst == k), undef)

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
        idx = next((idx for idx, [fst, _] in enumerate(asoc_lst) if fst == key), None)
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


class BCService(Service):
    pass
