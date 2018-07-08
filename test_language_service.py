from Redy.Opt.builtin_features import const, feature, show_ast, constexpr

a = 2


@feature(*const)
def f(x):
    g: const = a + 1
    return g


print(f(1))


@feature(const, constexpr)
def f(x):
    y = constexpr[1 + a]
    print(x + y)


f(1)
