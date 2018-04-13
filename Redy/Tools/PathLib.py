import os
import io
from ..Types import *

__all__ = ['Path']


def join_path(components: Iterable[str]):
    if not components:
        return os.path.abspath('.')
    head, *tail = components
    if head is '':
        head = os.sep
    return os.path.abspath(os.path.join(head, *tail))


class Path:
    """
    >>> from Redy.Tools import Path
    >>> p = Path('.')
    >>> p.abs()
    >>> p.is_dir()
    >>> p.list_dir()
    >>> p.parent()
    >>> list(p.collect())
    >>> p.__iter__()
    >>> new = p.into('justfortest')
    >>> new.mkdir()
    >>> new.mkdir()
    >>> new.delete()
    >>> p.relative()
    >>> new.open('w')
    >>> new.delete()
    >>> assert new == str(new)
    >>> root, *_ = new

    """
    __slots__ = ["_path"]

    def __init__(self, *path_sections: str):

        self._path: Sequence[str] = join_path(path_sections).split(os.sep)

    def __iter__(self):
        yield from self._path

    def __eq__(self, other: Union[str, 'Path']):
        return str(self) == os.path.abspath(str(other))

    def is_dir(self) -> bool:
        return os.path.isdir(str(self))

    def list_dir(self, filter_fn=None) -> 'List[Path]':
        path = str(self)
        items = map(lambda _: join_path((path, _)), os.listdir(path))
        if filter_fn is not None:
            items = filter(filter_fn, items)
        return list(map(Path, items))

    def abs(self) -> str:
        return str(self)

    def relative(self) -> str:
        return os.path.split(str(self))[1]

    def parent(self) -> 'Path':
        return Path(os.path.split(str(self))[0])

    def __truediv__(self, other: str) -> 'Path':
        return Path(*self._path, other)

    def __getitem__(self, item) -> str:
        return self._path[item]

    def __str__(self):
        return os.sep.join(self._path)

    def open(self, mode):
        return io.open(str(self), mode)

    def delete(self):
        if self.is_dir():
            for each in self.list_dir():
                each.delete()
            os.removedirs(str(self))
        else:
            os.remove(str(self))

    def into(self, directory: str) -> 'Path':
        return Path(*self._path, directory)

    def mkdir(self):
        try:
            os.makedirs(self.__str__())
        except IOError:
            pass

    def collect(self, cond=lambda _: True) -> 'List[Path]':
        for each in self.list_dir(cond):
            if each.is_dir():
                yield from each.collect(cond)
            else:
                yield each
