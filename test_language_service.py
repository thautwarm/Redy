from Redy.Opt import const, feature, const_link, constexpr, goto, label
from dis import dis


def show(f):
    dis(f)
    print('==================================')


a = 1


@show
@feature(const, constexpr)
def f(x):
    g: const = a + 1
    u: const = g + 2
    return constexpr[g + u]


@show
@feature(const, constexpr)
def f(x):
    y = constexpr[1 + a]
    print(x + y)


def f(x):
    @feature(const, constexpr)
    def g(y):
        if z:
            x: const = 1
            return x + y

    return g


show(f(1))


@show
@feature(goto)
def f(x):
    s : label

    s.jump()
    print(1)


    s.mark()
    print(x)