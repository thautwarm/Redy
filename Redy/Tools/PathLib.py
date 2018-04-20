import os
import io
import functools
import time
from ..Typing import *

__all__ = ['Path']


def path_split(components: str) -> Tuple[str, ...]:
    def _split(_components: str) -> Iterable[str]:
        head, end = os.path.split(_components)
        if not end and head == _components:
            yield head
        else:
            if head:
                yield from _split(head)

            yield end

    return tuple(_split(components)) if components else ()


def path_join(components: Iterable[str]) -> str:
    components = iter(components)

    try:
        path_head = next(components)
    except StopIteration:
        return '.'

    # noinspection PyTypeChecker
    return functools.reduce(os.path.join, components, path_head)


class Path:
    """
    >>> from Redy.Tools import Path
    >>> p = Path('.')
    >>> p.abs()
    >>> p.is_dir()
    >>> p.list_dir()
    >>> p.parent()
    >>> p.__iter__()
    >>> new = p.into('justfortest')
    >>> new.mkdir()
    >>> new.mkdir()
    >>> print(new._path)
    >>> new.delete()
    >>> p.relative()
    >>> tuple(p.collect(lambda _: _.endswith('.py')))
    >>> new.mkdir()
    >>> new.into('some').mkdir().into("somefile").open('w').close()
    >>> new.delete()
    >>> assert new == str(new)
    >>> root, *_ = new
    >>> print(f'0-th elem of arr{new._path}: ', new[0])
    >>> print(f'the elem where endswith .py of arr{new._path}', new[lambda _: _.endswith('.py')])

    """
    __slots__ = ["_path"]

    def __init__(self, *path_sections: str, no_check=False):
        if no_check:
            self._path = path_sections
            return

        self._path = path_split(os.path.abspath(path_join(path_sections)))

    def __iter__(self):
        yield from self._path

    def __eq__(self, other: Union[str, 'Path']):
        return str(self) == str(other if isinstance(other, Path) else Path(other))

    def is_dir(self) -> bool:
        return os.path.isdir(str(self))

    def list_dir(self, filter_fn=None) -> 'Tuple[Path, ...]':
        path = str(self)
        items = map(lambda _: path_join((path, _)), os.listdir(path))
        if filter_fn is not None:
            items = filter(filter_fn, items)
        return tuple(map(Path, items))

    def abs(self) -> str:
        return str(self)

    def relative(self) -> str:
        return os.path.split(str(self))[1]

    def parent(self) -> 'Path':
        return Path(*self._path[:-1], no_check=True)

    def __truediv__(self, other: str) -> 'Path':
        return Path(*self._path, *path_split(other), no_check=True)

    def __getitem__(self, item: Union[Callable[[str], bool], int]) -> Optional[str]:
        if callable(item):
            try:
                return next(filter(item, self._path))
            except StopIteration:
                return None

        return self._path[item]

    def __str__(self):
        return path_join(self._path)

    def open(self, mode):
        return io.open(str(self), mode)

    def delete(self):
        if self.is_dir():
            for each in self.list_dir():
                each.delete()
            os.rmdir(str(self))
        else:
            os.remove(str(self))

    def into(self, file_or_directory: str) -> 'Path':
        return Path(*self._path, file_or_directory.strip('/\\'), no_check=True)

    def mkdir(self):
        try:
            os.mkdir(str(self))
        except IOError:
            pass
        return self

    def collect(self, cond=lambda _: True) -> 'List[Path]':
        for each in self.list_dir(cond):
            if each.is_dir():
                yield from each.collect(cond)
            else:
                yield each
