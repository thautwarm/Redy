from Redy.Opt import *
import unittest
import pytest
from dis import dis


class DeadLoop(Exception):
    pass


@feature(goto)
def very_big_loop(x):
    task1: label
    task2: label
    end: label
    last = None
    with task1:
        if last is '1':
            raise DeadLoop
        last = '1'

        if x == 'end':
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            print('jump end')
            end.jump()
        elif x == '1':
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            print('jump task1')
            task1.jump()
        elif x == '2':
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            print('jump task2')
            last = '2'
            task2.jump()

        raise ValueError

    task2.mark()
    if last is '2':
        raise DeadLoop
    last = '2'
    print('task2| then turn to task1.')
    task1.jump()

    end.mark()
    if last is 'end':
        raise DeadLoop
    last = 'end'
    print('good bye')


class TestGoto(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def test_loop(self):
        dis(very_big_loop)

        def transaction(fn):
            try:
                fn()
            except Exception as e:
                raise e

        with self.assertRaises(DeadLoop):
            very_big_loop('1')

        with self.assertRaises(DeadLoop):
            very_big_loop('2')

        very_big_loop('end')


if __name__ == '__main__':
    unittest.main()
