import re
import types

from Redy.Collections.Traversal import *
from Redy.Collections import *
from Redy.Tools import PathLib, Path, Version, TypeInterface

from Redy.Collections import Core, Graph, Traversal, LinkedList
from Redy.Async import Accompany, Delegate
from Redy.Magic import Pattern, Classic
from Redy.ADT import Core as GADTCore
from Redy.Opt import ConstExpr

pattern_clear = re.compile('\s+\>\>\> ')
accept_private_doc = ('__add__', '__iadd__', '__sub__', '__isub__', '__mul__', '__imul__',
                      '__le__', '__ge__', '__lt__', '__gt__', '__eq__')


def rep(s: str) -> str:
    return pattern_clear.sub('', s)


def locate(s: str) -> bool:
    return s.__contains__('>>>')


def write(filename: str):
    def _(content: str):
        with open(filename, 'w') as f:
            f.write(content)

    return _


def collect_docstrings(each):
    def _(_each):
        if isinstance(_each, (classmethod, staticmethod)):
            _each = _each.__func__

        if hasattr(_each, '__doc__'):
            doc = _each.__doc__
            if doc:
                yield doc

        if hasattr(_each, '__dict__'):
            for sub in (v for k, v in _each.__dict__.items() if k in accept_private_doc or not k.startswith('_')):
                yield from _(sub)

    return tuple(_(each))


def generate_doc_for(module: Mapping[str, object]):
    path = Path(module.__file__)
    root = path
    while 'README.md' not in root.parent().list_dir():
        root = root.parent()
    directory = root.parent().__str__()
    path = Path(directory, 'tests', str(path)[len(str(root)) + 1:])
    print(f'generating the test script for {path}')
    path.parent().mkdir()

    __all__ = [getattr(module, k) for k in module.__all__]

    codes = []
    for each in __all__:
        docs = collect_docstrings(each)
        doc: str = '\n'.join(docs)

        if not doc:
            continue
        nil = Flow(doc.splitlines())[
            filter_by(locate)
        ][
            map_by(rep)
        ][
            '\n'.join
        ][
            codes.append
        ]
    with open(str(path), 'w') as f:
        f.write("from Redy.Typing import *\n\n\n")
        f.write('\n\n'.join(codes))


if __name__ == '__main__':
    generate_doc_for(Traversal)
    generate_doc_for(Core)
    generate_doc_for(Accompany)
    generate_doc_for(PathLib)
    generate_doc_for(Delegate)
    generate_doc_for(Graph)
    generate_doc_for(LinkedList)
    generate_doc_for(Pattern)
    generate_doc_for(Version)
    generate_doc_for(TypeInterface)
    generate_doc_for(Classic)
    generate_doc_for(GADTCore)
    generate_doc_for(ConstExpr)

