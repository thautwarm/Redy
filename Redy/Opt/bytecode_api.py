"""

Bytecode.from_code is awesome!
"""
import typing
import opcode
import dis
import bytecode
import abc
from .basic import Service

Bytecode = bytecode.Bytecode


class BCService(Service[Bytecode]):
    pass
