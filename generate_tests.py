import re

from Redy.Collections.Traversal import *
from Redy.Collections import *
from Redy.Tools import PathLib, Path

from Redy.Collections import Core, Graph, Traversal, LinkedList
from Redy.Async import Accompany, Delegate

pattern_clear = re.compile('\s+\>\>\> ')


def rep(s: str) -> str:
    return pattern_clear.sub('', s)


def locate(s: str) -> bool:
    return s.__contains__('>>>')


def write(filename: str):
    def _(content: str):
        with open(filename, 'w') as f:
            f.write(content)

    return _


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
        doc: str = each.__doc__
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
        f.write("from Redy.Types import *\n\n\n")
        f.write('\n\n'.join(codes))


if __name__ == '__main__':
    generate_doc_for(Traversal)
    generate_doc_for(Core)
    generate_doc_for(Accompany)
    generate_doc_for(PathLib)
    generate_doc_for(Delegate)
    generate_doc_for(Graph)
    generate_doc_for(LinkedList)
