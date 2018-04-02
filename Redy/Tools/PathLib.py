import os
import io
from ..Types import *

__all__ = ['Path']


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

    """
    __slots__ = ["_path"]

    def __init__(self, *path_sections: str):
        self._path = path_sections

    def __iter__(self):
        yield from self._path

    def __eq__(self, other):
        return self.abs() == os.path.abspath(str(other))

    def is_dir(self) -> bool:
        return os.path.isdir(str(self))

    def list_dir(self, filter_fn=None) -> 'List[Path]':
        path = str(self)
        items = map(lambda _: os.path.join(path, _), os.listdir(str(self)))
        if filter_fn is not None:
            items = filter(filter_fn, items)
        return list(map(Path, items))

    def abs(self) -> str:
        return os.path.abspath(str(self))

    def relative(self) -> str:
        return os.path.split(str(self))[1]

    def parent(self) -> 'Path':
        return Path(os.path.split(str(self))[0])

    def __truediv__(self, *others: str) -> 'Path':
        return Path(*self._path, *map(str, others))

    def __getitem__(self, item) -> str:
        return str(self)[item]

    def __str__(self):
        return os.path.join(*self._path)

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
        return Path(*self._path, str(directory))

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
