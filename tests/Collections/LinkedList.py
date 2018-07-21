from Redy.Typing import *

import unittest
import pytest
class Test_Redy_Collections_LinkedList(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def test_2427484080472(self):
        from Redy.Collections.LinkedList import LinkedList
        x = LinkedList(1)
        x.next = [1, 2, 3]
        print(x.next)
        def inf_stream():
           i = 0
           while True:
               yield i
               i += 1
        x.next = inf_stream()
        for i in zip(range(10), x):
           print(i)
        x.next = None
        x.__repr__()
        try:
           x.next = 1
        except TypeError:
           print('expected error')
        except Exception as e:
           raise e
        z = LinkedList(2)
        z.next = x
        print(z)
        a1 = LinkedList(1)
        a2 = a1.cons(2)
        a3 = a2.cons(3)

        from Redy.Collections.LinkedList import zero_list, ZeroList
        print(zero_list)
        if not zero_list:
            print('test as false')
        try:
            zero_list.next
        except StopIteration:
            print('expected exception')
        except Exception as e:
            raise e
        try:
            zero_list.any = 1
        except AttributeError:
            print('expected error')
        except Exception as e:
            raise e
        zero_list_ = ZeroList()
        assert zero_list is zero_list_
        assert isinstance(zero_list, ZeroList)

        from Redy.Collections.LinkedList import zero_list, ZeroList
        print(zero_list)
        if not zero_list:
            print('test as false')
        try:
            zero_list.next
        except StopIteration:
            print('expected exception')
        except Exception as e:
            raise e
        try:
            zero_list.any = 1
        except AttributeError:
            print('expected error')
        except Exception as e:
            raise e
        zero_list_ = ZeroList()
        assert zero_list is zero_list_
        assert isinstance(zero_list, ZeroList)