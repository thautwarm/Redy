from Redy.Opt import constexpr, const, feature
import dis
import unittest


class TestConstExpr(unittest.TestCase):

    def test_constexpr(self):
        a = 1

        @feature(const, constexpr)
        def my_func(x):
            z: const = 20
            print(z)
            if constexpr[1 == a]:
                return x
            else:
                return x + d

        self.assertEqual(my_func(1), 1)
        print(dis.dis(my_func))
        self.assertTrue('d' not in my_func.__code__.co_names)
        self.assertTrue(len(my_func.__code__.co_varnames) == 1)
        self.assertTrue(len(my_func.__code__.co_consts) == 2)


if __name__ == '__main__':
    unittest.main()
