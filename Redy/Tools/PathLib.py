import itertools
import os
import io
import functools
import typing
import time
from ..Typing import *

__all__ = ['Path']

_encodings = ['utf8', 'gb18030', 'gbk', 'latin-1']


def default_auto_open(file, mode):
    for each in _encodings:
        try:
            stream = open(file, 'r', encoding=each)
            stream.read(1)
            stream.seek(0)
            if mode == 'r':
                return stream
            stream.close()
            return open(file, mode, encoding=each)

        except UnicodeError:
            continue

    raise UnicodeError


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


def _convert_to_path(it):
    if isinstance(it, str):
        return Path(it)
    return it


def _convert_to_str(it):
    if isinstance(it, str):
        return it
    return Path(it)


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
    >>> assert "justfortest" in p
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

        if path_sections:  # check if it's `~/somewhere`
            head, *tail = path_split(path_sections[0])
            if head == '~':
                path_sections = (os.path.expanduser('~'), *tail, *path_sections[1:])

        self._path = path_split(os.path.abspath(path_join(path_sections)))

    def __contains__(self, item):
        if isinstance(item, str):
            return item in (each[-1] for each in self.list_dir())

        return item in self.list_dir()

    def __iter__(self):
        yield from self._path

    def __eq__(self, other: Union[str, 'Path']):
        return str(self) == _convert_to_str(other)

    def exists(self) -> bool:
        return os.path.exists(str(self))

    def is_dir(self) -> bool:
        return os.path.isdir(str(self))

    def move_to(self, destination: Union[str, 'Path'], exception_handler: Optional[Callable[[Exception], None]] = None):
        if isinstance(destination, str):
            destination = Path(destination)
        try:
            relative = self.relative()
            if self.is_dir():
                destination = destination.into(relative)
                if not destination.exists():
                    destination.mkdir()

                def _move_to(from_: Path, to_: Path):
                    for each in from_.list_dir():
                        relative = each.relative()
                        if each.is_dir():
                            each_to = to_.into(relative)
                            if not each_to.exists():
                                each_to.mkdir()
                            _move_to(each, each_to)
                        else:
                            with each.open('rb') as read_item, to_.into(relative).open('wb') as write_item:
                                write_item.write(read_item.read())

                _move_to(self, destination)
            else:
                with destination.into(relative).open('wb') as write_item, self.open('rb') as read_item:
                    write_item.write(read_item.read())
        except Exception as e:
            if exception_handler is None:
                raise e
            exception_handler(e)

    def list_dir(self, filter_fn=None) -> 'Tuple[Path, ...]':
        """
        * the `self` Path object is assumed to be a directory

        :param filter_fn:
            a `None` object or
            a predicative function `str -> bool` which will be applied on the
            filename/directory in `self` directory.

        :return:
            a tuple of Path objects
            each of which represents a file/directory
            in `self` directory.

            If the filter_fn is not None,
            each item in return tuple whose filename/directory name
            doesn't match the `filter_fn` will filtered.

        e.g:
            - Dir1
                - File.py
                - File.pyi
                - File.pyx
            Dir1.list_dir(lambda path: '.py' in py)
            => [<Path object of File1.py>]

            Dir1.list_dir(lambda path: print(path))
            IO:
              File.py
              File.pyi
              File.pyx
            => []
        """

        path = str(self)
        items = os.listdir(path)
        if filter_fn is not None:
            items = filter(filter_fn, items)

        return tuple(Path(path_join((path, item))) for item in items)

    def abs(self) -> str:
        """
        :return: absolute path of Path object
        """
        return str(self)

    def relative(self, start: typing.Optional[typing.Union['Path', str]] = None) -> str:
        """
        :param start: an object of NoneType or Path or str.
        :return: a string
            If `start` is None:
                returns the relative path of current Path object from its own directory.
            Else:
                returns the relative path of current Path object from the `start` path.
        e.g
        - Dir1
            - Dir2
                - File1
                - File2
            - Dir3
                - File3
            Path(<path of File1>).relative() => "<filename of File1>"
            Path(<path of Dir2>).relative() => "<directory name of Dir1>"
            Path(<path of File3>).relative(<path of File1>) => "../Dir2/<filename of File1>"
        """
        if start is None:
            return os.path.split(str(self))[1]
        return os.path.relpath(str(self), start)

    def parent(self) -> 'Path':
        return Path(*self._path[:-1], no_check=True)

    def __truediv__(self, other: str) -> 'Path':
        return Path(*self._path, *path_split(other), no_check=True)

    def __getitem__(self, item: Union[Callable[[str], bool], int]) -> Optional[str]:
        if callable(item):
            return next(filter(item, self._path), None)

        return self._path[item]

    def __str__(self):
        return path_join(self._path)

    def open(self, mode, encoding='auto'):
        """
        :param mode: the same as the argument `mode` of `builtins.open`
        :param encoding: similar to the argument `encoding` of `builtins.open` which is compatible to io.open.
                         - `encoding='auto'` to automatically detect the encoding.n
                         - `encoding=<function>`
                            If you want to apply custom encoding detection method, you could pass
                            an encoding detecting function `(filename: str) -> (encoding: str)` here
                            which receives the filename and returns encoding of the file.
        :return: the same as the return of ``builtins.open`.
        """
        if 'b' in mode or 'w' in mode:
            return io.open(str(self), mode)

        if callable(encoding):
            encoding = encoding(str(self))

        if encoding == 'auto':
            return default_auto_open(str(self), mode)

        return io.open(str(self), mode, encoding=encoding)

    def delete(self):
        if self.is_dir():
            for each in self.list_dir():
                each.delete()
            os.rmdir(str(self))
        else:
            os.remove(str(self))

    def into(self, file_or_directory: str) -> 'Path':
        if '/' not in file_or_directory and '\\' not in file_or_directory:
            return Path(*self._path, file_or_directory, no_check=True)

        return Path(*self._path, file_or_directory.strip('/\\'))

    def mkdir(self, warning=True):
        try:
            os.makedirs(str(self))
        except OSError as e:
            if warning:
                print(e)
            pass
        return self

    def collect(self, cond=None) -> 'typing.Iterable[Path]':
        for each in self.list_dir(cond):
            if each.is_dir():
                yield from each.collect(cond)
            else:
                yield each
