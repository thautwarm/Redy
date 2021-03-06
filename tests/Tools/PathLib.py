from Redy.Typing import *

import unittest
import pytest
class Test_Redy_Tools_PathLib(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def test_2309557027928(self):
        from Redy.Tools import Path
        p = Path('.')
        p.abs()
        p.is_dir()
        p.list_dir()
        p.parent()
        p.__iter__()
        new = p.into('justfortest')
        new.mkdir()
        new.mkdir()
        assert "justfortest" in p
        print(new._path)
        new.delete()
        p.relative()
        tuple(p.collect(lambda _: _.endswith('.py')))
        new.mkdir()
        new.into('some').mkdir().into("somefile").open('w').close()
        new.delete()
        assert new == str(new)
        root, *_ = new
        print(f'0-th elem of arr{new._path}: ', new[0])
        print(f'the elem where endswith .py of arr{new._path}', new[lambda _: _.endswith('.py')])