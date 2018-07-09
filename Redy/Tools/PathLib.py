import itertools
import os
import io
import functools
import time
from ..Typing import *

try:
    from chardet import detect as _encoding_detect


    def auto_open_file(file, mode):
        with open(file, 'rb') as sample:
            encoding = _encoding_detect(sample.read(1024))['encoding']
        return open(file, mode, encoding=encoding)
except:
    import warnings

    warnings.warn('No module chardet found. `auto_open_file` function could be inefficient.')
    _encodings = ['utf8', 'gb18030', 'gbk', 'latin-1']


    def auto_open_file(file, mode):
        for each in _encodings:
            try:
                stream = open(file, mode, encoding=each)
                stream.read(1)
                stream.seek(0)
                return stream
            except UnicodeError:
                continue
        raise UnicodeError

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
        return str(self) == str(other if isinstance(other, Path) else Path(other))

    def exists(self) -> bool:
        return os.path.exists(self.__str__())

    def is_dir(self) -> bool:
        return os.path.isdir(str(self))

    def move_to(self, path: Union[str, 'Path'], exception_handler: Optional[Callable[[Exception], None]] = None):
        if isinstance(path, str):
            path = Path(path)
        try:
            relative = self.relative()
            if self.is_dir():
                path = path.into(relative)
                if not path.exists():
                    path.mkdir()

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

                _move_to(self, path)
            else:
                with path.into(relative).open('wb') as write_item, self.open('rb') as read_item:
                    write_item.write(read_item.read())
        except Exception as e:
            if exception_handler is None:
                raise e
            exception_handler(e)

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

    def open(self, mode, encoding='utf8'):
        """

        :param mode: the same as the argument `mode` of `builtins.open`
        :param encoding: similar to the argument `encoding` of `builtins.open`.
                         You can use `encoding='auto'` to automatically detect the encoding.
        :return: the same as the return of ``builtins.open`.
        """
        if encoding == 'auto':
            return auto_open_file(str(self), mode)
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

    def collect(self, cond=lambda _: True) -> 'List[Path]':
        for each in self.list_dir(cond):
            if each.is_dir():
                yield from each.collect(cond)
            else:
                yield each
