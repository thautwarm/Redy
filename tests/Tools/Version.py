from Redy.Typing import *

import unittest
import pytest
class Test_Redy_Tools_Version(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def test_2170699620744(self):
        from Redy.Tools.Version import Version
        a = Version('1.0.0.2')
        a.increment(version_number_idx=2, increment=1)
        assert a == ('1.0.1.0')
        print(a[0])
        a[0] = 2
        from Redy.Tools.Version import Version
        a = Version()
        b = Version('1.0.0')
        b.copy_to(a)
        assert a == '1.0.0'
        from Redy.Tools.Version import Version
        a = Version()
        b = Version('1.0.0')
        a.copy(b)
        assert a == '1.0.0'
        from Redy.Tools.Version import Version
        a = Version("1.0")
        assert a == '1.0'
        from Redy.Tools.Version import Version
        a = Version('1.0')
        assert a >= '0.8'
        from Redy.Tools.Version import Version
        a = Version('1.0')
        assert a <= '1.1'
        from Redy.Tools.Version import Version
        a = Version('1.0')
        assert a > '0.8'
        from Redy.Tools.Version import Version
        a = Version('1.0')
        assert a < '1.1'
        from Redy.Tools.Version import Version
        a = Version('1.0.0')
        a += '0.0.1'
        assert a == '1.0.1'
        from Redy.Tools.Version import Version
        a = Version('1.1.0')
        assert a - '0.1' == '1.0.0'
        assert a - Version('0.1') == '1.0.0'
        from Redy.Tools.Version import Version
        a = Version('1.1.1')
        a -= '0.0.1'
        assert a == '1.1.0'